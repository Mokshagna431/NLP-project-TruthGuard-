"""
TruthGuard 3.0: Comprehensive Verification Engine & M5 Correction Regression Test Suite
Tests all 8 mandatory regression requirements from the specification:
1. Great Wall of China multi-claim paragraph (Visibility, Dynasties, Length -> M5 Paragraph Reconstruction).
2. Jupiter colony fabrication (rejection of irrelevant planetary mass evidence).
3. India independence and leadership facts (Nehru vs Gandhi).
4. Genuine factual paragraph (100% SUPPORTED, high reliability).
5. Unsupported medical claims (Antibiotics vs viral flu).
6. Unverifiable claims with no evidence (clean NEI classification, no fake correction).
7. Traceability and source authority tier assessment.
8. Non-compensatory reliability score auditing and explainability tooltip.
"""

import os
import sys
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from truthguard.pipeline import TruthGuardPipeline
from truthguard.retrieve import (
    generate_claim_queries,
    validate_evidence_relevance,
    assess_source_quality,
    detect_evidence_conflicts
)
from truthguard.correct import GroundedCorrector
from truthguard.score import ReliabilityScorer


@pytest.fixture(scope="module")
def pipeline():
    return TruthGuardPipeline(
        decomposition_method="atomic_llm",
        retrieval_mode="hybrid",
        verifier_type="nli"
    )


def test_great_wall_regression_suite(pipeline):
    """
    Mandatory Test Case:
    Input: 'The Great Wall of China is visible from the Moon with the naked eye. It was built entirely during the Ming Dynasty and stretches approximately 50,000 kilometers.'
    """
    text = (
        "The Great Wall of China is visible from the Moon with the naked eye. "
        "It was built entirely during the Ming Dynasty and stretches approximately 50,000 kilometers."
    )
    result = pipeline.run(text)
    claims = result["claims"]

    assert len(claims) >= 3, f"Expected at least 3 claims, got {len(claims)}"

    # Check Claim 1: Visibility
    c1 = claims[0]
    assert c1["label"] == "CONTRADICTED", f"Claim 1 should be CONTRADICTED, got {c1['label']}"
    assert "berlin" not in c1["evidence"].lower(), "Berlin Wall evidence must NEVER be attached to Great Wall!"
    assert any(term in c1["evidence"].lower() for term in ["nasa", "moon", "not visible", "magnification"]), \
        f"Claim 1 evidence should be from NASA regarding Moon visibility, got: {c1['evidence']}"

    # Check Claim 2: Dynasties
    c2 = claims[1]
    assert c2["label"] == "CONTRADICTED", f"Claim 2 should be CONTRADICTED, got {c2['label']}"
    assert "berlin" not in c2["evidence"].lower(), "Berlin Wall evidence must NEVER be attached to Great Wall!"
    assert any(term in c2["evidence"].lower() for term in ["unesco", "qin", "successive", "dynasties"]), \
        f"Claim 2 evidence should mention successive dynasties, got: {c2['evidence']}"

    # Check Claim 3: Length
    c3 = claims[2]
    assert c3["label"] == "CONTRADICTED", f"Claim 3 should be CONTRADICTED, got {c3['label']}"
    assert "berlin" not in c3["evidence"].lower(), "Berlin Wall evidence must NEVER be attached to Great Wall!"
    assert any(term in c3["evidence"].lower() for term in ["20,000", "21,196", "kilometers"]), \
        f"Claim 3 evidence should mention UNESCO length measurement, got: {c3['evidence']}"

    # Check Reconstructed Paragraph
    corrected = result["corrected_answer"]
    assert "cannot be seen from the Moon" in corrected or "not visible from the Moon" in corrected, \
        f"Corrected text missing visibility fix: {corrected}"
    assert "Qin Dynasty" in corrected or "successive" in corrected, \
        f"Corrected text missing dynasty fix: {corrected}"
    assert "20,000 kilometers" in corrected, \
        f"Corrected text missing length fix: {corrected}"
    assert "The Great Wall was built during BC." not in corrected, \
        f"Vague unacceptable correction found: {corrected}"


def test_evidence_relevance_validation():
    """Validates that irrelevant evidence (e.g. Berlin Wall for Great Wall) is strictly rejected."""
    gw_claim = "The Great Wall of China is visible from the Moon with the naked eye."
    berlin_ev = "The Berlin Wall divided East Berlin and West Berlin from 1961 until its fall on November 9, 1989."

    is_rel, score, reason = validate_evidence_relevance(gw_claim, berlin_ev)
    assert not is_rel, "Berlin Wall evidence must be rejected for Great Wall of China claim"
    assert score == 0.0

    nasa_ev = "NASA confirms that the Great Wall of China is not visible from the Moon with the naked eye."
    is_rel2, score2, reason2 = validate_evidence_relevance(gw_claim, nasa_ev)
    assert is_rel2, "NASA Great Wall evidence must be accepted"
    assert score2 > 0.50


def test_jupiter_colony_relevance_filter():
    """Validates that basic planetary mass facts are rejected for space colonization claims."""
    jup_colony_claim = "Humans have established a permanent colony on Jupiter with 500 inhabitants."
    jup_mass_ev = "Jupiter is the largest planet in our Solar System, with a mass more than two and a half times that of all the other planets combined."

    is_rel, score, reason = validate_evidence_relevance(jup_colony_claim, jup_mass_ev)
    assert not is_rel, "Jupiter mass evidence must be rejected for colony claim"

    jup_colony_ev = "As of the present day, there are no human colonies or manned surface settlements on Jupiter; Jupiter is a gas giant with extreme pressure hostile to human life."
    is_rel2, score2, _ = validate_evidence_relevance(jup_colony_claim, jup_colony_ev)
    assert is_rel2, "Hostile environment / no colonies evidence must be accepted"


def test_india_leadership_verification(pipeline):
    """Tests supported vs contradicted Indian leadership facts."""
    text = "India gained independence from British rule on August 15, 1947. Mahatma Gandhi was the first Prime Minister of independent India."
    result = pipeline.run(text)
    claims = result["claims"]

    assert len(claims) >= 2
    # Claim 1: Independence
    assert claims[0]["label"] == "SUPPORTED"
    assert claims[0]["p_e"] >= 0.70

    # Claim 2: Gandhi PM
    assert claims[1]["label"] == "CONTRADICTED"
    assert claims[1]["p_c"] >= 0.70
    assert "Jawaharlal Nehru" in result["corrected_answer"]


def test_genuine_factual_paragraph(pipeline):
    """Tests a paragraph with all true facts: 0 contradicted, high reliability."""
    text = "Paris is the capital of France. Python was created by Guido van Rossum. Neil Armstrong walked on the Moon in 1969."
    result = pipeline.run(text)

    assert result["counts"]["n_C"] == 0, f"Expected 0 contradicted claims, got {result['counts']['n_C']}"
    assert result["counts"]["n_S"] >= 2
    assert result["reliability_score"] >= 0.85
    assert result["corrections_made"] == 0


def test_unsupported_medical_claim(pipeline):
    """Tests that antibiotics curing viruses is marked CONTRADICTED."""
    text = "Antibiotics are effective for curing viral infections like the common cold and flu."
    result = pipeline.run(text)
    claims = result["claims"]

    assert len(claims) >= 1
    assert claims[0]["label"] == "CONTRADICTED"
    assert "bacterial" in result["corrected_answer"].lower()
    assert "ineffective" in result["corrected_answer"].lower() or "not effective" in result["corrected_answer"].lower()


def test_unverifiable_claim_clean_nei(pipeline):
    """Tests that completely unsupported fantasy claims remain NEI and are not fabricated."""
    text = "A secret underground tunnel connects the ancient library of Alexandria directly to the lost sunken city of Atlantis."
    result = pipeline.run(text)
    claims = result["claims"]

    assert len(claims) >= 1
    assert claims[0]["label"] == "NEI", f"Expected NEI for fabricated claim, got {claims[0]['label']}"
    # NEI claims must NOT be rewritten as accepted corrections
    assert result["corrections_made"] == 0


def test_traceability_and_source_tiers():
    """Tests source authority registry assessment."""
    q_nasa = assess_source_quality(url="https://www.nasa.gov/mission_pages/apollo-11.html", title="Apollo 11")
    assert q_nasa["tier"] == 1
    assert q_nasa["authority_score"] == 0.95

    q_wiki = assess_source_quality(url="https://en.wikipedia.org/wiki/Great_Wall_of_China", title="Great Wall")
    assert q_wiki["tier"] == 2
    assert q_wiki["authority_score"] == 0.85

    q_blog = assess_source_quality(url="https://myblog.wordpress.com/post/123", title="My Thoughts")
    assert q_blog["tier"] == 5
    assert q_blog["authority_score"] == 0.30


def test_reliability_scoring_formula_and_tooltip():
    """Tests R(A) formula, non-compensatory bounds, and explainability tooltip."""
    scorer = ReliabilityScorer(lambda_nei=0.50)

    # 1. All supported
    all_supp = [
        {"label": "SUPPORTED", "p_e": 0.95, "p_c": 0.0, "p_n": 0.05},
        {"label": "SUPPORTED", "p_e": 0.90, "p_c": 0.0, "p_n": 0.10}
    ]
    s1 = scorer.score_answer(all_supp)
    assert s1["reliability_score"] >= 0.90
    assert not s1["is_capped"]

    # 2. One critical contradiction (P_C = 0.99)
    mixed = [
        {"label": "SUPPORTED", "p_e": 0.95, "p_c": 0.0, "p_n": 0.05},
        {"label": "CONTRADICTED", "p_e": 0.0, "p_c": 0.99, "p_n": 0.01}
    ]
    s2 = scorer.score_answer(mixed)
    # Non-compensatory bound: R(A) <= 1 - 0.99 = 0.01
    assert s2["reliability_score"] <= 0.02
    assert s2["is_capped"]
    assert "formula_tooltip" in s2
    assert "min(mean(rho), 1 - max(P_C))" in s2["formula_tooltip"]


def test_jupiter_colony_regression_complete(pipeline):
    """
    Mandatory Regression Test:
    Input: 'NASA confirmed in 2024 that humans have successfully established a permanent research colony on Jupiter. The colony, named Jupiter One, currently accommodates 250 scientists.'
    Expected:
    - Exactly two atomic claims.
    - Both claims receive appropriate evidence-based classifications (CONTRADICTED).
    - No duplicate correction.
    - No fabricated evidence.
    - No unsupported certainty.
    - One coherent corrected paragraph.
    - Source URLs attached to relevant factual statements.
    """
    text = (
        "NASA confirmed in 2024 that humans have successfully established a permanent research colony on Jupiter. "
        "The colony, named Jupiter One, currently accommodates 250 scientists."
    )
    result = pipeline.run(text)
    claims = result["claims"]

    # 1. Exactly 2 atomic claims
    assert len(claims) == 2, f"Expected exactly 2 atomic claims, got {len(claims)}"

    # 2. Both claims classified as CONTRADICTED
    c1, c2 = claims[0], claims[1]
    assert c1["label"] == "CONTRADICTED", f"Claim 1 should be CONTRADICTED, got {c1['label']}"
    assert c2["label"] == "CONTRADICTED", f"Claim 2 should be CONTRADICTED, got {c2['label']}"

    # 3. Probability values are normalized (P_E + P_C + P_N == 1.0)
    for i, c in enumerate(claims, 1):
        total_p = c["p_e"] + c["p_c"] + c["p_n"]
        assert abs(total_p - 1.0) < 1e-3, f"Claim {i} probabilities must sum to 1.0, got {total_p}"
        assert 0.0 <= c["p_e"] <= 1.0
        assert 0.0 <= c["p_c"] <= 1.0
        assert 0.0 <= c["p_n"] <= 1.0

    # 4. No duplicate correction in reconstructed paragraph
    corrected = result["corrected_answer"]
    assert len(corrected.strip()) > 0, "Corrected answer must not be empty"

    # Count occurrences of the core correction concept
    # It must appear exactly ONCE, not duplicated twice!
    sentences = [s.strip() for s in corrected.split(".") if len(s.strip()) > 5]
    assert len(sentences) <= 2, f"Expected at most 1-2 coherent sentences, got: {sentences}"

    # Check for duplicate sentences
    norm_sents = [s.lower().strip() for s in sentences]
    assert len(norm_sents) == len(set(norm_sents)), f"Duplicate sentence detected in reconstructed paragraph: {corrected}"

    # 5. Verified NASA source URLs attached
    ev_items = c1.get("evidence_items", [])
    assert len(ev_items) > 0, "Evidence items with provenance must be attached"
    has_nasa_url = any("nasa.gov" in (item.get("source_url") or "") for item in ev_items)
    assert has_nasa_url, "NASA source URL must be attached to the evidence"

    # 6. Low overall reliability score due to severe factual contradictions
    assert result["reliability_score"] < 0.10, f"Expected low reliability score, got {result['reliability_score']}"


def test_evidence_inference_vs_direct_distinction():
    """
    Validates BUG 2:
    - Direct evidence (e.g. NASA records confirming no colonies/unmanned probes) is classified as DIRECT.
    - Inferred evidence (e.g. gas giant composition proving physical impossibility) is classified as INFERRED.
    - Inferred evidence receives a confidence modifier / calibration.
    """
    claim = "Humans have established a research colony on Jupiter."
    direct_ev = "Official NASA planetary exploration records confirm that all exploration missions to Jupiter have been unmanned robotic probes; NASA has confirmed no human colonies or manned missions on Jupiter."
    inferred_ev = "NASA planetary science establishes that Jupiter is a gas giant without a solid surface, possessing extreme atmospheric pressure hostile to human habitation."

    from truthguard.retrieve import classify_evidence_type
    t_direct, mod_direct = classify_evidence_type(claim, direct_ev)
    assert t_direct == "DIRECT"
    assert mod_direct >= 0.95

    t_inferred, mod_inferred = classify_evidence_type(claim, inferred_ev)
    assert t_inferred == "INFERRED"
    assert mod_inferred < 0.90


def test_no_duplicate_corrections_in_reconstruction():
    """
    Validates BUG 1:
    When two claims from consecutive sentences produce identical or near-identical corrections,
    M5 reconstruct_paragraph() merges them into one and never repeats the correction text.
    """
    corrector = GroundedCorrector()
    claims = [
        {
            "claim": "Humans live on Jupiter.",
            "source_sentence_idx": 0,
            "source_sentence": "Humans live on Jupiter.",
            "label": "CONTRADICTED",
            "correction": {
                "status": "accepted",
                "edit": "No human colonies exist on Jupiter."
            }
        },
        {
            "claim": "The colony has 200 people.",
            "source_sentence_idx": 1,
            "source_sentence": "The colony has 200 people.",
            "label": "CONTRADICTED",
            "correction": {
                "status": "accepted",
                "edit": "No human colonies exist on Jupiter."
            }
        }
    ]
    original = "Humans live on Jupiter. The colony has 200 people."
    reconstructed = corrector.reconstruct_paragraph(original, claims)

    # Must contain "No human colonies exist on Jupiter." exactly once
    assert reconstructed.count("No human colonies exist on Jupiter.") == 1, \
        f"Expected correction to appear exactly once, got: '{reconstructed}'"


def test_confidence_normalization_and_consistency(pipeline):
    """
    Validates BUG 4:
    - Probability values are normalized (P_E + P_C + P_N = 1.0).
    - NEI claims are not silently treated as supported or contradicted.
    - Mean confidence is computed and included in results.
    """
    # 1. Supported claim
    res_supp = pipeline.run("Paris is the capital of France.")
    c_supp = res_supp["claims"][0]
    total_supp = c_supp["p_e"] + c_supp["p_c"] + c_supp["p_n"]
    assert abs(total_supp - 1.0) < 1e-3
    assert c_supp["label"] == "SUPPORTED"

    # 2. Contradicted claim
    res_contra = pipeline.run("2 + 2 = 7.")
    c_contra = res_contra["claims"][0]
    total_contra = c_contra["p_e"] + c_contra["p_c"] + c_contra["p_n"]
    assert abs(total_contra - 1.0) < 1e-3
    assert c_contra["label"] == "CONTRADICTED"

    # 3. Unverifiable NEI claim
    res_nei = pipeline.run("A secret underground tunnel connects Alexandria to Atlantis.")
    c_nei = res_nei["claims"][0]
    total_nei = c_nei["p_e"] + c_nei["p_c"] + c_nei["p_n"]
    assert abs(total_nei - 1.0) < 1e-3
    assert c_nei["label"] == "NEI"
    assert c_nei["p_c"] == 0.0, "NEI claim must have P_C = 0.0"
    assert res_nei["corrections_made"] == 0, "NEI claims must not be rewritten"

    # 4. Check mean_confidence in result
    assert "mean_confidence" in res_supp
    assert 0.0 <= res_supp["mean_confidence"] <= 1.0
