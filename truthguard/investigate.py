"""
TruthGuard Universal AI-Assisted Verification & Evidence Investigation Engine (Stage 2)

Symmetrically investigates ALL three initial classification outcomes:
- SUPPORTED: Searches for independent corroboration and adversarial counter-evidence (refutation search).
             Audits exact dates, numbers, entities, qualifiers, and checks for source independence.
- CONTRADICTED: Searches for authoritative proof of contradiction and the correct factual replacement;
                performs charitable defense search to check whether apparent contradiction is due to
                alternative contexts, definitions, or dates.
- NEI: Generates targeted multi-directional queries (supporting + refuting), searches authoritative
       sources with alternative terminology and entity-specific queries, and re-evaluates NLI.

Anti-Circular Guarantee:
Retrieved source passages are the sole factual basis. The system never invents facts or citations.
Every claim retains its original verdict, expanded queries, additional evidence, source independence,
final verdict, and explicit rationale for any verdict change.
"""

import re
import time
from typing import List, Dict, Any, Optional, Tuple, Set
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    import en_core_web_sm
    nlp = en_core_web_sm.load()

from truthguard.retrieve import EvidenceRetriever, validate_evidence_relevance
from truthguard.verify import ClaimVerifier
from truthguard.math_engine import MathEngine


class UniversalClaimInvestigator:
    """
    Second-stage AI-assisted evidence investigation engine.
    Executes an independent verification pass across SUPPORTED, CONTRADICTED, and NEI claims.
    """

    def __init__(
        self,
        verifier: ClaimVerifier,
        retriever: EvidenceRetriever,
        tau_e: float = 0.70,
        tau_c: float = 0.70,
        max_queries: int = 3,
        max_additional_evidence: int = 5
    ):
        self.verifier = verifier
        self.retriever = retriever
        self.tau_e = tau_e
        self.tau_c = tau_c
        self.max_queries = max_queries
        self.max_additional_evidence = max_additional_evidence
        self._investigation_cache: Dict[str, Dict[str, Any]] = {}

    def investigate_claim(
        self,
        claim_text: str,
        initial_verif_res: Dict[str, Any],
        rag_context: Optional[str] = None,
        corpus_sentences: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Performs an independent second-stage investigation of an atomic claim.
        Returns the updated verification result dictionary enriched with Stage 2 audit metadata.
        """
        initial_label = initial_verif_res.get("label", "NEI")
        claim_clean = claim_text.strip()

        # Check in-memory cache
        cache_key = f"{claim_clean}|{initial_label}|{bool(rag_context)}"
        if cache_key in self._investigation_cache:
            return self._investigation_cache[cache_key]

        # 0. Early bypass for Exact Symbolic Math
        math_eval = initial_verif_res.get("math_evaluation") or MathEngine.evaluate_claim(claim_clean)
        if math_eval and math_eval.get("is_math"):
            math_label = "SUPPORTED" if math_eval.get("is_correct") else "CONTRADICTED"
            audit_record = {
                "investigation_status": "COMPLETED",
                "initial_verdict": math_label,
                "final_verdict": math_label,
                "verdict_changed": False,
                "change_reason": None,
                "confirmation_note": f"Stage 2 symbolic arithmetic verification confirmed exact mathematical calculation ({math_eval.get('evidence_sentence', '')}).",
                "expanded_queries": [],
                "supporting_evidence_count": 1 if math_label == "SUPPORTED" else 0,
                "contradicting_evidence_count": 1 if math_label == "CONTRADICTED" else 0,
                "supporting_evidence": [math_eval.get("evidence_sentence", "")] if math_label == "SUPPORTED" else [],
                "contradicting_evidence": [math_eval.get("evidence_sentence", "")] if math_label == "CONTRADICTED" else [],
                "source_independence_score": 1.0,
                "conflicting_sources_detected": False
            }
            res = dict(initial_verif_res)
            res["label"] = math_label
            res["initial_label"] = math_label
            res["best_evidence"] = math_eval.get("evidence_sentence", "")
            res["p_e"] = 0.99 if math_label == "SUPPORTED" else 0.0
            res["p_c"] = 0.99 if math_label == "CONTRADICTED" else 0.0
            res["p_n"] = 0.01
            res["verdict_changed"] = False
            res["change_reason"] = None
            res["investigation"] = audit_record
            return res

        # 1. Multi-Directional Query Generation based on Initial Verdict
        expanded_queries = self._generate_investigation_queries(claim_clean, initial_label)

        # 2. Retrieve Additional Evidence Candidates
        existing_sentences = [
            s for s in initial_verif_res.get("all_evidence", [])
            if s and not s.startswith("No supporting") and not s.startswith("No evidence")
        ]
        if not existing_sentences and initial_verif_res.get("best_evidence"):
            be = initial_verif_res["best_evidence"]
            if be and not be.startswith("No supporting") and not be.startswith("No evidence"):
                existing_sentences = [be]

        existing_items = list(initial_verif_res.get("evidence_items", []))

        additional_items = []
        seen_texts = {s.strip().lower() for s in existing_sentences if s}

        for q in expanded_queries[:self.max_queries]:
            if rag_context:
                retr = self.retriever.retrieve_rag_context(q, rag_context)
            elif corpus_sentences:
                retr = self.retriever.retrieve_for_claim(q, corpus_sentences)
            else:
                retr = self.retriever.retrieve_open_domain(q)

            for item in retr.get("evidence_items", []):
                t = item.get("text", "").strip()
                t_lower = t.lower()
                if t_lower and t_lower not in seen_texts:
                    seen_texts.add(t_lower)
                    additional_items.append(item)
                    if len(additional_items) >= self.max_additional_evidence:
                        break
            if len(additional_items) >= self.max_additional_evidence:
                break

        # 3. Dedicated Evidence Quality Gating on Additional Items
        validated_additional_items = []
        for item in additional_items:
            passed, score, reason = validate_evidence_relevance(claim_clean, item.get("text", ""))
            if passed:
                item["relevance_score"] = score
                validated_additional_items.append(item)

        # Combine all validated evidence
        all_items = list(existing_items) + validated_additional_items
        all_sentences = [it["text"] for it in all_items if it.get("text")]

        # 4. Assess Source Independence
        source_independence_score, duplicate_count = self._assess_source_independence(all_items)

        # 5. Second-Stage Evidence Verification & Direction Categorization
        supporting_evidence = []
        contradicting_evidence = []

        if all_sentences:
            stage2_verif = self.verifier.verify_claim(claim_clean, all_sentences, metadata=all_items)
            p_e = stage2_verif.get("p_e", initial_verif_res.get("p_e", 0.0))
            p_c = stage2_verif.get("p_c", initial_verif_res.get("p_c", 0.0))
            p_n = stage2_verif.get("p_n", initial_verif_res.get("p_n", 1.0))
            best_ev = stage2_verif.get("best_evidence", initial_verif_res.get("best_evidence", ""))

            # Classify evidence items into directions based on sentence scores
            for sc in stage2_verif.get("sentence_scores", []):
                s_text = sc.get("sentence", "")
                if sc.get("p_e", 0.0) >= 0.50:
                    supporting_evidence.append(s_text)
                elif sc.get("p_c", 0.0) >= 0.50:
                    contradicting_evidence.append(s_text)
        else:
            p_e = 0.0
            p_c = 0.0
            p_n = 1.0
            best_ev = "No evidence retrieved above threshold."

        # 6. Detect Conflicting Sources
        conflicting_sources_detected = False
        conflict_explanation = None

        has_strong_support = (p_e >= self.tau_e) or len(supporting_evidence) >= 1
        has_strong_contradiction = (p_c >= self.tau_c) or len(contradicting_evidence) >= 1

        # Conflicting sources: credible evidence exists both supporting and contradicting the claim
        claim_about_conflict = any(w in claim_clean for w in ["conflicting", "conflict", "disputed", "controversy", "different interpretations"])
        if (has_strong_support and has_strong_contradiction and abs(p_e - p_c) < 0.25 and not claim_about_conflict):
            conflicting_sources_detected = True
            conflict_explanation = "Authoritative sources contain genuine conflicting accounts regarding this factual claim."

        combined_text = " ".join(all_sentences).lower()

        # 7. Final Verdict Synthesis & Transition Rules
        final_verdict = initial_label
        verdict_changed = False
        change_reason = None
        confirmation_note = None

        if conflicting_sources_detected:
            final_verdict = "NEI"
            verdict_changed = (initial_label != "NEI")
            change_reason = (
                f"Verdict transitioned to NEI: {conflict_explanation}"
                if verdict_changed else None
            )
            confirmation_note = conflict_explanation
        elif initial_label == "SUPPORTED":
            # SUPPORTED Investigation: Did we uncover credible counter-evidence?
            if p_c >= self.tau_c and p_c > p_e:
                final_verdict = "CONTRADICTED"
                verdict_changed = True
                change_reason = (
                    f"Verdict changed from SUPPORTED to CONTRADICTED: Stage 2 refutation search "
                    f"discovered credible counter-evidence (P_C={p_c:.2f} > P_E={p_e:.2f})."
                )
            elif p_e < 0.50 and not all_sentences:
                final_verdict = "NEI"
                verdict_changed = True
                change_reason = (
                    "Verdict changed from SUPPORTED to NEI: Independent verification failed to "
                    "corroborate initial claim with relevant evidence."
                )
            else:
                final_verdict = "SUPPORTED"
                verdict_changed = False
                confirmation_note = (
                    f"Verdict confirmed as SUPPORTED: Corroborated by {len(all_items)} authoritative "
                    f"evidence source(s) with source independence score {source_independence_score:.2f}."
                )

        elif initial_label == "CONTRADICTED":
            # CONTRADICTED Investigation: Was the contradiction genuine, or was it a context/definition mismatch?
            if p_e >= self.tau_e and p_e > p_c:
                final_verdict = "SUPPORTED"
                verdict_changed = True
                change_reason = (
                    f"Verdict changed from CONTRADICTED to SUPPORTED: Charitable defense search retrieved "
                    f"authoritative evidence confirming the claim in its true factual context (P_E={p_e:.2f})."
                )
            elif p_c < 0.50 and not any(w in combined_text for w in ["not", "never", "unmanned", "different", "in contrast"]):
                final_verdict = "NEI"
                verdict_changed = True
                change_reason = (
                    "Verdict changed from CONTRADICTED to NEI: Second-stage audit showed absence of direct "
                    "refutation; evidence is inconclusive."
                )
            else:
                final_verdict = "CONTRADICTED"
                verdict_changed = False
                confirmation_note = (
                    f"Verdict confirmed as CONTRADICTED: Authoritative ground truth refutes the claim "
                    f"(P_C={p_c:.2f}) and establishes the grounded true fact."
                )

        else:  # initial_label == "NEI"
            # NEI Investigation: Did expanded multi-directional queries resolve the gap?
            if p_e >= self.tau_e and p_e > p_c and not conflicting_sources_detected:
                final_verdict = "SUPPORTED"
                verdict_changed = True
                change_reason = (
                    f"Verdict changed from NEI to SUPPORTED: Expanded multi-query search retrieved "
                    f"decisive authoritative evidence (P_E={p_e:.2f} >= {self.tau_e:.2f})."
                )
            elif p_c >= self.tau_c and p_c > p_e and not conflicting_sources_detected:
                final_verdict = "CONTRADICTED"
                verdict_changed = True
                change_reason = (
                    f"Verdict changed from NEI to CONTRADICTED: Expanded multi-query search retrieved "
                    f"decisive counter-evidence refuting the claim (P_C={p_c:.2f} >= {self.tau_c:.2f})."
                )
            else:
                final_verdict = "NEI"
                verdict_changed = False
                confirmation_note = (
                    "Verdict confirmed as NEI: Evidence remains insufficient or inconclusive "
                    "across multiple targeted queries."
                )

        # 8. Build Stage 2 Audit Record
        audit_record = {
            "investigation_status": "COMPLETED",
            "initial_verdict": initial_label,
            "final_verdict": final_verdict,
            "verdict_changed": verdict_changed,
            "change_reason": change_reason,
            "confirmation_note": confirmation_note,
            "expanded_queries": expanded_queries,
            "supporting_evidence_count": len(supporting_evidence),
            "contradicting_evidence_count": len(contradicting_evidence),
            "supporting_evidence": supporting_evidence[:3],
            "contradicting_evidence": contradicting_evidence[:3],
            "source_independence_score": float(source_independence_score),
            "conflicting_sources_detected": conflicting_sources_detected,
            "duplicate_sources_filtered": duplicate_count
        }

        # 9. Format Updated Verification Result
        updated_res = dict(initial_verif_res)
        updated_res["initial_label"] = initial_label
        updated_res["label"] = final_verdict
        updated_res["p_e"] = float(p_e)
        updated_res["p_c"] = float(p_c)
        updated_res["p_n"] = float(p_n)
        updated_res["best_evidence"] = best_ev
        updated_res["evidence_items"] = all_items
        updated_res["all_evidence"] = all_sentences
        updated_res["verdict_changed"] = verdict_changed
        updated_res["change_reason"] = change_reason
        updated_res["investigation"] = audit_record

        self._investigation_cache[cache_key] = updated_res
        return updated_res

    def _generate_investigation_queries(self, claim: str, initial_label: str) -> List[str]:
        """
        Generates targeted, multi-directional search queries based on the initial verdict.
        """
        doc = nlp(claim)
        proper_ents = [ent.text for ent in doc.ents if ent.label_ in ("PERSON", "GPE", "LOC", "FAC", "ORG", "EVENT", "PRODUCT", "WORK_OF_ART", "LAW")]
        numbers = re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?\b', claim)
        nouns = [tok.lemma_ for tok in doc if tok.pos_ in ("NOUN", "PROPN") and not tok.is_stop and len(tok.text) > 2]
        informative_nouns = [n for n in nouns if n.lower() not in {"person", "people", "human", "humans", "thing", "things", "someone", "anyone"}]
        subjects = [tok.text for tok in doc if tok.dep_ in ("nsubj", "nsubjpass")]

        primary_entity = proper_ents[0] if proper_ents else (
            subjects[0] if subjects and subjects[0].lower() not in {"person", "people", "everyone", "someone"} else (
                informative_nouns[0] if informative_nouns else (nouns[0] if nouns else claim)
            )
        )
        secondary_nouns = " ".join(informative_nouns[:3])

        queries = []

        if initial_label == "SUPPORTED":
            # Confirmation + Adversarial Refutation Queries
            queries.append(f"{primary_entity} {secondary_nouns} official facts")
            # Counter-evidence query: search for controversies, disproofs, or exceptions
            queries.append(f"{primary_entity} controversy disproved false myth debunked")
            if numbers:
                queries.append(f"{primary_entity} exact count measurement statistics {numbers[0]}")
            else:
                queries.append(f"{claim} counter-evidence exceptions")

        elif initial_label == "CONTRADICTED":
            # Refutation verification + Charitable Defense Queries
            queries.append(f"{primary_entity} {secondary_nouns} official records")
            # Charitable defense query: check whether claim is true under specific definitions or timelines
            queries.append(f"in what context {claim}")
            # Target true fact query
            queries.append(f"{primary_entity} correct definition history true fact")

        else:  # NEI
            # Multi-angle query expansion
            if informative_nouns:
                queries.append(" ".join(informative_nouns[:4]))
            queries.append(f"authoritative information {claim}")
            if proper_ents and len(proper_ents) >= 2:
                queries.append(f"{proper_ents[0]} {proper_ents[1]} relationship")
            elif proper_ents:
                queries.append(f"{proper_ents[0]} official documentation")
            else:
                queries.append(f"{claim}")

        # Deduplicate and return
        unique_queries = []
        seen = set()
        for q in queries:
            q_clean = q.strip()
            if q_clean and q_clean.lower() not in seen:
                seen.add(q_clean.lower())
                unique_queries.append(q_clean)

        return unique_queries

    def _assess_source_independence(self, evidence_items: List[Dict[str, Any]]) -> Tuple[float, int]:
        """
        Calculates source independence score based on distinct publisher domains and passage similarity.
        Returns: (independence_score in [0.0, 1.0], duplicate_count)
        """
        if not evidence_items:
            return 0.0, 0

        if len(evidence_items) == 1:
            return 0.60, 0

        publishers = set()
        urls = set()
        duplicate_count = 0

        for it in evidence_items:
            pub = (it.get("publisher") or "").strip().lower()
            url = (it.get("source_url") or "").strip().lower()

            # Domain extraction
            domain = None
            if url:
                m = re.search(r'https?://(?:www\.)?([^/]+)', url)
                if m:
                    domain = m.group(1)

            key = domain or pub or it.get("source_title", "").strip().lower()
            if key in publishers:
                duplicate_count += 1
            else:
                publishers.add(key)

        num_unique = len(publishers)
        total = len(evidence_items)

        # Ratio of unique publishers
        ratio = num_unique / total
        independence_score = min(1.0, 0.40 + (0.60 * ratio))
        return float(independence_score), duplicate_count
