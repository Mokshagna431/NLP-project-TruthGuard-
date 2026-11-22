# TruthGuard 3.0: Complete Development Roadmap

**Roadmap Version**: 3.0.0  
**Methodology**: Phased, Test-Driven NLP Engineering & Verification  

---

## Phase Schedule & Work Breakdown

```
Phase 0 ───► Phase 1 ───► Phase 2 ───► Phase 3 ───► Phase 4 ───► Phase 5
 Audit       M1 Decomp   M2 Retrieval M3 Verif    M4 Score    M5 Correct
                                                                  │
                                                                  ▼
Phase 11 ◄── Phase 10 ◄── Phase 9 ◄─── Phase 8 ◄─── Phase 7 ◄─── Phase 6
Optimization Backend      Frontend     Benchmark    Multilingual  Citation
    │
    ▼
Phase 12 ───► Phase 13
 Testing      Docs & Papers
```

---

### Phase 0: Complete Repository Audit (MANDATORY)
- Complete technical inspection of codebase, datasets, models, and documentation.
- Deliverables: `AUDIT_REPORT.md`, `IMPLEMENTATION_STATUS.md`, `RESEARCH_GAPS.md`, `DEVELOPMENT_ROADMAP.md`, `DEVELOPMENT_PROGRESS.md`.

### Phase 1: M1 Intelligent Atomic Claim Decomposition
- Implement multi-predicate compound sentence decomposition with full context preservation (Subject, Predicate, Object, Date, Location).
- Implement fine-grained claim classification (Numerical, Temporal, Geographical, Named Entity, Scientific, Relational, Mathematical, Opinion).
- Multi-sentence coreference resolution with antecedent substitution.
- TruthGuard-100 evaluation benchmark tool and inter-annotator agreement verification.

### Phase 2: M2 Advanced Hybrid Evidence Retrieval
- Integrate source quality assessment across 6 authority tiers (Official/Government, Academic/Research, Reputable News, Encyclopedias, General Web, Low-Quality).
- Evidence provenance tracking (source URL, document title, publication date, retrieval timestamp, method, rank, relevance score).
- Evidence conflict detection identifying cross-source disagreements.
- Multi-metric retrieval evaluation: Recall@1, Recall@5, Recall@10, Precision@K, MRR, nDCG.

### Phase 3: M3 Multi-Strategy Factual Verification
- Three-class calibrated NLI (Supported, Contradicted, NEI).
- Multi-evidence joint reasoning over combined premises.
- Claim-type-aware verification routing (Symbolic Math, Temporal Reasoning, Entity Resolution, NLI).
- Temporal reasoning engine distinguishing current vs historical truth.
- Optional knowledge graph relationship verification (Subject $\to$ Predicate $\to$ Object).
- Full calibration diagnostics (ECE, Brier Score, NLL, reliability diagrams).

### Phase 4: M4 Explainable Non-Compensatory Reliability Scoring
- Dual configurable scoring formulas ($R_A$ continuous linear vs $R_B$ discontinuous step).
- Factual explainability generator formulating natural-language justifications grounded in retrieved evidence.
- Distinguish prediction confidence, evidence quality, and answer reliability.

### Phase 5: M5 Verified Grounded Correction
- Grounded minimal edit generation substituting erroneous tokens.
- Re-verification of both the edited claim and the full reconstructed sentence.
- Over-correction rate tracking, meaning preservation, and unresolved claim flagging.

### Phase 6: Citation Verification Engine
- Detection of fabricated references, non-existent papers, invalid URLs, and citation-evidence mismatches.
- Academic verification via Crossref and Semantic Scholar APIs with graceful offline fallbacks.
- Multi-state classification: `Verified`, `Partially Verified`, `Citation Mismatch`, `Unavailable`, `Potentially Fabricated`.

### Phase 7: Multilingual Hallucination Architecture
- Modular language detection and cross-lingual routing.
- Initial support for English and Hindi.
- Hindi claim decomposition and Hindi-English cross-lingual verification.

### Phase 8: Research Benchmarking & Leakage Validation
- Strict train/dev/test separation and leakage verification across FEVER, HaluEval-QA, and RAGTruth.
- Evaluation of Baselines T1–T7 + literature comparisons.
- Multi-seed execution ($[42, 123, 999]$) reporting mean $\pm$ standard deviation.
- Complete ablation matrix generation.

### Phase 9: React Frontend Improvements
- Add dedicated **Citation Verification** workbench.
- Add **Evidence Conflict Explorer** highlighting source disagreements.
- Add **Research & Benchmark Dashboard** visualizing ablation tables and calibration curves.
- Implement real backend job status tracking.

### Phase 10: Backend, Database & API Enhancements
- Schema migrations for claim categories, source metadata, citation verification, and temporal fields.
- Endpoints for citation audit, multilingual verification, and benchmark results.
- Input validation, rate limiting, and structured logging.

### Phase 11: Performance & Resource Optimization
- Batch inference for DeBERTa-v3 and Cross-Encoder.
- In-memory LRU evidence caching.
- CPU/CUDA auto-detection with documented graceful degradation.

### Phase 12: Testing & Quality Assurance
- Unit test suite for all newly created modules.
- 10 comprehensive edge-case end-to-end integration tests.

### Phase 13: Documentation & Research Publication Updates
- Updated research paper, system architecture, API documentation, and failure case studies.
