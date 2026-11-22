"""
TruthGuard 3.0 - Phase 7 Multilingual (EN + HI) Tests
Verifies:
1. Language detection between English and Hindi
2. Devanagari digit conversion
3. Hindi sentence decomposition using Purna Viram (।) and conjunctions
4. Hindi arithmetic claim detection
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from truthguard.multilingual import (
    detect_language,
    devanagari_to_arabic_numerals,
    MultilingualDecomposer
)


class TestMultilingual(unittest.TestCase):
    def test_language_detection(self):
        """Test detection of English vs Hindi script."""
        self.assertEqual(detect_language("The capital of India is New Delhi."), "en")
        self.assertEqual(detect_language("भारत की राजधानी नई दिल्ली है।"), "hi")

    def test_devanagari_digit_conversion(self):
        """Test conversion of Devanagari numerals to standard digits."""
        self.assertEqual(devanagari_to_arabic_numerals("२+२=४"), "2+2=4")
        self.assertEqual(devanagari_to_arabic_numerals("सन १९४७ में भारत स्वतंत्र हुआ।"), "सन 1947 में भारत स्वतंत्र हुआ।")

    def test_hindi_decomposition(self):
        """Test splitting multi-sentence and compound Hindi text."""
        decomposer = MultilingualDecomposer()
        hindi_text = "महात्मा गांधी का जन्म गुजरात में हुआ था। उन्होंने अहिंसा का मार्ग चुना और देश को स्वतंत्रता दिलाई।"
        claims = decomposer.decompose_hindi(hindi_text)
        self.assertGreaterEqual(len(claims), 2)
        for c in claims:
            self.assertEqual(c["language"], "hi")

    def test_hindi_math_claim(self):
        """Test identification of Hindi mathematical claim."""
        decomposer = MultilingualDecomposer()
        claims = decomposer.decompose_hindi("२ जमा २ बराबर ५ होते हैं।")
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0]["claim_type"], "Mathematical")


if __name__ == "__main__":
    unittest.main()
