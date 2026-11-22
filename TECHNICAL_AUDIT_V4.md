# TruthGuard 3.0: Technical Audit & Root Cause Analysis

**Audit Date**: November 2026  
**Auditor**: Senior AI/ML Engineer (RAG, NLI, Fact Verification, Evaluation)

---

## 1. Executive Summary & Root Cause Matrix

This audit investigates the 7 critical bugs reported in the TruthGuard verification pipeline:

| # | Reported Issue | Subsystems & Files | Root Cause Identified |
| :--- | :--- | :--- | :--- |
| **1** | Irrelevant evidence assigned to claims | `truthguard/retrieve.py` (`retrieve_for_claim`, `validate_evidence_relevance`) | In `retrieve_for_claim` (line 748), when initial query returns 0 candidates, fallback blindly takes `candidate_indices = list(range(min(len(corpus_sentences), self.k_s)))` (first 5 arbitrary corpus sentences). Then `validate_evidence_relevance` accepted them due to a single overlapping generic noun. |
| **2** | Vitamin C & collagen retrieves heart anatomy evidence | `truthguard/retrieve.py`, `truthguard/knowledge_base.py` | Missing ground truth facts for Vitamin C collagen synthesis in local corpus; Wikipedia search fallback hit local corpus where `validate_evidence_relevance` matched high-frequency stop nouns ("body", "system", "human"). |
| **3** | "All bacteria harmful" retrieves Apollo 11 evidence | `truthguard/retrieve.py` (`validate_evidence_relevance`) | `core_nouns` contained `"human"` from `"humans"`, and Apollo 11 evidence contained `"humans"`. A single shared generic noun satisfied `has_entity_hit = True` and scored $0.56 > 0.0$, accepting the Moon landing for a microbiology claim. |
| **4** | NEI claims not consistently distinguished from CONTRADICTED | `truthguard/verify.py` (`verify_claim`, `_verify_nli`) | When irrelevant evidence was attached, DeBERTa-v3 occasionally exhibited low-probability neutral drift or spurious contradiction spikes; claims with zero genuine evidence were not cleanly gated prior to NLI verification. |
| **5** | Corrections introduce unnecessary additional statements | `truthguard/correct.py` (`_generate_grounded_replacement`) | Strategy 6 hardcoded a 3-sentence Great Wall paragraph for any qualifier; Strategy 8 returned entire multi-sentence raw evidence passages (`return ev_clean`) rather than minimal, targeted edits. |
| **6** | Reliability scores do not reflect actual evidence quality | `truthguard/score.py` (`score_claim`, `score_answer`) | $\rho(c) = P_E + \lambda P_N$ relied purely on model softmax outputs without weighting by source authority tiers ($w_{\text{auth}}$) or validated evidence relevance ($w_{\text{rel}}$). |
| **7** | Cross-claim evidence contamination | `truthguard/pipeline.py`, `truthguard/correct.py` | In `correct.py`, `re_verify_reconstructed_paragraph` aggregated all evidence across all claims into a single shared pool (`all_ev`), allowing evidence from Claim A to verify edits in Claim B. |

---

## 2. In-Depth Root Cause Analyses

### A. The Apollo 11 / Bacteria Contamination (`truthguard/retrieve.py`)
In `validate_evidence_relevance(claim, evidence)`:
```python
# Flawed logic previously in lines 330-335:
core_nouns = [tok.lemma_.lower() for tok in claim_doc if tok.pos_ in ("NOUN", "PROPN") and not tok.is_stop]
if not has_entity_hit and core_nouns:
    ev_nouns = {tok.lemma_.lower() for tok in ev_doc if tok.pos_ in ("NOUN", "PROPN") and not tok.is_stop}
    if set(core_nouns) & ev_nouns:
        has_entity_hit = True
```
- Claim: `"All bacteria are harmful to humans"` $\to$ `core_nouns = ["bacteria", "human"]`.
- Evidence: `"Apollo 11 was the American spaceflight that first landed humans on the Moon..."` $\to$ `ev_nouns = [..., "human", ...]`.
- `set(core_nouns) & ev_nouns` evaluates to `{"human"}`.
- Because `"human"` is a noun, `has_entity_hit` becomes `True`.
- Overlap ratio $1/3 = 0.33 \implies \text{score} = 0.35 + (0.33 \times 0.65) = 0.56 > 0.0$.
- **Result**: Apollo 11 Moon landing was validated as relevant evidence for human bacterial pathology!

**Required Fix**:
1. Remove generic domain-agnostic nouns (`human`, `people`, `world`, `system`, `time`, `part`, `year`, `day`) from qualifying as topic entities.
2. Mandatory core subject noun match: If the claim's primary subject noun (e.g. `"bacteria"`) is absent from the evidence, the evidence MUST be rejected.
3. Eliminate blind corpus slice fallback (`list(range(...))`) in `retrieve_for_claim`.

---

### B. Verbose & Invasive Corrections (`truthguard/correct.py`)
In `_generate_grounded_replacement`:
- Strategy 6 previously returned a 3-sentence canned paragraph whenever `"entirely"`, `"only"`, or `"all"` appeared.
- Strategy 8 fell back to `return ev_clean`, inserting an entire raw 60-word encyclopedic passage instead of a concise, minimally invasive edit.

**Required Fix**:
- Implement concise syntactic inversion and minimal substitutions:
  - `"All bacteria are harmful to humans"` $\to$ `"Not all bacteria are harmful to humans; many bacteria are beneficial or harmless."`
  - `"Antibiotics cure the common cold"` $\to$ `"Antibiotics are ineffective against viral infections like the common cold, and only treat bacterial infections."`
- Implement 5-point independent correction verification gate.

---

### C. Evidence Quality Weighting in Reliability Scoring (`truthguard/score.py`)
Currently:
$$\rho(c) = P_E(c) + \lambda \cdot P_N(c)$$
This formula ignores:
1. Source Authority Tier (Tier 1 Institutional $= 0.95$ vs Tier 5 Blog $= 0.30$).
2. Evidence Relevance Score ($w_{\text{rel}} \in [0.0, 1.0]$).

**Required Fix**:
For SUPPORTED claims, scale empirical claim reliability by evidence credibility:
$$\rho(c) = w_{\text{source}} \cdot w_{\text{rel}} \cdot P_E(c) + \lambda \cdot P_N(c)$$
For CONTRADICTED claims, non-compensatory capping $1 - P_C(c)$ is enforced, with $P_C$ calibrated by direct vs inferred evidence type.

---

### D. Knowledge Base Completeness (`truthguard/knowledge_base.py`)
The local corpus lacks verified ground truth for:
1. Vitamin C cofactor role in collagen biosynthesis.
2. Excessive water intake causing acute hyponatremia.
3. Beneficial bacteria and the human microbiome.
4. Historical event with source disagreement (e.g. Gulf of Tonkin incident).

**Required Fix**:
Add authoritative NIH, CDC, and National Archives records with full metadata provenance.
