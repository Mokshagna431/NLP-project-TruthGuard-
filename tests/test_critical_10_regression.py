"""
TruthGuard 3.0 - Critical 10 Regression Benchmark Suite
Validates the 10 mandatory factual verification, retrieval relevance, claim classification,
and grounded correction scenarios:
1. Human heart has four chambers -> SUPPORTED
2. Antibiotics cure common cold -> CONTRADICTED
3. Vitamin C required for normal collagen synthesis -> SUPPORTED
4. Excessive water intake can cause hyponatremia -> SUPPORTED
5. All bacteria are harmful to humans -> CONTRADICTED
6. Humans have established a permanent colony on Jupiter -> CONTRADICTED
7. Taj Mahal commissioned by Shah Jahan -> SUPPORTED
8. Great Wall easily visible from Moon with naked eye -> CONTRADICTED
9. A specific unrecorded person's favorite food is pizza -> NEI (no irrelevant citations attached)
10. Historical event with conflicting interpretations (Gulf of Tonkin) -> Source disagreement addressed
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from truthguard.pipeline import TruthGuardPipeline


class TestCritical10Regression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize pipeline with hybrid retrieval and NLI verification
        cls.pipeline = TruthGuardPipeline(
            decomposition_method="atomic_llm",
            retrieval_mode="hybrid",
            verifier_type="nli"
        )

    def test_01_human_heart_four_chambers(self):
        """Scenario 1: Human heart has four chambers -> SUPPORTED"""
        text = "The human heart has four chambers."
        res = self.pipeline.run(text)
        self.assertGreaterEqual(len(res["claims"]), 1)
        labels = [c["label"] for c in res["claims"]]
        self.assertIn("SUPPORTED", labels)
        self.assertEqual(res["counts"]["n_C"], 0)
        self.assertGreaterEqual(res["reliability_score"], 0.70)
        # Check evidence relevance
        primary = res["claims"][0]
        self.assertIn("heart", primary["evidence"].lower())
        self.assertIn("chamber", primary["evidence"].lower())

    def test_02_antibiotics_cure_common_cold(self):
        """Scenario 2: Antibiotics cure common cold -> CONTRADICTED & grounded correction"""
        text = "Antibiotics cure the common cold."
        res = self.pipeline.run(text)
        self.assertGreaterEqual(len(res["claims"]), 1)
        labels = [c["label"] for c in res["claims"]]
        self.assertIn("CONTRADICTED", labels)
        self.assertLessEqual(res["reliability_score"], 0.40)
        # Check correction
        self.assertGreaterEqual(res["corrections_made"], 1)
        corrected = res["corrected_answer"].lower()
        self.assertTrue(
            "ineffective against" in corrected or "not" in corrected or "treat bacterial" in corrected,
            f"Correction did not address viral ineffectiveness: {res['corrected_answer']}"
        )

    def test_03_vitamin_c_collagen_synthesis(self):
        """Scenario 3: Vitamin C required for normal collagen synthesis -> SUPPORTED"""
        text = "Vitamin C is required for normal collagen synthesis."
        res = self.pipeline.run(text)
        self.assertGreaterEqual(len(res["claims"]), 1)
        labels = [c["label"] for c in res["claims"]]
        self.assertIn("SUPPORTED", labels)
        self.assertEqual(res["counts"]["n_C"], 0)
        self.assertGreaterEqual(res["reliability_score"], 0.70)
        # Verify heart anatomy evidence was NOT falsely assigned
        for c in res["claims"]:
            self.assertNotIn("heart", c["evidence"].lower(), "Heart evidence falsely assigned to Vitamin C claim!")
            self.assertIn("collagen", c["evidence"].lower())

    def test_04_excessive_water_hyponatremia(self):
        """Scenario 4: Excessive water intake can cause hyponatremia -> SUPPORTED"""
        text = "Excessive water intake can cause hyponatremia."
        res = self.pipeline.run(text)
        self.assertGreaterEqual(len(res["claims"]), 1)
        labels = [c["label"] for c in res["claims"]]
        self.assertIn("SUPPORTED", labels)
        self.assertEqual(res["counts"]["n_C"], 0)
        self.assertGreaterEqual(res["reliability_score"], 0.70)
        for c in res["claims"]:
            self.assertIn("hyponatremia", c["evidence"].lower())

    def test_05_all_bacteria_harmful(self):
        """Scenario 5: All bacteria are harmful to humans -> CONTRADICTED (no Apollo 11 evidence!)"""
        text = "All bacteria are harmful to humans."
        res = self.pipeline.run(text)
        self.assertGreaterEqual(len(res["claims"]), 1)
        labels = [c["label"] for c in res["claims"]]
        self.assertIn("CONTRADICTED", labels)
        for c in res["claims"]:
            # Critical regression: Apollo 11 evidence must NEVER be assigned to bacteria!
            self.assertNotIn("apollo", c["evidence"].lower(), "Apollo 11 evidence falsely assigned to bacteria claim!")
            self.assertNotIn("moon", c["evidence"].lower())
            self.assertIn("bacteria", c["evidence"].lower())
        # Check concise grounded correction
        corrected = res["corrected_answer"].lower()
        self.assertTrue(
            "not all bacteria" in corrected or "beneficial" in corrected or "harmless" in corrected,
            f"Correction was not concise/accurate: {res['corrected_answer']}"
        )

    def test_06_humans_permanent_colony_jupiter(self):
        """Scenario 6: Humans have established permanent colony on Jupiter -> CONTRADICTED"""
        text = "Humans have established a permanent colony on Jupiter."
        res = self.pipeline.run(text)
        self.assertGreaterEqual(len(res["claims"]), 1)
        labels = [c["label"] for c in res["claims"]]
        self.assertIn("CONTRADICTED", labels)
        self.assertLessEqual(res["reliability_score"], 0.40)
        # Check correction
        corrected = res["corrected_answer"].lower()
        self.assertTrue("no human colonies" in corrected or "gas giant" in corrected)

    def test_07_taj_mahal_shah_jahan(self):
        """Scenario 7: Taj Mahal commissioned by Shah Jahan -> SUPPORTED (not hotel/Bibi Ka Maqbara)"""
        text = "The Taj Mahal was commissioned by Shah Jahan."
        res = self.pipeline.run(text)
        self.assertGreaterEqual(len(res["claims"]), 1)
        labels = [c["label"] for c in res["claims"]]
        self.assertIn("SUPPORTED", labels)
        self.assertEqual(res["counts"]["n_C"], 0)
        self.assertGreaterEqual(res["reliability_score"], 0.70)
        for c in res["claims"]:
            self.assertNotIn("hotel", c["evidence"].lower(), "Hotel distractor evidence retrieved!")
            self.assertNotIn("maqbara", c["evidence"].lower(), "Bibi Ka Maqbara distractor retrieved!")
            self.assertIn("shah jahan", c["evidence"].lower())

    def test_08_great_wall_visible_from_moon(self):
        """Scenario 8: Great Wall easily visible from Moon -> CONTRADICTED (not Berlin Wall!)"""
        text = "The Great Wall of China is easily visible from the Moon with the naked eye."
        res = self.pipeline.run(text)
        self.assertGreaterEqual(len(res["claims"]), 1)
        labels = [c["label"] for c in res["claims"]]
        self.assertIn("CONTRADICTED", labels)
        for c in res["claims"]:
            self.assertNotIn("berlin", c["evidence"].lower(), "Berlin Wall distractor assigned to Great Wall!")
            self.assertIn("great wall", c["evidence"].lower())
        corrected = res["corrected_answer"].lower()
        self.assertTrue("not visible" in corrected or "cannot be seen" in corrected)

    def test_09_unrecorded_person_favorite_food_pizza(self):
        """Scenario 9: Unrecorded person's favorite food is pizza -> NEI (NO citations attached!)"""
        text = "A specific unrecorded person's favorite food is pizza."
        res = self.pipeline.run(text)
        self.assertGreaterEqual(len(res["claims"]), 1)
        labels = [c["label"] for c in res["claims"]]
        self.assertIn("NEI", labels)
        self.assertEqual(res["counts"]["n_C"], 0)
        self.assertEqual(res["counts"]["n_S"], 0)
        self.assertEqual(res["corrections_made"], 0)
        for c in res["claims"]:
            # Must not attach arbitrary evidence items
            evidence_items = c.get("evidence_items", [])
            self.assertEqual(len(evidence_items), 0, "Arbitrary evidence items attached to unrecorded NEI claim!")
            # Reliability score should be around neutral 0.50
            self.assertAlmostEqual(res["reliability_score"], 0.50, delta=0.10)

    def test_10_gulf_of_tonkin_conflicting_interpretations(self):
        """Scenario 10: Gulf of Tonkin historical event -> Conflicting interpretations addressed"""
        text = "Historical records regarding the Gulf of Tonkin incident contain conflicting interpretations."
        res = self.pipeline.run(text)
        self.assertGreaterEqual(len(res["claims"]), 1)
        labels = [c["label"] for c in res["claims"]]
        # This claim about conflicting interpretations is supported by declassified historical records
        self.assertIn("SUPPORTED", labels)
        for c in res["claims"]:
            self.assertIn("tonkin", c["evidence"].lower())


if __name__ == "__main__":
    unittest.main()
