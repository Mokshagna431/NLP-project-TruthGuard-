"""
TruthGuard 3.0 - Phase 6 Academic Citation Verification Tests
Verifies:
1. Citation & DOI extraction from text
2. Landmark paper verification against registry
3. Detection of fabricated / hallucinated citations
4. Detection of author/year citation mismatches
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from truthguard.citation import CitationVerifier


class TestCitationVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = CitationVerifier(timeout_sec=2.0)

    def test_extract_citations(self):
        """Test extraction of DOIs, ArXiv IDs, and bibliographic entries."""
        text = (
            "The Transformer architecture was introduced in 10.5555/3295222.3295349 by Vaswani et al. (2017). "
            "Later, Devlin et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. "
            "Also check arXiv:2005.14165 for GPT-3."
        )
        cites = self.verifier.extract_citations(text)
        self.assertGreaterEqual(len(cites), 3)
        types = [c["type"] for c in cites]
        self.assertIn("doi", types)
        self.assertIn("arxiv", types)

    def test_verify_known_landmark_paper(self):
        """Test verification of a valid landmark paper from registry."""
        cite = {
            "type": "doi",
            "doi": "10.5555/3295222.3295349",
            "authors_str": "Vaswani et al.",
            "year": 2017
        }
        res = self.verifier.verify_citation(cite)
        self.assertEqual(res["status"], "VERIFIED")
        self.assertGreaterEqual(res["confidence"], 0.95)
        self.assertIn("Attention Is All You Need", res["registry_data"]["title"])

    def test_detect_fabricated_citation(self):
        """Test detection of an entirely hallucinated LLM reference."""
        cite = {
            "type": "full_reference",
            "doi": "10.9999/fake.doi.12345.99999",
            "authors_str": "Fictitious, A. and Hallucinator, B.",
            "title": "Quantum Hallucinations in Multi-Dimensional Wormhole Neural Networks",
            "year": 2024
        }
        res = self.verifier.verify_citation(cite)
        self.assertEqual(res["status"], "POTENTIALLY_FABRICATED")
        self.assertGreaterEqual(res["confidence"], 0.85)

    def test_verify_all_in_text(self):
        """Test batch extraction and verification across a document."""
        doc = (
            "According to Vaswani et al. (2017), self-attention is effective. "
            "However, Smith et al. (2024). A Completely Fabricated Study on Unicorns and Dragons in Deep Learning. 10.1234/fake.paper.8888 claims otherwise."
        )
        res = self.verifier.verify_all_in_text(doc)
        self.assertGreater(res["total_citations"], 0)
        self.assertIn("counts", res)


if __name__ == "__main__":
    unittest.main()
