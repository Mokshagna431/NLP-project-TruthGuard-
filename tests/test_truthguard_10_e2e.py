"""
TruthGuard 3.0 - Phase 12 Quality Assurance: 10 End-to-End Scenarios
Tests:
1. Fully supported response
2. One contradicted claim
3. Mixed supported and contradicted claims
4. NEI-only response (no evidence retrieved)
5. Mathematical hallucination (e.g. 2+2=7 -> 2+2=4)
6. Incorrect date / temporal error (Eiffel Tower completed in 1950)
7. Incorrect named entity (Leonardo da Vinci created Statue of David)
8. Conflicting sources (Evidence disagreement)
9. Outdated information / temporal uncertainty
10. Verify-then-accept correction loop
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from truthguard.pipeline import TruthGuardPipeline
from truthguard.retrieve import detect_evidence_conflicts
from truthguard.citation import CitationVerifier
from truthguard.math_engine import MathEngine


class TestTruthGuard10Scenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize pipeline in full NLI mode
        cls.pipeline = TruthGuardPipeline(
            decomposition_method="atomic_llm",
            retrieval_mode="hybrid",
            verifier_type="nli"
        )
        cls.citation_verifier = CitationVerifier()

    def test_01_fully_supported_response(self):
        """Scenario 1: Fully supported factual response against authoritative context."""
        context = "The Apollo 11 mission landed humans on the Moon on July 20, 1969. Commander Neil Armstrong was the first person to walk on the lunar surface."
        answer = "Neil Armstrong walked on the Moon on July 20, 1969."
        res = self.pipeline.run(answer, rag_context=context)
        self.assertGreaterEqual(res["counts"]["n_S"], 1)
        self.assertEqual(res["counts"]["n_C"], 0)
        self.assertGreaterEqual(res["reliability_score"], 0.70)

    def test_02_one_contradicted_claim(self):
        """Scenario 2: Single contradicted claim."""
        context = "The Eiffel Tower was constructed from 1887 to 1889 in Paris, France."
        answer = "The Eiffel Tower was constructed in Berlin, Germany."
        res = self.pipeline.run(answer, rag_context=context)
        self.assertGreaterEqual(res["counts"]["n_C"], 1)
        self.assertLess(res["reliability_score"], 0.50)

    def test_03_mixed_supported_and_contradicted_claims(self):
        """Scenario 3: Mixed supported and contradicted claims."""
        context = (
            "The Mona Lisa is a half-length portrait painting by Leonardo da Vinci. "
            "The Statue of David was sculpted by Michelangelo Buonarroti."
        )
        answer = "The Mona Lisa was painted by Leonardo da Vinci. Da Vinci also sculpted the Statue of David."
        res = self.pipeline.run(answer, rag_context=context)
        self.assertGreaterEqual(res["counts"]["n_S"], 1)
        self.assertGreaterEqual(res["counts"]["n_C"], 1)
        # Non-compensatory capping ensures R(A) is penalized despite supported claim
        self.assertLessEqual(res["reliability_score"], 0.50)

    def test_04_nei_only_response(self):
        """Scenario 4: NEI response with no evidence retrieved above threshold."""
        answer = "The mysterious alien civilization in the Andromeda galaxy has three moons."
        res = self.pipeline.run(answer, rag_context=None)
        self.assertEqual(res["counts"]["n_C"], 0)
        self.assertGreaterEqual(res["counts"]["n_NEI"], 1)
        # NEI is given partial credit (0.5) but never penalized as false
        self.assertAlmostEqual(res["reliability_score"], 0.50, places=1)

    def test_05_mathematical_hallucination(self):
        """Scenario 5: Mathematical arithmetic hallucination (e.g. 2+2=7 -> 2+2=4)."""
        answer = "2+2=7"
        res = self.pipeline.run(answer)
        self.assertEqual(res["counts"]["n_C"], 1)
        self.assertEqual(res["counts"]["n_S"], 0)
        self.assertLessEqual(res["reliability_score"], 0.05)
        self.assertEqual(res["corrected_answer"], "2+2=4")
        self.assertEqual(res["corrections_made"], 1)

    def test_06_incorrect_date(self):
        """Scenario 6: Temporal date hallucination."""
        context = "The Treaty of Versailles was signed on June 28, 1919."
        answer = "The Treaty of Versailles was signed in 1945."
        res = self.pipeline.run(answer, rag_context=context)
        self.assertGreaterEqual(res["counts"]["n_C"], 1)

    def test_07_incorrect_named_entity(self):
        """Scenario 7: Entity attribution error."""
        context = "Python was created by Guido van Rossum and first released in 1991."
        answer = "Python was created by James Gosling."
        res = self.pipeline.run(answer, rag_context=context)
        self.assertGreaterEqual(res["counts"]["n_C"], 1)

    def test_08_conflicting_sources(self):
        """Scenario 8: Disagreement between evidence passages."""
        sources = [
            {"text": "The candidate won 52% of the votes in the election.", "source_title": "Source 1"},
            {"text": "The candidate won 48% of the votes in the election.", "source_title": "Source 2"}
        ]
        conflicts = detect_evidence_conflicts(sources)
        self.assertTrue(conflicts["has_conflict"])
        self.assertIn("Discrepancy", conflicts["conflict_type"])

    def test_09_outdated_information(self):
        """Scenario 9: Temporal uncertainty / outdated evidence comparison."""
        context = "In 2015, John Doe served as the CEO of TechCorp."
        answer = "John Doe is the current CEO of TechCorp."
        res = self.pipeline.run(answer, rag_context=context)
        # Verifier flags temporal discrepancy or non-conclusive current status
        self.assertTrue(res["counts"]["n_C"] >= 1 or res["counts"]["n_NEI"] >= 1)

    def test_10_verify_then_accept_correction(self):
        """Scenario 10: Grounded correction accepted only after verification confirmation."""
        context = "The capital of France is Paris."
        answer = "The capital of France is Lyon."
        res = self.pipeline.run(answer, rag_context=context)
        self.assertEqual(res["counts"]["n_C"], 1)
        self.assertIn("Paris", res["corrected_answer"])


if __name__ == "__main__":
    unittest.main()
