"""
TruthGuard 3.0 - Multilingual Hallucination Detection Module
Supports English and Hindi claim decomposition, script detection,
Devanagari numeral mapping, and cross-lingual factual verification.
"""

import re
from typing import List, Dict, Any, Tuple, Optional


# Devanagari to Arabic digits mapping
DEVANAGARI_DIGITS = {
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
}

# Hindi math words
HINDI_MATH_WORDS = {
    "जमा": "+",
    "धन": "+",
    "प्लस": "+",
    "ऋण": "-",
    "माइनस": "-",
    "गुणा": "*",
    "भाग": "/",
    "बराबर": "=",
    "होते हैं": "=",
    "होता है": "="
}


def detect_language(text: str) -> str:
    """
    Detects language of input text:
    Returns 'hi' for Hindi (Devanagari script), 'en' for English.
    """
    if not text:
        return "en"

    # Count Devanagari Unicode characters (U+0900 to U+097F)
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
    total_letters = len(re.findall(r'[a-zA-Z\u0900-\u097F]', text))

    if total_letters > 0 and (devanagari_chars / total_letters) >= 0.30:
        return "hi"
    return "en"


def devanagari_to_arabic_numerals(text: str) -> str:
    """Replaces Devanagari digits (०-९) with standard Arabic numerals (0-9)."""
    res = []
    for char in text:
        res.append(DEVANAGARI_DIGITS.get(char, char))
    return "".join(res)


class MultilingualDecomposer:
    """Decomposes non-English (Hindi) text into atomic factual claims."""

    def __init__(self):
        # Hindi sentence boundary delimiters: Purna Viram (।), double danda (॥), question mark, exclamation, newline
        self.sent_delimiter = r'[।॥\?\!\n]+'
        # Hindi coordinating conjunctions
        self.conjunctions = [r'\s+और\s+', r'\s+तथा\s+', r'\s+एवं\s+', r'\s+परंतु\s+', r'\s+लेकिन\s+', r'\s+किंतु\s+']

    def decompose_hindi(self, text: str) -> List[Dict[str, Any]]:
        """Decomposes Hindi text into independent atomic claims."""
        raw_sentences = [s.strip() for s in re.split(self.sent_delimiter, text) if s.strip()]
        claims = []

        for idx, sent in enumerate(raw_sentences):
            # Check if sentence is compound with conjunctions
            split_parts = [sent]
            for conj in self.conjunctions:
                new_parts = []
                for p in split_parts:
                    splits = [s.strip() for s in re.split(conj, p) if len(s.strip().split()) >= 3]
                    if len(splits) > 1:
                        new_parts.extend(splits)
                    else:
                        new_parts.append(p)
                split_parts = new_parts

            for part in split_parts:
                part_clean = part.strip()
                if len(part_clean.split()) >= 2:
                    # Detect mathematical claim in Hindi
                    is_math = self._is_hindi_math(part_clean)
                    claims.append({
                        "claim": part_clean if part_clean.endswith("।") else part_clean + "।",
                        "source_sentence_idx": idx,
                        "language": "hi",
                        "claim_type": "Mathematical" if is_math else "Relational",
                        "is_opinion": False
                    })

        return claims

    def _is_hindi_math(self, text: str) -> bool:
        """Checks if Hindi text represents arithmetic, e.g. '२+२=४' or '२ जमा २ बराबर ५'."""
        converted = devanagari_to_arabic_numerals(text)
        if re.search(r'[\d]\s*[\+\-\*\/]\s*[\d].*?[=]', converted):
            return True
        for hw in ["जमा", "धन", "गुणा", "बराबर"]:
            if hw in text and any(d in text for d in "०१२३४५६७८९0123456789"):
                return True
        return False
