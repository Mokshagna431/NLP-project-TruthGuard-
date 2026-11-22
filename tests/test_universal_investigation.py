"""
TruthGuard Universal AI-Assisted Verification Test Suite (Stage 2 Investigation)

Validates that:
1. Every atomic claim undergoes Stage 2 Universal Evidence Investigation regardless of initial verdict.
2. SUPPORTED claims undergo confirmation corroboration and adversarial counter-evidence search.
3. CONTRADICTED claims undergo refutation verification, true-fact retrieval, and charitable defense search.
4. NEI claims undergo multi-directional expanded query search.
5. Source independence is evaluated and stored.
6. Verdict transitions are correctly handled and justified:
   - Confirmed verdicts retain classification with corroboration audit.
   - Transition from NEI -> SUPPORTED when evidence is uncovered.
   - Transition from NEI -> CONTRADICTED when refutation is uncovered.
   - Conflicting sources are detected and surfaced with explanatory rationale.
"""

import pytest
from truthguard.pipeline import TruthGuardPipeline
from truthguard.investigate import UniversalClaimInvestigator
from truthguard.verify import ClaimVerifier
from truthguard.retrieve import EvidenceRetriever


@pytest.fixture(scope="module")
def pipeline():
    return TruthGuardPipeline()


@pytest.fixture(scope="module")
def investigator():
    verifier = ClaimVerifier()
    retriever = EvidenceRetriever()
    return UniversalClaimInvestigator(verifier=verifier, retriever=retriever)


def test_01_supported_claim_undergoes_investigation(pipeline):
    """SUPPORTED claims must undergo second-stage corroboration and refutation search."""
    text = "The human heart has four chambers."
    res = pipeline.run(text)
    claim = res["claims"][0]
    
    assert claim["label"] == "SUPPORTED"
    assert claim["initial_label"] == "SUPPORTED"
    assert claim["verdict_changed"] is False
    
    inv = claim.get("investigation", {})
    assert inv.get("investigation_status") == "COMPLETED"
    assert inv.get("initial_verdict") == "SUPPORTED"
    assert inv.get("final_verdict") == "SUPPORTED"
    assert len(inv.get("expanded_queries", [])) >= 2
    assert inv.get("source_independence_score", 0.0) > 0.0
    assert "Verdict confirmed as SUPPORTED" in inv.get("confirmation_note", "")


def test_02_contradicted_claim_undergoes_investigation(pipeline):
    """CONTRADICTED claims must undergo refutation verification and charitable defense search."""
    text = "The chemical symbol for gold is Ag."
    res = pipeline.run(text)
    claim = res["claims"][0]
    
    assert claim["label"] == "CONTRADICTED"
    assert claim["initial_label"] == "CONTRADICTED"
    assert claim["verdict_changed"] is False
    
    inv = claim.get("investigation", {})
    assert inv.get("investigation_status") == "COMPLETED"
    assert inv.get("initial_verdict") == "CONTRADICTED"
    assert inv.get("final_verdict") == "CONTRADICTED"
    assert len(inv.get("expanded_queries", [])) >= 2
    assert "Verdict confirmed as CONTRADICTED" in inv.get("confirmation_note", "")
    
    # Grounded correction must be verified and present
    assert res["corrected_answer"] is not None
    assert "Au" in res["corrected_answer"]


def test_03_nei_claim_undergoes_investigation(pipeline):
    """NEI claims must undergo multi-directional search and remain NEI if evidence is absent."""
    text = "NASA plans to send exactly 12 astronauts to establish a permanent settlement on Mars in 2035."
    res = pipeline.run(text)
    claim = res["claims"][0]
    
    assert claim["label"] == "NEI"
    assert claim["initial_label"] == "NEI"
    assert claim["verdict_changed"] is False
    
    inv = claim.get("investigation", {})
    assert inv.get("investigation_status") == "COMPLETED"
    assert inv.get("initial_verdict") == "NEI"
    assert inv.get("final_verdict") == "NEI"
    assert len(inv.get("expanded_queries", [])) >= 2
    assert "Verdict confirmed as NEI" in inv.get("confirmation_note", "")
    assert res["corrected_answer"] == text


def test_04_conflicting_sources_investigation(pipeline):
    """Historical claims with conflicting sources must flag conflict and explain."""
    text = "Historical records regarding the Gulf of Tonkin incident of August 4, 1964 contain conflicting interpretations."
    res = pipeline.run(text)
    claim = res["claims"][0]
    
    assert claim["label"] in ("SUPPORTED", "NEI")
    inv = claim.get("investigation", {})
    assert inv.get("conflicting_sources_detected") is True or "conflicting" in inv.get("confirmation_note", "").lower() or "conflicting" in claim.get("evidence", "").lower()


def test_05_verdict_transition_nei_to_supported(investigator):
    """Simulates an initially NEI claim that transitions to SUPPORTED when evidence is uncovered."""
    claim = "Light travels through a vacuum at approximately 299,792,458 meters per second."
    # Initial result artificially simulated as NEI
    mock_initial_nei = {
        "label": "NEI",
        "p_e": 0.0,
        "p_c": 0.0,
        "p_n": 1.0,
        "best_evidence": "No evidence retrieved.",
        "all_evidence": [],
        "evidence_items": []
    }
    
    res = investigator.investigate_claim(claim, mock_initial_nei)
    assert res["initial_label"] == "NEI"
    assert res["label"] == "SUPPORTED"
    assert res["verdict_changed"] is True
    assert "Verdict changed from NEI to SUPPORTED" in res["change_reason"]
    assert res["p_e"] >= 0.70


def test_06_verdict_transition_nei_to_contradicted(investigator):
    """Simulates an initially NEI claim that transitions to CONTRADICTED when refutation is uncovered."""
    claim = "Humans landed on Mars through Curiosity in 2012."
    mock_initial_nei = {
        "label": "NEI",
        "p_e": 0.0,
        "p_c": 0.0,
        "p_n": 1.0,
        "best_evidence": "No evidence retrieved.",
        "all_evidence": [],
        "evidence_items": []
    }
    
    res = investigator.investigate_claim(claim, mock_initial_nei)
    assert res["initial_label"] == "NEI"
    assert res["label"] == "CONTRADICTED"
    assert res["verdict_changed"] is True
    assert "Verdict changed from NEI to CONTRADICTED" in res["change_reason"]
    assert res["p_c"] >= 0.70


def test_07_source_independence_assessment(investigator):
    """Validates source independence scoring for distinct vs duplicate publishers."""
    distinct_evidence = [
        {"publisher": "National Aeronautics and Space Administration (NASA)", "source_url": "https://nasa.gov/article1", "text": "Evidence 1"},
        {"publisher": "European Space Agency (ESA)", "source_url": "https://esa.int/article2", "text": "Evidence 2"},
        {"publisher": "Nature Astronomy", "source_url": "https://nature.com/articles/s41550", "text": "Evidence 3"}
    ]
    score, dups = investigator._assess_source_independence(distinct_evidence)
    assert score >= 0.85
    assert dups == 0
    
    duplicate_evidence = [
        {"publisher": "NASA", "source_url": "https://nasa.gov/item1", "text": "Evidence 1"},
        {"publisher": "NASA", "source_url": "https://nasa.gov/item2", "text": "Evidence 2"},
        {"publisher": "NASA", "source_url": "https://nasa.gov/item3", "text": "Evidence 3"}
    ]
    score_dup, dups_count = investigator._assess_source_independence(duplicate_evidence)
    assert score_dup < score
    assert dups_count >= 1


def test_08_pipeline_scoring_coverage_and_rates(pipeline):
    """Validates that pipeline output contains coverage, support rate, contradiction rate, and quality."""
    text = "The human heart has four chambers. The chemical symbol for gold is Ag."
    res = pipeline.run(text)
    
    assert "verification_coverage" in res
    assert "support_rate" in res
    assert "contradiction_rate" in res
    assert "unverified_rate" in res
    assert "evidence_quality" in res
    
    # 1 supported, 1 contradicted -> coverage = 1.0, support = 0.5, contradiction = 0.5, unverified = 0.0
    assert res["verification_coverage"] == 1.0
    assert res["support_rate"] == 0.5
    assert res["contradiction_rate"] == 0.5
    assert res["unverified_rate"] == 0.0
    assert res["evidence_quality"] >= 0.70
