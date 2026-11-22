"""
AlignScore Baseline Wrapper
Evaluates factual consistency of (context, response sentence) pairs using an alignment function.
Response score is the minimum sentence alignment score (or 1 - min alignment for hallucination probability).
"""

from typing import List, Dict, Any
from truthguard.verify import ClaimVerifier


class AlignScoreWrapper:
    def __init__(self, verifier: ClaimVerifier = None):
        self.verifier = verifier or ClaimVerifier(verifier_type="nli")

    def score_sentence(self, sentence: str, context: str) -> float:
        """
        Calculates alignment score between context and sentence.
        Returns P_E(sentence | context).
        """
        res = self.verifier.verify_claim(sentence, [context])
        # Alignment is proportional to entailment probability
        return float(res.get("p_e", 0.5))

    def score_response(self, sentences: List[str], context: str) -> Dict[str, Any]:
        """
        A response's alignment score is the minimum sentence score.
        Hallucination probability is 1.0 - min_sentence_score.
        """
        if not sentences:
            return {"alignment_score": 1.0, "hallucination_score": 0.0, "sentence_scores": []}

        sent_scores = []
        for s in sentences:
            score = self.score_sentence(s, context)
            sent_scores.append({"sentence": s, "score": score})

        min_score = float(min(item["score"] for item in sent_scores))
        return {
            "alignment_score": min_score,
            "hallucination_score": 1.0 - min_score,
            "sentence_scores": sent_scores
        }
