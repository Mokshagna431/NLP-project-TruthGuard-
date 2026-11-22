"""
TruthGuard End-to-End Orchestration Pipeline
Orchestrates:
M1: Claim decomposition
M2: Evidence retrieval
M3: Calibrated NLI verification
M4: Reliability scoring
M5: Grounded correction and span highlighting
"""

import time
from typing import List, Dict, Any, Optional
from truthguard.decompose import ClaimDecomposer
from truthguard.retrieve import EvidenceRetriever
from truthguard.verify import ClaimVerifier
from truthguard.score import ReliabilityScorer
from truthguard.correct import GroundedCorrector
from truthguard.math_engine import MathEngine
from truthguard.investigate import UniversalClaimInvestigator


class TruthGuardPipeline:
    def __init__(
        self,
        decomposition_method: str = "atomic_llm",
        retrieval_mode: str = "hybrid",
        verifier_type: str = "nli",
        nli_model_name: str = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
        tau_e: float = 0.70,
        tau_c: float = 0.70,
        tau_r: float = 0.10,
        lambda_nei: float = 0.50,
        max_correction_rounds: int = 2,
        k_s: int = 5
    ):
        print(f"[TruthGuard] Initializing pipeline (Decomp: {decomposition_method}, Retr: {retrieval_mode}, Verif: {verifier_type})...")
        self.decomposer = ClaimDecomposer(method=decomposition_method)
        self.retriever = EvidenceRetriever(
            mode=retrieval_mode,
            k_s=k_s,
            tau_r=tau_r
        )
        self.verifier = ClaimVerifier(
            verifier_type=verifier_type,
            model_name=nli_model_name,
            tau_e=tau_e,
            tau_c=tau_c
        )
        self.scorer = ReliabilityScorer(lambda_nei=lambda_nei)
        self.corrector = GroundedCorrector(
            verifier=self.verifier,
            max_rounds=max_correction_rounds
        )
        self.investigator = UniversalClaimInvestigator(
            verifier=self.verifier,
            retriever=self.retriever,
            tau_e=tau_e,
            tau_c=tau_c
        )

    def run(
        self,
        answer: str,
        rag_context: Optional[str] = None,
        corpus_sentences: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Runs the full TruthGuard pipeline on an answer string.
        """
        start_time = time.time()
        
        # M1: Decompose answer into atomic claims
        raw_claims = self.decomposer.decompose(answer)
        if not raw_claims:
            return {
                "answer": answer,
                "claims": [],
                "reliability_score": 1.0,
                "counts": {"n_S": 0, "n_C": 0, "n_NEI": 0},
                "corrected_answer": answer,
                "latency_sec": time.time() - start_time
            }

        verified_claims = []
        corrections_to_merge = []

        for c_item in raw_claims:
            claim_text = c_item["claim"]
            
            # Check 1: Symbolic Math & Arithmetic Evaluator
            math_res = MathEngine.evaluate_claim(claim_text)
            if math_res is not None and math_res.get("is_math"):
                if math_res["is_correct"]:
                    verif_res = {
                        "label": "SUPPORTED",
                        "p_e": 0.99,
                        "p_c": 0.0,
                        "p_n": 0.01,
                        "best_evidence": math_res["evidence_sentence"],
                        "math_evaluation": math_res
                    }
                    retrieval = {
                        "sentences": [math_res["evidence_sentence"]],
                        "gated_nei": False,
                        "scores": [1.0]
                    }
                else:
                    verif_res = {
                        "label": "CONTRADICTED",
                        "p_e": 0.0,
                        "p_c": 0.99,
                        "p_n": 0.01,
                        "best_evidence": math_res["evidence_sentence"],
                        "math_evaluation": math_res
                    }
                    retrieval = {
                        "sentences": [math_res["evidence_sentence"]],
                        "gated_nei": False,
                        "scores": [1.0]
                    }
            else:
                # M2: Retrieve evidence from RAG context, corpus, or open-domain knowledge base
                if rag_context:
                    retrieval = self.retriever.retrieve_rag_context(claim_text, rag_context)
                elif corpus_sentences:
                    retrieval = self.retriever.retrieve_for_claim(claim_text, corpus_sentences)
                else:
                    retrieval = self.retriever.retrieve_open_domain(claim_text)

                # Check retrieval gate (tau_r)
                if retrieval.get("gated_nei", False) or not retrieval["sentences"]:
                    verif_res = {
                        "label": "NEI",
                        "p_e": 0.0,
                        "p_c": 0.0,
                        "p_n": 1.0,
                        "best_evidence": "No supporting or contradicting evidence retrieved above threshold."
                    }
                else:
                    # M3: Verify claim against retrieved evidence
                    verif_res = self.verifier.verify_claim(
                        claim_text,
                        retrieval["sentences"],
                        metadata=retrieval.get("evidence_items")
                    )

            # Stage 2: Universal AI-Assisted Investigation across ALL three verdicts (SUPPORTED, CONTRADICTED, NEI)
            verif_res["all_evidence"] = retrieval.get("sentences", [])
            verif_res["evidence_items"] = retrieval.get("evidence_items", [])
            investigated_res = self.investigator.investigate_claim(
                claim_text=claim_text,
                initial_verif_res=verif_res,
                rag_context=rag_context,
                corpus_sentences=corpus_sentences
            )
            verif_res = investigated_res

            # M4: Claim reliability incorporating evidence metadata & authority tiers
            if verif_res.get("evidence_items"):
                best_idx = verif_res.get("best_evidence_idx", 0)
                if isinstance(best_idx, int) and 0 <= best_idx < len(verif_res["evidence_items"]):
                    verif_res["best_evidence_item"] = verif_res["evidence_items"][best_idx]
            rho = self.scorer.score_claim(verif_res)
            
            # M5: If Contradicted, run grounded correction and error span highlighting
            error_spans = []
            correction_info = None

            if verif_res["label"] == "CONTRADICTED":
                best_ev = verif_res.get("best_evidence", "")
                # Highlight error spans
                error_spans = self.corrector.highlight_error_spans(
                    claim=claim_text,
                    contradicting_evidence=best_ev,
                    source_sentence=c_item.get("source_sentence", claim_text),
                    sent_char_start=c_item.get("char_start", 0)
                )

                # Correct claim
                edit, status = self.corrector.correct_contradicted_claim(claim_text, best_ev)
                correction_info = {
                    "original_claim": claim_text,
                    "evidence": best_ev,
                    "edit": edit,
                    "status": status,
                    "char_start": c_item.get("char_start", 0),
                    "char_end": c_item.get("char_end", len(answer))
                }
                corrections_to_merge.append(correction_info)

            claim_record = {
                "claim": claim_text,
                "claim_id": c_item.get("claim_id", f"c_{len(verified_claims)}"),
                "canonical_claim_id": c_item.get("canonical_claim_id"),
                "is_duplicate": c_item.get("is_duplicate", False),
                "paragraph_idx": c_item.get("paragraph_idx", 0),
                "claim_type": c_item.get("claim_type", "Relational"),
                "is_opinion": c_item.get("is_opinion", False),
                "initial_label": verif_res.get("initial_label", verif_res["label"]),
                "label": verif_res["label"],
                "verdict_changed": verif_res.get("verdict_changed", False),
                "change_reason": verif_res.get("change_reason"),
                "investigation": verif_res.get("investigation", {}),
                "p_e": verif_res["p_e"],
                "p_c": verif_res["p_c"],
                "p_n": verif_res["p_n"],
                "rho": rho,
                "evidence": verif_res.get("best_evidence", ""),
                "all_evidence": verif_res.get("all_evidence", retrieval.get("sentences", [])),
                "evidence_items": verif_res.get("evidence_items", retrieval.get("evidence_items", [])),
                "char_start": c_item.get("char_start", 0),
                "char_end": c_item.get("char_end", 0),
                "source_sentence": c_item.get("source_sentence", claim_text),
                "source_sentence_idx": c_item.get("source_sentence_idx", 0),
                "error_spans": error_spans,
                "correction": correction_info,
                "metadata": c_item.get("metadata", {})
            }
            verified_claims.append(claim_record)

        # M4: Calculate overall answer reliability score R(a) and counts
        score_res = self.scorer.score_answer(verified_claims)

        # M5: Full-paragraph reconstruction with verify-then-accept checks
        corrected_answer = self.corrector.reconstruct_paragraph(answer, verified_claims)
        accepted_corrections_count = sum(
            1 for c in verified_claims if (c.get("correction") or {}).get("status") == "accepted"
        )

        elapsed = time.time() - start_time

        return {
            "answer": answer,
            "claims": verified_claims,
            "reliability_score": score_res["reliability_score"],
            "mean_rho": score_res["mean_rho"],
            "mean_confidence": score_res.get("mean_confidence", 1.0),
            "max_p_c": score_res["max_p_c"],
            "counts": score_res["counts"],
            "support_rate": score_res.get("support_rate", 0.0),
            "evidence_backed_support_rate": score_res.get("evidence_backed_support_rate", 0.0),
            "contradiction_rate": score_res.get("contradiction_rate", 0.0),
            "verification_coverage": score_res.get("verification_coverage", 0.0),
            "unverified_rate": score_res.get("unverified_rate", 0.0),
            "evidence_quality": score_res.get("evidence_quality", 0.85),
            "explanation": score_res.get("explanation", ""),
            "formula_tooltip": score_res.get("formula_tooltip", ""),
            "corrected_answer": corrected_answer,
            "corrections_made": accepted_corrections_count,
            "latency_sec": elapsed
        }
