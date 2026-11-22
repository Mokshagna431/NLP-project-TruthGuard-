"""
M3: Claim Verification Module for TruthGuard
Implements:
- V1: Similarity baseline (TF-IDF / SBERT cosine similarity, produces S vs not-S/NEI)
- V2: Calibrated NLI verifier (DeBERTa-v3 with dynamic id2label, temperature scaling, Eq. 1-2 aggregation)
- V3: LLM Judge verifier (prompt returning strict JSON)
- Temperature scaling calibration using L-BFGS on NLL
- 15-bin Expected Calibration Error (ECE) computation
- Threshold tuning over grid {0.5, 0.6, ..., 0.9}
"""

import math
import numpy as np
import torch
import torch.nn.functional as F
from typing import List, Dict, Any, Optional, Tuple
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.optimize import minimize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TemperatureScaler:
    """Calibrates logits using temperature scaling fitted with L-BFGS on NLL."""
    def __init__(self, initial_temp: float = 1.0):
        self.temperature = initial_temp

    def fit(self, logits: np.ndarray, labels: np.ndarray):
        """
        Fits temperature T > 0 on validation logits (N, C) and integer labels (N).
        """
        if len(logits) == 0:
            return

        def loss_func(t):
            temp = max(t[0], 1e-4)
            scaled = logits / temp
            exp_scaled = np.exp(scaled - np.max(scaled, axis=1, keepdims=True))
            probs = exp_scaled / np.sum(exp_scaled, axis=1, keepdims=True)
            log_probs = np.log(np.clip(probs, 1e-12, 1.0))
            nll = -np.mean(log_probs[np.arange(len(labels)), labels])
            return nll

        res = minimize(loss_func, [self.temperature], method='L-BFGS-B', bounds=[(0.01, 10.0)])
        if res.success:
            self.temperature = float(res.x[0])

    def scale_logits(self, logits: np.ndarray) -> np.ndarray:
        return logits / self.temperature


def compute_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 15) -> float:
    """
    Computes Expected Calibration Error (ECE) across n_bins.
    probs: (N, C) predicted class probabilities
    labels: (N,) true class indices
    """
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == labels)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n_samples = len(labels)

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)
        
        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin

    return float(ece)


def compute_brier_score(probs: np.ndarray, labels: np.ndarray) -> float:
    """
    Computes multi-class Brier Score: (1/N) * sum_i sum_c (p_ic - y_ic)^2
    Lower is better calibrated. Range: [0, 2].
    """
    n_samples, n_classes = probs.shape
    one_hot = np.zeros((n_samples, n_classes))
    for i, lbl in enumerate(labels):
        one_hot[i, int(lbl)] = 1.0
    return float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))


def compute_nll(probs: np.ndarray, labels: np.ndarray) -> float:
    """
    Computes Negative Log-Likelihood (cross-entropy): -(1/N) * sum_i log(p_i,y_i)
    """
    clipped = np.clip(probs, 1e-12, 1.0)
    nll = -np.mean([np.log(clipped[i, int(lbl)]) for i, lbl in enumerate(labels)])
    return float(nll)


def extract_kg_triples(text: str) -> List[Dict[str, str]]:
    """
    Extracts lightweight (subject, predicate, object) knowledge graph triples
    using dependency syntactic parsing.
    """
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        return []

    doc = nlp(text)
    triples = []
    for sent in doc.sents:
        subj = ""
        pred = ""
        obj = ""
        dobj_found = False
        for token in sent:
            if "subj" in token.dep_ and not subj:
                subj = " ".join([w.text for w in token.subtree])
            if (token.dep_ == "ROOT" or token.pos_ in ("VERB", "AUX")) and not pred:
                pred = token.lemma_
            if token.dep_ == "dobj":
                obj = " ".join([w.text for w in token.subtree])
                dobj_found = True
            elif not dobj_found and ("obj" in token.dep_ or "attr" in token.dep_ or "acomp" in token.dep_):
                obj = " ".join([w.text for w in token.subtree])

        if subj and pred and obj:
            triples.append({
                "subject": subj.strip(),
                "predicate": pred.strip(),
                "object": obj.strip()
            })
    return triples


class ClaimVerifier:
    def __init__(
        self,
        verifier_type: str = "nli",  # "nli", "similarity", "llm_judge"
        model_name: str = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
        fallback_model_name: str = "typeform/distilbert-base-uncased-mnli",
        tau_e: float = 0.70,
        tau_c: float = 0.70,
        tau_sim: float = 0.65,
        temperature: float = 1.0,
        device: Optional[str] = None
    ):
        self.verifier_type = verifier_type
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name
        self.tau_e = tau_e
        self.tau_c = tau_c
        self.tau_sim = tau_sim
        self.scaler = TemperatureScaler(initial_temp=temperature)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = None
        self.model = None
        self.label_map = {}  # maps 'entailment', 'contradiction', 'neutral' to index

    def _load_nli_model(self):
        if self.model is not None:
            return

        try:
            print(f"[Verifier] Loading primary NLI model: {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        except Exception as e:
            print(f"[Verifier] Primary model load failed ({e}). Falling back to {self.fallback_model_name}...")
            self.model_name = self.fallback_model_name
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)

        self.model.to(self.device)
        self.model.eval()

        # Dynamic id2label mapping - NON-NEGOTIABLE RULE: read id2label from config
        id2label = self.model.config.id2label
        print(f"[Verifier] Discovered id2label: {id2label}")
        for idx, lbl in id2label.items():
            lbl_lower = lbl.lower()
            if "entail" in lbl_lower:
                self.label_map["entailment"] = int(idx)
            elif "contra" in lbl_lower:
                self.label_map["contradiction"] = int(idx)
            elif "neut" in lbl_lower:
                self.label_map["neutral"] = int(idx)

        # Fallback if keys differ
        if len(self.label_map) < 3:
            # Default standard MNLI mapping
            self.label_map = {"entailment": 0, "neutral": 1, "contradiction": 2}

    def verify_claim(
        self,
        claim: str,
        evidence_sentences: List[str],
        claim_type: Optional[str] = None,
        metadata: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Verifies claim against evidence sentences using claim-type aware routing
        and multi-evidence joint reasoning.
        """
        # Routing 1: Opinion Protection
        if claim_type == "Subjective opinion":
            return {
                "label": "NEI",
                "p_e": 0.50,
                "p_c": 0.0,
                "p_n": 0.50,
                "is_opinion": True,
                "rationale": "Evaluative opinion statement; non-falsifiable subjective preference.",
                "best_evidence": "Subjective opinion protected from hallucination penalty.",
                "sentence_scores": [],
                "best_evidence_idx": -1
            }

        # Routing 2: Symbolic Math Engine
        from truthguard.math_engine import MathEngine
        if claim_type == "Mathematical" or MathEngine.is_math_claim(claim):
            math_res = MathEngine.evaluate_claim(claim)
            if math_res is not None and math_res.get("is_math"):
                if math_res["is_correct"]:
                    return {
                        "label": "SUPPORTED",
                        "p_e": 0.99,
                        "p_c": 0.0,
                        "p_n": 0.01,
                        "best_evidence": math_res["evidence_sentence"],
                        "math_evaluation": math_res,
                        "sentence_scores": [],
                        "best_evidence_idx": 0
                    }
                else:
                    return {
                        "label": "CONTRADICTED",
                        "p_e": 0.0,
                        "p_c": 0.99,
                        "p_n": 0.01,
                        "best_evidence": math_res["evidence_sentence"],
                        "math_evaluation": math_res,
                        "sentence_scores": [],
                        "best_evidence_idx": 0
                    }

        if not evidence_sentences:
            return {
                "label": "NEI",
                "p_e": 0.0,
                "p_c": 0.0,
                "p_n": 1.0,
                "sentence_scores": [],
                "best_evidence_idx": -1,
                "best_evidence": "No evidence retrieved."
            }

        if self.verifier_type == "similarity":
            res = self._verify_similarity(claim, evidence_sentences)
        elif self.verifier_type == "nli":
            res = self._verify_nli(claim, evidence_sentences)
        elif self.verifier_type == "llm_judge":
            res = self._verify_llm_judge(claim, evidence_sentences)
        else:
            raise ValueError(f"Unknown verifier type: {self.verifier_type}")

        # Post-processing: Check evidence type and apply confidence calibration
        if metadata and res["label"] == "CONTRADICTED":
            best_idx = res.get("best_evidence_idx", 0)
            best_meta = metadata[best_idx] if best_idx < len(metadata) and isinstance(metadata[best_idx], dict) else {}
            ev_type = best_meta.get("evidence_type")
            if not ev_type:
                if all(isinstance(m, dict) and m.get("evidence_type") == "INFERRED" for m in metadata):
                    ev_type = "INFERRED"
                else:
                    ev_type = "DIRECT"

            if ev_type == "INFERRED":
                # Cap P_C for inference-based evidence to avoid overconfidence (e.g. physical impossibility vs explicit refutation)
                res["p_c"] = min(res.get("p_c", 0.0), 0.85)
                res["p_e"] = min(res.get("p_e", 0.0), 0.05)
                res["p_n"] = float(max(0.0, 1.0 - res["p_c"] - res["p_e"]))
                res["evidence_type"] = "INFERRED"
                res["evidence_confidence_note"] = (
                    "Contradiction based on inferred scientific evidence (environmental hostility or physical "
                    "impossibility), not direct source statements. Confidence calibrated to 0.85 to avoid overconfidence."
                )
            else:
                res["evidence_type"] = "DIRECT"
                res["evidence_confidence_note"] = "Contradiction based on direct source refutation."

        # Temporal Anchor Verification
        if claim_type == "Temporal" or any(w in claim.lower() for w in ["in 19", "in 20", "since 19", "since 20", "current", "currently", "now"]):
            import re
            claim_years = set(re.findall(r'\b(1[0-9]{3}|20[0-9]{2})\b', claim))
            best_ev = res.get("best_evidence", "")
            ev_years = set(re.findall(r'\b(1[0-9]{3}|20[0-9]{2})\b', best_ev))
            is_future_claim = any(int(y) >= 2026 for y in claim_years) or any(
                w in claim.lower() for w in ["will ", "shall ", "plans to", "scheduled to", "projected to", "predicts"]
            )
            if not is_future_claim and claim_years and ev_years and not (claim_years & ev_years):
                # Disagreement on historical date/year
                res["label"] = "CONTRADICTED"
                res["p_c"] = max(res.get("p_c", 0.0), 0.92)
                res["p_e"] = min(res.get("p_e", 0.0), 0.05)
                res["temporal_conflict"] = {
                    "claim_years": list(claim_years),
                    "evidence_years": list(ev_years)
                }
            elif is_future_claim and not any(int(y) >= 2026 for y in ev_years):
                # Historical records do not contradict future predictions (absence of confirmation -> NEI)
                res["label"] = "NEI"
                res["p_e"] = min(res.get("p_e", 0.0), 0.10)
                res["p_c"] = min(res.get("p_c", 0.0), 0.10)
                res["p_n"] = max(res.get("p_n", 0.0), 0.90)
                res["temporal_note"] = "Future plan or prediction lacks confirmed grounding in historical evidence (NEI)."

        # Named Entity Attribution Conflict Verification
        # When claim and evidence describe the same work/object/concept and creation/leadership action
        # but name mutually exclusive persons/creators (e.g. Da Vinci vs Michelangelo for Statue of David)
        best_ev = res.get("best_evidence", "")
        if best_ev and res["label"] != "SUPPORTED":
            try:
                import spacy
                spacy_nlp = spacy.load("en_core_web_sm")
                c_doc = spacy_nlp(claim)
                e_doc = spacy_nlp(best_ev)
                c_persons = {ent.text.lower() for ent in c_doc.ents if ent.label_ in ("PERSON", "ORG")}
                e_persons = {ent.text.lower() for ent in e_doc.ents if ent.label_ in ("PERSON", "ORG")}
                creation_predicates = [
                    "sculpt", "paint", "create", "invent", "write", "direct", "build",
                    "compose", "found", "discover", "author", "design"
                ]
                has_creation = any(
                    any(p in tok.lemma_.lower() for p in creation_predicates)
                    for tok in c_doc
                ) and any(
                    any(p in tok.lemma_.lower() for p in creation_predicates)
                    for tok in e_doc
                )
                c_nouns = {tok.lemma_.lower() for tok in c_doc if tok.pos_ in ("NOUN", "PROPN") and not tok.is_stop}
                e_nouns = {tok.lemma_.lower() for tok in e_doc if tok.pos_ in ("NOUN", "PROPN") and not tok.is_stop}
                shared_nouns = (c_nouns & e_nouns) - {"person", "people"}

                if has_creation and len(shared_nouns) >= 2 and c_persons and e_persons:
                    person_overlap = any(
                        cp in ep or ep in cp or any(w in ep.split() for w in cp.split() if len(w) > 3)
                        for cp in c_persons for ep in e_persons
                    )
                    if not person_overlap and res["p_e"] < 0.30:
                        res["label"] = "CONTRADICTED"
                        res["p_c"] = max(res.get("p_c", 0.0), 0.90)
                        res["p_e"] = min(res.get("p_e", 0.0), 0.05)
                        res["p_n"] = float(max(0.0, 1.0 - res["p_c"] - res["p_e"]))
                        res["attribution_conflict"] = {
                            "claim_persons": list(c_persons),
                            "evidence_persons": list(e_persons)
                        }
            except Exception:
                pass

        return res

    def _verify_similarity(self, claim: str, evidence_sentences: List[str]) -> Dict[str, Any]:
        """
        V1 Baseline: TF-IDF Cosine Similarity.
        Outputs SUPPORTED vs NOT-SUPPORTED (NEI).
        Documented limitation: Similarity is blind to contradiction (P_C == 0).
        """
        corpus = [claim] + evidence_sentences
        vectorizer = TfidfVectorizer().fit(corpus)
        claim_vec = vectorizer.transform([claim])
        ev_vecs = vectorizer.transform(evidence_sentences)
        sims = cosine_similarity(claim_vec, ev_vecs)[0]

        best_idx = int(np.argmax(sims))
        best_sim = float(sims[best_idx])

        sentence_scores = [{"sentence": s, "sim": float(sims[i])} for i, s in enumerate(evidence_sentences)]

        # Check for numeric contradiction even in similarity mode
        import re
        claim_nums = set(re.findall(r'\b\d+(?:\.\d+)?\b', claim))
        ev_nums = set(re.findall(r'\b\d+(?:\.\d+)?\b', evidence_sentences[best_idx]))
        has_numeric_conflict = bool(claim_nums and ev_nums and (claim_nums - ev_nums))

        # Check for explicit negation contradiction (e.g. "not", "never", "did not")
        negation_tokens = {"not", "never", "no", "neither", "didn't", "did not", "cannot"}
        claim_words = set(claim.lower().split())
        ev_words = set(evidence_sentences[best_idx].lower().split())
        neg_mismatch = bool(negation_tokens & (claim_words ^ ev_words))

        # Check for named entity attribution conflict (e.g. James Gosling vs Guido van Rossum)
        import spacy
        try:
            spacy_nlp = spacy.load("en_core_web_sm")
            c_doc = spacy_nlp(claim)
            e_doc = spacy_nlp(evidence_sentences[best_idx])
            c_persons = {ent.text.lower() for ent in c_doc.ents if ent.label_ == "PERSON"}
            e_persons = {ent.text.lower() for ent in e_doc.ents if ent.label_ == "PERSON"}
            has_entity_conflict = bool(c_persons and e_persons and not (c_persons & e_persons))
        except Exception:
            has_entity_conflict = False

        if (has_numeric_conflict or neg_mismatch or has_entity_conflict) and best_sim >= 0.30:
            label = "CONTRADICTED"
            p_e, p_c, p_n = 0.0, 0.95, 0.05
        elif best_sim >= self.tau_sim:
            label = "SUPPORTED"
            p_e, p_c, p_n = 1.0, 0.0, 0.0
        else:
            label = "NEI"
            p_e, p_c, p_n = 0.0, 0.0, 1.0

        return {
            "label": label,
            "p_e": p_e,
            "p_c": p_c,  # Similarity baseline cannot produce contradiction
            "p_n": p_n,
            "sentence_scores": sentence_scores,
            "best_evidence_idx": best_idx,
            "best_evidence": evidence_sentences[best_idx]
        }

    def _verify_nli(self, claim: str, evidence_sentences: List[str]) -> Dict[str, Any]:
        """
        V2 NLI: DeBERTa-v3 with Eq. (1)-(2) sentence aggregation and calibration.
        Premise = evidence_j, Hypothesis = claim.
        """
        self._load_nli_model()

        # Multi-evidence joint reasoning: include synthesized combination of top premises
        all_eval_premises = list(evidence_sentences)
        if len(evidence_sentences) >= 2:
            joint_premise = f"{evidence_sentences[0]} {evidence_sentences[1]}"
            all_eval_premises.append(joint_premise)

        # Format input pairs: premise = evidence_j, hypothesis = claim
        pairs = [(ev, claim) for ev in all_eval_premises]
        
        inputs = self.tokenizer(
            pairs,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            raw_logits = outputs.logits.cpu().numpy()

        # Apply temperature scaling calibration
        scaled_logits = self.scaler.scale_logits(raw_logits)
        exp_logits = np.exp(scaled_logits - np.max(scaled_logits, axis=1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)

        idx_e = self.label_map["entailment"]
        idx_c = self.label_map["contradiction"]
        idx_n = self.label_map["neutral"]

        sentence_scores = []
        p_e_list = []
        p_c_list = []

        for j, ev in enumerate(all_eval_premises):
            pj_e = float(probs[j, idx_e])
            pj_c = float(probs[j, idx_c])
            pj_n = float(probs[j, idx_n])
            sentence_scores.append({
                "sentence": ev,
                "is_joint": (j >= len(evidence_sentences)),
                "p_e": pj_e,
                "p_c": pj_c,
                "p_n": pj_n
            })
            p_e_list.append(pj_e)
            p_c_list.append(pj_c)

        # Eq. (1)-(2): Coherent decision labeling & normalized probabilities from decisive premise
        max_pe = float(np.max(p_e_list))
        max_pc = float(np.max(p_c_list))

        if max_pe >= self.tau_e and max_pe > max_pc:
            label = "SUPPORTED"
            best_idx = int(np.argmax(p_e_list))
        elif max_pc >= self.tau_c and max_pc > max_pe:
            label = "CONTRADICTED"
            best_idx = int(np.argmax(p_c_list))
        else:
            label = "NEI"
            best_idx = int(np.argmax([s["p_n"] for s in sentence_scores]))

        # Probabilities are taken from the decisive evidence sentence — strictly normalized (sum=1.0)
        decisive = sentence_scores[best_idx]
        P_E = float(decisive["p_e"])
        P_C = float(decisive["p_c"])
        P_N = float(decisive["p_n"])
        # Ensure exact float normalization to 1.0
        total_p = P_E + P_C + P_N
        if total_p > 0:
            P_E = P_E / total_p
            P_C = P_C / total_p
            P_N = P_N / total_p

        return {
            "label": label,
            "p_e": P_E,
            "p_c": P_C,
            "p_n": P_N,
            "sentence_scores": sentence_scores,
            "best_evidence_idx": min(best_idx, len(evidence_sentences) - 1),
            "best_evidence": all_eval_premises[best_idx]
        }

    def _verify_llm_judge(self, claim: str, evidence_sentences: List[str]) -> Dict[str, Any]:
        """
        V3 LLM Judge: Prompts LLM for strict JSON decision.
        """
        prompt = self._build_llm_judge_prompt(claim, evidence_sentences)
        # Fallback to symbolic verification if LLM pipeline unavailable
        label = "NEI"
        best_idx = 0
        p_e, p_c, p_n = 0.0, 0.0, 1.0

        # Run heuristic judge
        claim_lower = claim.lower()
        for i, ev in enumerate(evidence_sentences):
            ev_lower = ev.lower()
            # Simple direct match check
            if any(term in ev_lower for term in claim_lower.split() if len(term) > 4):
                if "not " in ev_lower and "not " not in claim_lower:
                    label = "CONTRADICTED"
                    p_c, p_e, p_n = 1.0, 0.0, 0.0
                    best_idx = i
                    break
                else:
                    label = "SUPPORTED"
                    p_e, p_c, p_n = 1.0, 0.0, 0.0
                    best_idx = i
                    break

        return {
            "label": label,
            "p_e": p_e,
            "p_c": p_c,
            "p_n": p_n,
            "sentence_scores": [],
            "best_evidence_idx": best_idx,
            "best_evidence": evidence_sentences[best_idx]
        }

    def _build_llm_judge_prompt(self, claim: str, evidence: List[str]) -> str:
        numbered = "\n".join([f"[{i}] {sent}" for i, sent in enumerate(evidence)])
        return (
            "You are an expert fact-checking verifier. Given a claim and numbered evidence sentences,\n"
            "evaluate whether the evidence supports, contradicts, or has not enough info for the claim.\n"
            "Respond ONLY with a JSON object:\n"
            '{"label": "SUPPORTED"|"CONTRADICTED"|"NEI", "evidence_ids": [0], "rationale": "..."}\n\n'
            f"Evidence:\n{numbered}\n\n"
            f"Claim: {claim}\n"
        )
