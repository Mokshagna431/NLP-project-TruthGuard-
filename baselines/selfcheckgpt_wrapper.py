"""
SelfCheckGPT-NLI Baseline Wrapper
Implements reference-free hallucination detection via sampled generations (N=20)
and cross-sentence NLI consistency scoring.
"""

import numpy as np
from typing import List, Dict, Any
from truthguard.verify import ClaimVerifier


class SelfCheckGPTNLI:
    def __init__(
        self,
        num_samples: int = 20,
        verifier: ClaimVerifier = None
    ):
        self.num_samples = num_samples
        self.verifier = verifier or ClaimVerifier(verifier_type="nli")

    def predict_score(
        self,
        sentence: str,
        sampled_passages: List[str]
    ) -> float:
        """
        Calculates contradiction / inconsistency score for a sentence across N sampled responses.
        Higher score indicates higher probability of hallucination.
        """
        if not sampled_passages:
            return 0.5

        contradiction_scores = []
        for sample in sampled_passages:
            res = self.verifier.verify_claim(sentence, [sample])
            contradiction_scores.append(res.get("p_c", 0.0))

        # Inconsistency score is the mean contradiction across samples
        return float(np.mean(contradiction_scores))

    def score_response(
        self,
        sentences: List[str],
        sampled_passages: List[str]
    ) -> Dict[str, Any]:
        """
        A response's score is the maximum sentence inconsistency score.
        """
        if not sentences:
            return {"response_score": 0.0, "sentence_scores": []}

        sent_scores = []
        for s in sentences:
            score = self.predict_score(s, sampled_passages)
            sent_scores.append({"sentence": s, "score": score})

        max_score = float(max(item["score"] for item in sent_scores))
        return {
            "response_score": max_score,
            "sentence_scores": sent_scores
        }
