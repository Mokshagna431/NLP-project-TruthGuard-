"""
TruthGuard 3.0 - Phase 3 (M3) Multi-Strategy Verification Unit Tests
Verifies:
1. Calibration functions: ECE, Brier Score, NLL
2. MathEngine symbolic routing
3. Temporal anchor reasoning
4. Opinion claim handling
5. Knowledge Graph triple extraction
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
from truthguard.verify import (
    ClaimVerifier,
    compute_ece,
    compute_brier_score,
    compute_nll,
    extract_kg_triples
)


class TestVerifyV3(unittest.TestCase):
    def test_calibration_metrics(self):
        """Test calculation of ECE, Brier Score, and NLL."""
        # Perfect predictions: probs match true labels
        labels = np.array([0, 1, 2, 0])
        perfect_probs = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0]
        ])
        ece_perfect = compute_ece(perfect_probs, labels)
        self.assertAlmostEqual(ece_perfect, 0.0, places=3)

        brier_perfect = compute_brier_score(perfect_probs, labels)
        self.assertAlmostEqual(brier_perfect, 0.0, places=3)

        nll_perfect = compute_nll(perfect_probs, labels)
        self.assertAlmostEqual(nll_perfect, 0.0, places=3)

        # Imperfect predictions
        imperfect_probs = np.array([
            [0.7, 0.2, 0.1],
            [0.1, 0.8, 0.1],
            [0.2, 0.2, 0.6],
            [0.4, 0.5, 0.1]
        ])
        ece = compute_ece(imperfect_probs, labels)
        brier = compute_brier_score(imperfect_probs, labels)
        nll = compute_nll(imperfect_probs, labels)
        self.assertGreater(ece, 0.0)
        self.assertGreater(brier, 0.0)
        self.assertGreater(nll, 0.0)

    def test_math_claim_verification(self):
        """Test that math statements route directly to MathEngine."""
        verifier = ClaimVerifier(verifier_type="similarity")
        res_true = verifier.verify_claim("2+2=4", [], claim_type="Mathematical")
        self.assertEqual(res_true["label"], "SUPPORTED")
        self.assertGreaterEqual(res_true["p_e"], 0.95)

        res_false = verifier.verify_claim("2+2=7", [], claim_type="Mathematical")
        self.assertEqual(res_false["label"], "CONTRADICTED")
        self.assertGreaterEqual(res_false["p_c"], 0.95)

    def test_opinion_claim_protection(self):
        """Test that subjective opinions are protected from contradiction penalties."""
        verifier = ClaimVerifier(verifier_type="similarity")
        res = verifier.verify_claim(
            "In my opinion, the Mona Lisa is the most fascinating painting ever created.",
            ["The Mona Lisa is an oil painting by Leonardo da Vinci."],
            claim_type="Subjective opinion"
        )
        self.assertEqual(res["label"], "NEI")
        self.assertEqual(res["p_c"], 0.0)
        self.assertTrue(res.get("is_opinion"))

    def test_temporal_anchor_reasoning(self):
        """Test contradiction trigger when temporal dates disagree."""
        verifier = ClaimVerifier(verifier_type="similarity")
        res = verifier.verify_claim(
            claim="The Eiffel Tower was completed in 1950.",
            evidence_sentences=["The Eiffel Tower was constructed from 1887 to 1889 as the centerpiece of the 1889 World's Fair."],
            claim_type="Temporal"
        )
        self.assertEqual(res["label"], "CONTRADICTED")
        self.assertGreaterEqual(res["p_c"], 0.90)

    def test_kg_triple_extraction(self):
        """Test extraction of (subject, predicate, object) knowledge graph triples."""
        triples = extract_kg_triples("Albert Einstein received the Nobel Prize in Physics.")
        self.assertGreater(len(triples), 0)
        t = triples[0]
        self.assertIn("Einstein", t["subject"])
        self.assertIn("receive", t["predicate"].lower())
        self.assertIn("Prize", t["object"])


if __name__ == "__main__":
    unittest.main()
