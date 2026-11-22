"""
Acceptance test script for Phase 1: M1 Claim Decomposition.
Tests 10 hand-written answers across all 3 decomposition modes:
- atomic_llm
- rule_based
- sentence_split
And prints decompositions of 20 FEVER-style samples and 20 RAGTruth-style samples.
"""

import json
from truthguard.decompose import ClaimDecomposer

HAND_WRITTEN_ANSWERS = [
    # 1. Iconic Eiffel Tower example from the paper
    "The Eiffel Tower was constructed in 1892 and was designed by Leonardo da Vinci.",
    # 2. Multi-fact historical figure
    "Albert Einstein was born in Ulm in 1879, and he developed the theory of general relativity.",
    # 3. Science fact with multiple clauses
    "Water boils at 100 degrees Celsius at sea level, but its boiling point decreases at higher altitudes.",
    # 4. Mixed opinion and fact
    "In my opinion Paris is great, but the Louvre Museum holds thousands of historic artworks.",
    # 5. Question and hedge
    "Could this be the oldest tree? Perhaps it has lived for over four thousand years.",
    # 6. Astronomy fact with conjunction
    "Mars has two moons named Phobos and Deimos, and both were discovered by Asaph Hall in 1877.",
    # 7. Biology fact with relative clause
    "Alexander Fleming was a Scottish physician who discovered penicillin in 1928.",
    # 8. Computing history
    "The World Wide Web was invented by Tim Berners-Lee in 1989 and the first website went live in 1991.",
    # 9. Geography with coordinate verbs
    "The Amazon River flows through South America and empties into the Atlantic Ocean.",
    # 10. Multi-sentence response with coreference
    "Neil Armstrong walked on the Moon in July 1969. He was commander of the Apollo 11 mission."
]

FEVER_SAMPLES = [
    "Roman Atwood is a content creator who produces comedic videos.",
    "The Boston Red Sox won the World Series in 2018.",
    "The Roman Empire fell entirely in 476 AD.",
    "Telemundo is an American Spanish-language television network.",
    "The Great Wall of China is visible from the Moon with the naked eye.",
    "Michael Jordan played fifteen seasons in the National Basketball Association.",
    "The United Nations was established following World War II in 1945.",
    "Oxygen is the most abundant element in the Earth's atmosphere.",
    "William Shakespeare wrote Hamlet and Romeo and Juliet.",
    "Barack Obama was elected as the 44th President of the United States in 2008.",
    "Mount Everest is located in the Himalayas on the border between Nepal and China.",
    "The Mona Lisa was painted by Michelangelo during the Renaissance.",
    "Thomas Edison invented the telephone in 1876.",
    "The Pacific Ocean is the largest and deepest ocean basin on Earth.",
    "Cleopatra was the last active ruler of the Ptolemaic Kingdom of Egypt.",
    "Saturn is the fifth planet from the Sun.",
    "J.K. Rowling wrote the Harry Potter fantasy series.",
    "The Declaration of Independence was adopted on July 4, 1776.",
    "Antarctica is considered the largest desert on Earth.",
    "Stephen Hawking authored A Brief History of Time in 1988."
]

RAGTRUTH_SAMPLES = [
    "According to the quarterly report, Acme Corp earned $4.5 million in revenue and hired 120 new employees.",
    "The clinical trial showed that Drug X reduced blood pressure by 15% and had no severe adverse effects.",
    "Summary of the meeting: The committee approved the budget proposal and scheduled the next meeting for Friday.",
    "The document states that the bridge project started in March 2020 and finished six months ahead of schedule.",
    "Customer feedback indicates that the app is responsive, but the checkout page takes too long to load.",
    "Based on the flight records, Flight 204 departed at 14:30 UTC and landed in Frankfurt after eight hours.",
    "The audit confirmed that all financial records were accurate and compliant with federal regulations.",
    "The dataset contains 50,000 annotated images and includes 20 different animal categories.",
    "The manual specifies that the machine requires 220V power and must be inspected every three months.",
    "The article mentions that the earthquake had a magnitude of 6.8 and struck near the coast of Chile.",
    "The company announced a new CEO on Tuesday and revealed plans to open three new branches in Asia.",
    "The survey indicates that 72% of respondents prefer remote work and 18% want a hybrid schedule.",
    "According to the weather report, rainfall exceeded 50mm overnight and caused localized flooding in low-lying areas.",
    "The patient has a history of type 2 diabetes and was prescribed metformin 500mg twice daily.",
    "The study demonstrated that students who studied in groups scored 12% higher on the final exam.",
    "The contract was signed on January 15 and will remain valid for a duration of three years.",
    "The system architecture uses a microservices pattern and deploys services inside Docker containers.",
    "Sales data reveals that product sales peaked during the holiday season and declined by 8% in January.",
    "The research team synthesized compound B-12 and evaluated its stability across various temperatures.",
    "The technical specification states that the database supports ACID transactions and replicates data across three nodes."
]


def run_acceptance_tests():
    print("=" * 80)
    print("PHASE 1 ACCEPTANCE: 10 HAND-WRITTEN ANSWERS UNIT TEST")
    print("=" * 80)

    decomposer_atomic = ClaimDecomposer(method="atomic_llm")
    decomposer_rules = ClaimDecomposer(method="rule_based")
    decomposer_sent = ClaimDecomposer(method="sentence_split")

    for i, ans in enumerate(HAND_WRITTEN_ANSWERS, 1):
        print(f"\n[Test {i}] Original Answer: {ans}")
        atomic_claims = decomposer_atomic.decompose(ans)
        rule_claims = decomposer_rules.decompose(ans)
        sent_claims = decomposer_sent.decompose(ans)

        print(f"  -> Atomic claims ({len(atomic_claims)}):")
        for c in atomic_claims:
            print(f"     * [{c['char_start']}:{c['char_end']}] {c['claim']}")
        print(f"  -> Rule-based claims ({len(rule_claims)}):")
        for c in rule_claims:
            print(f"     * [{c['char_start']}:{c['char_end']}] {c['claim']}")
        print(f"  -> Sentence-split claims ({len(sent_claims)}):")
        for c in sent_claims:
            print(f"     * [{c['char_start']}:{c['char_end']}] {c['claim']}")

        # Basic assertion: must produce at least 1 checkable claim for non-opinion inputs
        assert len(atomic_claims) >= 1, f"Failed to produce atomic claims for answer {i}"
        for c in atomic_claims:
            assert "claim" in c and "char_start" in c and "char_end" in c and "source_sentence_idx" in c

    print("\n" + "=" * 80)
    print("PHASE 1 ACCEPTANCE: 20 FEVER SAMPLES DECOMPOSITION")
    print("=" * 80)
    for i, fever_text in enumerate(FEVER_SAMPLES, 1):
        claims = decomposer_atomic.decompose(fever_text)
        print(f"\n[FEVER {i:02d}] {fever_text}")
        for c in claims:
            print(f"   Claim: {c['claim']} (Offsets: {c['char_start']}-{c['char_end']})")

    print("\n" + "=" * 80)
    print("PHASE 1 ACCEPTANCE: 20 RAGTRUTH SAMPLES DECOMPOSITION")
    print("=" * 80)
    for i, rag_text in enumerate(RAGTRUTH_SAMPLES, 1):
        claims = decomposer_atomic.decompose(rag_text)
        print(f"\n[RAGTruth {i:02d}] {rag_text}")
        for c in claims:
            print(f"   Claim: {c['claim']} (Offsets: {c['char_start']}-{c['char_end']})")

    print("\n" + "=" * 80)
    print("ALL PHASE 1 ACCEPTANCE CHECKS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_acceptance_tests()
