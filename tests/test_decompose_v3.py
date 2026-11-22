"""
Unit Test Suite for TruthGuard 3.0 M1 Claim Decomposition
Tests:
- Compound sentence decomposition (Albert Einstein test case)
- Multi-sentence coreference resolution (Marie Curie test case)
- Fine-grained claim classification
- Exact span tracking
- Subjective opinion identification
"""

import sys
import os
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from truthguard.decompose import ClaimDecomposer, classify_claim_type, resolve_coreference_full


class TestM1Decomposition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decomposer = ClaimDecomposer(method="atomic_llm")

    def test_01_compound_sentence_decomposition(self):
        """Tests decomposition of multi-predicate compound sentence into 4 atomic claims."""
        text = "Albert Einstein was born in Germany in 1879, developed the theory of relativity, and received the Nobel Prize in Physics in 1921."
        claims = self.decomposer.decompose(text)
        
        self.assertGreaterEqual(len(claims), 4)
        claim_texts = [c["claim"] for c in claims]

        # Verify all 4 required facts are extracted
        self.assertTrue(any("born in Germany" in c for c in claim_texts), "Missing Germany location claim")
        self.assertTrue(any("born in 1879" in c for c in claim_texts), "Missing 1879 birth year claim")
        self.assertTrue(any("theory of relativity" in c for c in claim_texts), "Missing relativity claim")
        self.assertTrue(any("Nobel Prize" in c and "1921" in c for c in claim_texts), "Missing Nobel Prize claim")

        # Verify subject is preserved across all claims
        for c in claims:
            self.assertIn("Albert Einstein", c["claim"], f"Claim '{c['claim']}' lost the subject!")

    def test_02_coreference_resolution(self):
        """Tests resolving 3rd-person pronouns to salient antecedents across sentences."""
        text = "Marie Curie was a Polish physicist. She discovered polonium. Her research won Nobel Prizes."
        resolved, subs = resolve_coreference_full(text)
        
        self.assertIn("Marie Curie discovered polonium", resolved)
        self.assertIn("Marie Curie's research", resolved)
        self.assertGreaterEqual(len(subs), 2)

    def test_03_claim_classification(self):
        """Tests accurate claim classification into specialized categories."""
        cases = [
            ("2 + 2 = 7.", "Mathematical"),
            ("Water has the chemical formula H2O.", "Scientific"),
            ("The library contained 542,000 manuscripts.", "Numerical"),
            ("World War I started in 1914.", "Temporal"),
            ("The Amazon River is located in South America.", "Geographical"),
            ("Leonardo da Vinci painted the Mona Lisa.", "Named entity"),
            ("In my opinion, Jupiter is the most beautiful planet.", "Subjective opinion"),
            ("Global temperatures will rise by 2 degrees by 2050.", "Prediction"),
            ("What is the capital of France?", "Non-verifiable")
        ]
        for claim_text, expected_type in cases:
            pred_type = classify_claim_type(claim_text)
            self.assertEqual(pred_type, expected_type, f"Failed for '{claim_text}': got {pred_type}, expected {expected_type}")

    def test_04_character_span_tracking(self):
        """Tests that character offsets correspond to valid spans in the source text."""
        text = "Python was created by Guido van Rossum. It was released in 1991."
        claims = self.decomposer.decompose(text)
        
        self.assertGreaterEqual(len(claims), 2)
        for c in claims:
            self.assertIn("char_start", c)
            self.assertIn("char_end", c)
            self.assertGreaterEqual(c["char_start"], 0)
            self.assertLessEqual(c["char_end"], len(text))
            self.assertGreater(c["char_end"], c["char_start"])

    def test_05_opinion_protection(self):
        """Tests that subjective opinions are marked with is_opinion=True to protect from hallucination penalty."""
        text = "Jupiter is the largest planet in our solar system. In my opinion, it is also the most beautiful."
        claims = self.decomposer.decompose(text)
        
        opinion_claims = [c for c in claims if c["is_opinion"]]
        self.assertGreaterEqual(len(opinion_claims), 1)
        self.assertEqual(opinion_claims[0]["claim_type"], "Subjective opinion")


if __name__ == "__main__":
    unittest.main()
