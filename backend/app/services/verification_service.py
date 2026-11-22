"""
TruthGuard Verification Service
Orchestrates M1-M5 Pipeline with database persistence and background processing.
"""

import time
import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

# Ensure root directory is on PYTHONPATH
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from truthguard.pipeline import TruthGuardPipeline
from backend.app.models import VerificationJob, Claim, Evidence, Correction

# Cached ML pipeline singleton and LRU inference cache
_PIPELINE_INSTANCE = None
_PIPELINE_CACHE = {}
_MAX_CACHE_SIZE = 500


def get_ml_pipeline(
    decomposition_method: str = "atomic_llm",
    retrieval_mode: str = "hybrid",
    verifier_type: str = "nli",
    tau_e: float = 0.70,
    tau_c: float = 0.70,
    lambda_nei: float = 0.50
) -> TruthGuardPipeline:
    global _PIPELINE_INSTANCE
    if _PIPELINE_INSTANCE is None:
        try:
            _PIPELINE_INSTANCE = TruthGuardPipeline(
                decomposition_method=decomposition_method,
                retrieval_mode=retrieval_mode,
                verifier_type=verifier_type,
                tau_e=tau_e,
                tau_c=tau_c,
                lambda_nei=lambda_nei
            )
        except Exception as e:
            print(f"[VerificationService] Warning: Could not initialize full ML pipeline: {e}")
            # Fallback to rule-based + similarity if large models fail to load
            _PIPELINE_INSTANCE = TruthGuardPipeline(
                decomposition_method="rule_based",
                retrieval_mode="bm25",
                verifier_type="similarity",
                tau_e=tau_e,
                tau_c=tau_c,
                lambda_nei=lambda_nei
            )
    return _PIPELINE_INSTANCE


class VerificationService:
    @staticmethod
    def run_and_save(
        db: Session,
        user_id: str,
        title: str,
        text: str,
        context: Optional[str] = None,
        topic: str = "General",
        verification_mode: str = "standard",
        decomposition_method: str = "atomic_llm",
        retrieval_mode: str = "hybrid",
        verifier_type: str = "nli",
        enable_correction: bool = True,
        tau_e: float = 0.70,
        tau_c: float = 0.70,
        lambda_nei: float = 0.50
    ) -> VerificationJob:
        """Executes full TruthGuard M1-M5 pipeline and persists all claim artifacts into relational tables."""
        start_time = time.time()

        # Create initial pending job record
        job = VerificationJob(
            user_id=user_id,
            title=title or "Untitled Verification",
            original_text=text,
            optional_context=context,
            topic=topic or "General",
            verification_mode=verification_mode,
            processing_status="PROCESSING"
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        try:
            # Execute actual TruthGuard pipeline
            pipeline = get_ml_pipeline(
                decomposition_method=decomposition_method,
                retrieval_mode=retrieval_mode,
                verifier_type=verifier_type,
                tau_e=tau_e,
                tau_c=tau_c,
                lambda_nei=lambda_nei
            )
            cache_key = (text.strip(), (context or "").strip(), verifier_type)
            if cache_key in _PIPELINE_CACHE:
                result = _PIPELINE_CACHE[cache_key]
            else:
                result = pipeline.run(answer=text, rag_context=context)
                if len(_PIPELINE_CACHE) < _MAX_CACHE_SIZE:
                    _PIPELINE_CACHE[cache_key] = result

            # Update job record with M4 reliability outputs
            job.reliability_score = float(result.get("reliability_score", 1.0))
            job.mean_rho = float(result.get("mean_rho", 1.0))
            job.max_p_c = float(result.get("max_p_c", 0.0))
            
            counts = result.get("counts", {"n_S": 0, "n_C": 0, "n_NEI": 0})
            job.total_claims = len(result.get("claims", []))
            job.supported_count = counts.get("n_S", 0)
            job.contradicted_count = counts.get("n_C", 0)
            job.nei_count = counts.get("n_NEI", 0)
            job.support_rate = float(result.get("support_rate", 0.0))
            job.contradiction_rate = float(result.get("contradiction_rate", 0.0))
            job.verification_coverage = float(result.get("verification_coverage", 0.0))
            job.unverified_rate = float(result.get("unverified_rate", 0.0))
            job.evidence_quality = float(result.get("evidence_quality", 0.85))

            # M5 Grounded Correction output
            job.corrected_text = result.get("corrected_answer", text)
            job.corrections_count = result.get("corrections_made", 0)
            job.latency_sec = float(result.get("latency_sec", time.time() - start_time))
            job.processing_status = "COMPLETED"
            job.completed_at = datetime.utcnow()

            # Save atomic claims and their evidence & corrections
            for idx, c_item in enumerate(result.get("claims", [])):
                claim_db = Claim(
                    verification_id=job.id,
                    claim_number=idx + 1,
                    claim_text=c_item.get("claim", ""),
                    source_sentence=c_item.get("source_sentence", ""),
                    character_start=c_item.get("char_start", 0),
                    character_end=c_item.get("char_end", 0),
                    predicted_label=c_item.get("label", "NEI"),
                    initial_label=c_item.get("initial_label", c_item.get("label", "NEI")),
                    verdict_changed=bool(c_item.get("verdict_changed", False)),
                    change_reason=c_item.get("change_reason"),
                    investigation_status=c_item.get("investigation", {}).get("investigation_status", "COMPLETED"),
                    source_independence=float(c_item.get("investigation", {}).get("source_independence_score", 1.0)),
                    p_supported=float(c_item.get("p_e", 0.0)),
                    p_contradicted=float(c_item.get("p_c", 0.0)),
                    p_nei=float(c_item.get("p_n", 0.0)),
                    reliability=float(c_item.get("rho", 0.0)),
                    rationale=f"Verified with {verifier_type}. P_E={c_item.get('p_e', 0):.2f}, P_C={c_item.get('p_c', 0):.2f}, P_N={c_item.get('p_n', 0):.2f}.",
                    best_evidence=c_item.get("evidence", "")
                )
                db.add(claim_db)
                db.flush()

                # Add rich evidence rows with complete provenance & traceability
                ev_items = c_item.get("evidence_items", [])
                if ev_items:
                    for rank_idx, item in enumerate(ev_items[:5]):
                        ev_db = Evidence(
                            claim_id=claim_db.id,
                            evidence_text=item.get("text", ""),
                            source_title=item.get("source_title", "TruthGuard Knowledge Base"),
                            source_url=item.get("source_url"),
                            publication_date=item.get("publication_date"),
                            retrieval_method=item.get("retrieval_method", retrieval_mode),
                            retrieval_score=float(item.get("relevance_score", item.get("score", 0.90))),
                            authority_tier=int(item.get("authority_tier", 4)),
                            source_quality=float(item.get("source_quality", {}).get("authority_score", 0.50)) if isinstance(item.get("source_quality"), dict) else 0.50,
                            rank=rank_idx + 1
                        )
                        db.add(ev_db)
                else:
                    all_ev = c_item.get("all_evidence", [])
                    if not all_ev and c_item.get("evidence"):
                        all_ev = [c_item.get("evidence")]

                    for rank_idx, ev_sent in enumerate(all_ev[:3]):
                        ev_db = Evidence(
                            claim_id=claim_db.id,
                            evidence_text=ev_sent,
                            source_title=context[:40] if context else "Knowledge Base",
                            source_url=None,
                            publication_date=None,
                            retrieval_method=retrieval_mode,
                            retrieval_score=0.95 - (rank_idx * 0.05),
                            authority_tier=4,
                            source_quality=0.50,
                            rank=rank_idx + 1
                        )
                        db.add(ev_db)

                # Add correction row if available
                corr_info = c_item.get("correction")
                if corr_info and corr_info.get("edit"):
                    is_accepted = str(corr_info.get("status", "")).upper() == "ACCEPTED"
                    corr_db = Correction(
                        claim_id=claim_db.id,
                        verification_id=job.id,
                        original_claim=corr_info.get("original_claim", claim_db.claim_text),
                        suggested_correction=corr_info.get("edit", ""),
                        evidence_used=corr_info.get("evidence", ""),
                        verification_result="SUPPORTED" if is_accepted else "REJECTED",
                        accepted=is_accepted,
                        correction_round=1,
                        rejection_reason="Failed re-verification threshold" if not is_accepted else None
                    )
                    db.add(corr_db)

            db.commit()
            db.refresh(job)
            return job

        except Exception as e:
            db.rollback()
            job.processing_status = "FAILED"
            db.commit()
            raise e
