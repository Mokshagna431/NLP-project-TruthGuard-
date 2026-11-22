"""
Test Suite for TruthGuard 3.0 Large-Scale Evaluation Benchmark (Phase 6)
Validates:
1. Dataset structure, completeness (exactly 350 items), and class balance.
2. Domain distribution across 10 distinct knowledge disciplines.
3. Execution of the evaluation engine and computation of all scientific metrics:
   - Confusion Matrix
   - Precision, Recall, Macro F1
   - Retrieval Relevance Rate
   - Citation Accuracy Rate
   - False Correction Rate (must be 0.0%)
"""

import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from truthguard.evaluation_suite import build_350_benchmark_dataset, EvaluationEngine
from truthguard.pipeline import TruthGuardPipeline


class TestEvaluationSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = build_350_benchmark_dataset()

    def test_01_dataset_completeness_and_balance(self):
        """Validates that exactly 350 balanced claims are generated across 3 classes."""
        self.assertEqual(len(self.dataset), 350, f"Expected 350 claims, got {len(self.dataset)}")

        counts = {"SUPPORTED": 0, "CONTRADICTED": 0, "NEI": 0}
        for item in self.dataset:
            counts[item["ground_truth_label"]] += 1

        self.assertEqual(counts["SUPPORTED"], 120, "Expected 120 SUPPORTED claims")
        self.assertEqual(counts["CONTRADICTED"], 120, "Expected 120 CONTRADICTED claims")
        self.assertEqual(counts["NEI"], 110, "Expected 110 NEI claims")

    def test_02_domain_coverage(self):
        """Validates that all 10 distinct knowledge domains are covered with exactly 35 claims each."""
        domains = set(item["domain"] for item in self.dataset)
        self.assertEqual(len(domains), 10, f"Expected 10 domains, got {len(domains)}")
        for d in domains:
            d_count = sum(1 for item in self.dataset if item["domain"] == d)
            self.assertEqual(d_count, 35, f"Domain '{d}' should contain exactly 35 items, got {d_count}")

    def test_03_sample_evaluation_and_metrics_structure(self):
        """Runs a fast multi-domain sample evaluation to verify metric calculation integrity."""
        # Pick 1 item of each label from 3 different domains (9 items total)
        sample_items = []
        for d in ["Medicine & Life Sciences", "Space & Astronomy", "Computing & Mathematics"]:
            for lbl in ["SUPPORTED", "CONTRADICTED", "NEI"]:
                item = next(it for it in self.dataset if it["domain"] == d and it["ground_truth_label"] == lbl)
                sample_items.append(item)

        self.assertEqual(len(sample_items), 9)

        pipeline = TruthGuardPipeline(
            decomposition_method="atomic_llm",
            retrieval_mode="hybrid",
            verifier_type="nli"
        )
        engine = EvaluationEngine(pipeline)
        report = engine.evaluate(sample_items)

        # Check required fields
        self.assertIn("overall_metrics", report)
        self.assertIn("confusion_matrix", report)
        self.assertIn("per_class_metrics", report)
        self.assertIn("retrieval_and_citation_metrics", report)
        self.assertIn("latency_report", report)

        # Accuracy and F1 must be valid numbers
        self.assertGreaterEqual(report["overall_metrics"]["accuracy"], 0.70)
        self.assertGreaterEqual(report["overall_metrics"]["macro_f1"], 0.70)
        # False correction rate on supported and NEI claims must be 0.0%
        self.assertEqual(report["retrieval_and_citation_metrics"]["false_correction_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
