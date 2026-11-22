"""
TruthGuard 3.0 - Phase 2 (M2) Hybrid Retrieval Unit Tests
Verifies:
1. Source authority tiers and quality assessment
2. Evidence conflict detection (dates, numbers, negations)
3. Retrieval metrics (MRR, nDCG@K, Precision@K, Recall@K)
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from truthguard.retrieve import (
    AUTHORITY_TIERS,
    assess_source_quality,
    detect_evidence_conflicts,
    compute_retrieval_metrics
)


class TestRetrieveV3(unittest.TestCase):
    def test_source_authority_tiers(self):
        """Test source classification into tiers 1-5."""
        # Tier 1: Academic / Gov
        gov_q = assess_source_quality("https://www.nasa.gov/mission_pages/apollo", "NASA Official Archive", "1969")
        self.assertEqual(gov_q["tier"], 1)
        self.assertGreaterEqual(gov_q["authority_weight"], 0.90)

        edu_q = assess_source_quality("https://oxford.ac.uk/research/history", "Oxford Repository")
        self.assertEqual(edu_q["tier"], 1)

        # Tier 2: Wire / Encyclopedia
        wiki_q = assess_source_quality("https://en.wikipedia.org/wiki/Albert_Einstein", "Wikipedia")
        self.assertEqual(wiki_q["tier"], 2)
        self.assertAlmostEqual(wiki_q["authority_weight"], 0.85, places=2)

        # Tier 3: Tech docs
        github_q = assess_source_quality("https://github.com/python/cpython", "Python Docs")
        self.assertEqual(github_q["tier"], 3)
        self.assertAlmostEqual(github_q["authority_weight"], 0.70, places=2)

        # Tier 5: Unknown / Blog
        blog_q = assess_source_quality("http://randomuserblog12345.org/post", "Personal Blog")
        self.assertEqual(blog_q["tier"], 5)
        self.assertLessEqual(blog_q["authority_weight"], 0.40)

    def test_conflict_detection_negation(self):
        """Test detection of contradictory claims between retrieved evidence passages."""
        ev_items = [
            {
                "text": "The project was approved by the board.",
                "source_title": "Source A",
                "authority_weight": 0.95
            },
            {
                "text": "The project was not approved by the board.",
                "source_title": "Source B",
                "authority_weight": 0.85
            }
        ]
        conflicts = detect_evidence_conflicts(ev_items)
        self.assertTrue(conflicts["has_conflict"])
        self.assertEqual(conflicts["conflict_type"], "Negation Contradiction")
        self.assertGreater(len(conflicts["conflicting_pairs"]), 0)

    def test_conflict_detection_numeric_dates(self):
        """Test numeric conflict detection across evidence items."""
        ev_items = [
            {
                "text": "The treaty was signed in 1919.",
                "source_title": "Primary Archive",
                "authority_weight": 0.95
            },
            {
                "text": "The treaty was signed in 1923.",
                "source_title": "Secondary Source",
                "authority_weight": 0.50
            }
        ]
        conflicts = detect_evidence_conflicts(ev_items)
        self.assertTrue(conflicts["has_conflict"])
        self.assertEqual(conflicts["conflict_type"], "Date/Year Inconsistency")

    def test_retrieval_metrics(self):
        """Test MRR, nDCG@5, Precision@K, and Recall@K calculation."""
        retrieved_ids = ["doc_2", "doc_5", "doc_1", "doc_9", "doc_3"]
        relevant_ids = ["doc_1", "doc_3"]

        metrics = compute_retrieval_metrics(gold_relevant=relevant_ids, retrieved=retrieved_ids, k=5)
        # doc_1 is at rank 3 -> MRR should be 1/3
        self.assertAlmostEqual(metrics["mrr"], 1.0 / 3.0, places=3)
        # 2 of 2 relevant retrieved in top 5 -> Recall@5 = 1.0
        self.assertAlmostEqual(metrics["recall@5"], 1.0, places=3)
        # 2 relevant out of 5 -> Precision@5 = 0.4
        self.assertAlmostEqual(metrics["precision@5"], 0.4, places=3)
        # nDCG should be between 0 and 1
        self.assertGreater(metrics["ndcg@5"], 0.0)
        self.assertLessEqual(metrics["ndcg@5"], 1.0)


if __name__ == "__main__":
    unittest.main()
