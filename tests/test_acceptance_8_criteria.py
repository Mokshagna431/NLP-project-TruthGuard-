"""
TruthGuard Acceptance Criteria Test Suite (8 Mandatory Verification Claims)

Covers the 8 core acceptance criteria claims defined in the specification:
1. "Earth revolves around the Sun approximately every 365.25 days." -> SUPPORTED
2. "Humans landed on Mars through Curiosity in 2012." -> CONTRADICTED + Grounded Correction
3. "The human brain contains approximately 86 billion neurons." -> SUPPORTED
4. "Gold's chemical symbol is Ag." -> CONTRADICTED + Grounded Correction
5. "Water boils at 100°C at standard atmospheric pressure." -> SUPPORTED
6. "The first iPhone was released in 2007." -> SUPPORTED
7. "Every person who uses AI becomes less intelligent over time." -> NEI (gated, 0 evidence)
8. "NASA will send exactly 12 astronauts to establish a permanent Mars settlement in 2035." -> NEI (gated, 0 evidence)
"""

import pytest
from truthguard.pipeline import TruthGuardPipeline


@pytest.fixture(scope="module")
def pipeline():
    return TruthGuardPipeline()


def test_claim_1_earth_revolution(pipeline):
    """Claim 1: Earth revolves around the Sun approximately every 365.25 days. -> SUPPORTED"""
    text = "Earth revolves around the Sun approximately every 365.25 days."
    res = pipeline.run(text)
    assert len(res["claims"]) >= 1, "Expected at least 1 claim extracted"
    claim_res = res["claims"][0]
    
    assert claim_res["label"] == "SUPPORTED", f"Expected SUPPORTED, got {claim_res['label']}"
    assert claim_res["p_e"] >= 0.70, f"Expected P_E >= 0.70, got {claim_res['p_e']}"
    assert len(claim_res["evidence_items"]) > 0, "Expected retrieved evidence items"
    
    # Check institutional provenance
    top_ev = claim_res["evidence_items"][0]
    assert any(term in top_ev["publisher"].lower() or term in top_ev["text"].lower() for term in ["nasa", "earth", "orbit", "sun", "jpl"])
    assert res["reliability_score"] >= 0.80, f"Expected high reliability score, got {res['reliability_score']}"


def test_claim_2_mars_curiosity_landing(pipeline):
    """Claim 2: Humans landed on Mars through Curiosity in 2012. -> CONTRADICTED + Grounded Correction"""
    text = "Humans landed on Mars through Curiosity in 2012."
    res = pipeline.run(text)
    assert len(res["claims"]) >= 1
    claim_res = res["claims"][0]
    
    assert claim_res["label"] == "CONTRADICTED", f"Expected CONTRADICTED, got {claim_res['label']}"
    assert claim_res["p_c"] >= 0.70, f"Expected P_C >= 0.70, got {claim_res['p_c']}"
    
    # Verify institutional evidence citation (NASA / JPL Curiosity)
    top_ev = claim_res["evidence_items"][0]
    assert "nasa" in top_ev["publisher"].lower() or "jpl" in top_ev["publisher"].lower()
    assert "curiosity" in top_ev["text"].lower()
    assert "unmanned" in top_ev["text"].lower() or "robotic" in top_ev["text"].lower() or "no human" in top_ev["text"].lower()
    
    # Verify M5 grounded correction
    corrected_text = res["corrected_answer"]
    assert "curiosity" in corrected_text.lower()
    assert "robotic" in corrected_text.lower() or "unmanned" in corrected_text.lower() or "no human" in corrected_text.lower()
    assert res["reliability_score"] <= 0.20, f"Expected capped reliability score for contradicted claim, got {res['reliability_score']}"


def test_claim_3_brain_neurons(pipeline):
    """Claim 3: The human brain contains approximately 86 billion neurons. -> SUPPORTED"""
    text = "The human brain contains approximately 86 billion neurons."
    res = pipeline.run(text)
    assert len(res["claims"]) >= 1
    claim_res = res["claims"][0]
    
    assert claim_res["label"] == "SUPPORTED", f"Expected SUPPORTED, got {claim_res['label']}"
    assert claim_res["p_e"] >= 0.70, f"Expected P_E >= 0.70, got {claim_res['p_e']}"
    assert len(claim_res["evidence_items"]) > 0
    
    # Verify biomedical citation
    top_ev = claim_res["evidence_items"][0]
    assert any(term in top_ev["publisher"].lower() or term in top_ev["text"].lower() for term in ["nih", "national institutes", "neurons", "brain", "azevedo"])
    assert res["reliability_score"] >= 0.80


def test_claim_4_gold_chemical_symbol(pipeline):
    """Claim 4: Gold's chemical symbol is Ag. -> CONTRADICTED + Grounded Correction"""
    text = "Gold's chemical symbol is Ag."
    res = pipeline.run(text)
    assert len(res["claims"]) >= 1
    claim_res = res["claims"][0]
    
    assert claim_res["label"] == "CONTRADICTED", f"Expected CONTRADICTED, got {claim_res['label']}"
    assert claim_res["p_c"] >= 0.70, f"Expected P_C >= 0.70, got {claim_res['p_c']}"
    
    # Verify chemical nomenclature evidence
    top_ev = claim_res["evidence_items"][0]
    assert any(term in top_ev["publisher"].lower() or term in top_ev["text"].lower() for term in ["iupac", "nist", "periodic", "au", "silver"])
    
    # Verify M5 grounded correction
    corrected_text = res["corrected_answer"]
    assert "Au" in corrected_text or "gold" in corrected_text.lower()
    assert "silver" in corrected_text.lower() or "Ag" in corrected_text
    assert res["reliability_score"] <= 0.20


def test_claim_5_water_boiling_point(pipeline):
    """Claim 5: Water boils at 100°C at standard atmospheric pressure. -> SUPPORTED"""
    text = "Water boils at 100°C at standard atmospheric pressure."
    res = pipeline.run(text)
    assert len(res["claims"]) >= 1
    claim_res = res["claims"][0]
    
    assert claim_res["label"] == "SUPPORTED", f"Expected SUPPORTED, got {claim_res['label']}"
    assert claim_res["p_e"] >= 0.70, f"Expected P_E >= 0.70, got {claim_res['p_e']}"
    assert len(claim_res["evidence_items"]) > 0
    assert res["reliability_score"] >= 0.80


def test_claim_6_iphone_release_2007(pipeline):
    """Claim 6: The first iPhone was released in 2007. -> SUPPORTED"""
    text = "The first iPhone was released in 2007."
    res = pipeline.run(text)
    assert len(res["claims"]) >= 1
    claim_res = res["claims"][0]
    
    assert claim_res["label"] == "SUPPORTED", f"Expected SUPPORTED, got {claim_res['label']}"
    assert claim_res["p_e"] >= 0.70, f"Expected P_E >= 0.70, got {claim_res['p_e']}"
    assert len(claim_res["evidence_items"]) > 0
    top_ev = claim_res["evidence_items"][0]
    assert any(term in top_ev["publisher"].lower() or term in top_ev["text"].lower() for term in ["apple", "iphone", "2007"])
    assert res["reliability_score"] >= 0.75, f"Expected high reliability score, got {res['reliability_score']}"


def test_claim_7_ai_intelligence_speculation(pipeline):
    """Claim 7: Every person who uses AI becomes less intelligent over time. -> NEI"""
    text = "Every person who uses AI becomes less intelligent over time."
    res = pipeline.run(text)
    assert len(res["claims"]) >= 1
    claim_res = res["claims"][0]
    
    # Speculative ungrounded generalization must be gated to NEI with 0 attached citations
    assert claim_res["label"] == "NEI", f"Expected NEI, got {claim_res['label']}"
    assert claim_res["p_n"] >= 0.70, f"Expected P_N >= 0.70, got {claim_res['p_n']}"
    assert len(claim_res["evidence_items"]) == 0, f"Expected 0 evidence items for ungrounded claim, got {len(claim_res['evidence_items'])}"
    # Original text must be preserved, not modified
    assert res["corrected_answer"] == text


def test_claim_8_mars_settlement_future_plan(pipeline):
    """Claim 8: NASA will send exactly 12 astronauts to establish a permanent Mars settlement in 2035. -> NEI"""
    text = "NASA will send exactly 12 astronauts to establish a permanent Mars settlement in 2035."
    res = pipeline.run(text)
    assert len(res["claims"]) >= 1
    claim_res = res["claims"][0]
    
    # Future unconfirmed prediction must be gated to NEI with 0 attached citations
    assert claim_res["label"] == "NEI", f"Expected NEI, got {claim_res['label']}"
    assert claim_res["p_n"] >= 0.70, f"Expected P_N >= 0.70, got {claim_res['p_n']}"
    assert len(claim_res["evidence_items"]) == 0, f"Expected 0 evidence items for unconfirmed future plan, got {len(claim_res['evidence_items'])}"
    # Original text must be preserved, not modified
    assert res["corrected_answer"] == text


def test_claim_13_taj_mahal_akbar_1556(pipeline):
    """Claim 13: The Taj Mahal was built by Akbar in 1556. -> CONTRADICTED"""
    text = "The Taj Mahal was built by Akbar in 1556."
    res = pipeline.run(text)
    assert len(res["claims"]) >= 1
    claim_res = res["claims"][0]
    assert claim_res["label"] == "CONTRADICTED", f"Expected CONTRADICTED, got {claim_res['label']}"
    assert claim_res["p_c"] >= 0.70


def test_claim_14_taj_mahal_unesco_1983(pipeline):
    """Claim 14: The Taj Mahal was declared a UNESCO World Heritage Site in 1983. -> SUPPORTED"""
    text = "The Taj Mahal was declared a UNESCO World Heritage Site in 1983."
    res = pipeline.run(text)
    assert len(res["claims"]) >= 1
    claim_res = res["claims"][0]
    assert claim_res["label"] == "SUPPORTED", f"Expected SUPPORTED, got {claim_res['label']}"
    assert claim_res["p_e"] >= 0.70
    assert len(claim_res["evidence_items"]) > 0
    top_ev = claim_res["evidence_items"][0]
    assert "unesco" in top_ev["text"].lower() or "unesco" in top_ev["publisher"].lower()
