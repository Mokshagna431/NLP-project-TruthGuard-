# TruthGuard 3.0: Comprehensive Codebase & Research Audit Report

**Audit Date**: November 2026  
**Auditor**: Senior NLP Research Scientist & Full-Stack Systems Architect  
**Scope**: Full Repository Audit (`truthguard/`, `backend/`, `frontend/`, `data/`, `eval/`, `annotation/`, `tests/`, `configs/`, `results/`, `docs`)

---

## 1. Executive Summary

TruthGuard is an evidence-grounded AI hallucination detection, reliability scoring, and grounded correction platform. A deep inspection of all codebases, test suites, evaluation scripts, and research documents reveals a functioning prototype with a solid baseline structure (Vite/React frontend, FastAPI backend, SQLAlchemy database, calibrated DeBERTa-v3 verifier, and symbolic math engine). However, significant discrepancies exist between the described research methodology and the actual codebase.

This audit details the exact technical reality across all 10 mandated evaluation dimensions, identifying genuine implementations, partial capabilities, theoretical gaps, and critical engineering requirements for **TruthGuard 3.0**.

---

## 2. Dimensional Audit Findings

### 2.1 Features Already Implemented and Working
1. **Core M1-M5 Pipeline Skeleton (`truthguard/pipeline.py`)**: End-to-end execution path from decomposition through retrieval, verification, scoring, and correction.
2. **Symbolic AST Math Engine (`truthguard/math_engine.py`)**: Safe AST evaluation for arithmetic claims (`2+2=7` $\to$ `CONTRADICTED`, `2+2=4`), extracting numeric error spans and producing proofs.
3. **Calibrated NLI Verifier (`truthguard/verify.py`)**: DeBERTa-v3 Large (`MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli`) with dynamic `id2label` discovery, temperature scaling, and max-pooling aggregation.
4. **Relational Database (`backend/app/models/`)**: 9 SQLAlchemy ORM tables (`users`, `user_settings`, `verification_jobs`, `claims`, `evidence`, `corrections`, `saved_results`, `feedback`, `audit_logs`).
5. **FastAPI Services (`backend/app/api/`)**: JWT authentication with bcrypt, verification execution, analytics aggregation, ReportLab PDF generation, CSV/JSON/TXT exports, and RBAC admin controls.
6. **React 19 Frontend (`frontend/src/`)**: Clean editorial design system, authentication modals, verification submission, side-by-side M5 comparisons, history table, and analytics charts.
7. **Automated Backend Regression Suite (`tests/test_full_platform_backend.py`)**: 10 integration tests passing with 100% success.

---

### 2.2 Features Partially Implemented
1. **Atomic Claim Decomposition (`truthguard/decompose.py`)**:
   - *Current state*: Rule-based dependency splitting handles simple coordinate clauses (`and`, `but`, `who`), but fails on compound multi-predicate sentences with dates/locations (e.g. Einstein born in Germany in 1879, developed relativity, won Nobel in 1921).
   - *Missing*: Classification of claim types (temporal, numerical, relational, scientific, opinion); context-preserving entity enrichment; TruthGuard-100 benchmark validation.
2. **Hybrid Evidence Retrieval (`truthguard/retrieve.py`)**:
   - *Current state*: BM25 + SBERT + Cross-Encoder re-ranking with Sigmoid gating ($\tau_r = 0.10$).
   - *Missing*: Source credibility assessment, evidence provenance tracking (timestamps, publication dates), evidence conflict detection when sources disagree, and temporal evidence retrieval.
3. **Verify-Then-Accept Grounded Correction (`truthguard/correct.py`)**:
   - *Current state*: Heuristic string replacement of numbers and entities; re-verifies the isolated claim.
   - *Missing*: Re-verification of the *entire reconstructed sentence* in context; tracking over-correction rate and meaning preservation.
4. **TruthGuard-100 Tooling (`annotation/`)**:
   - *Current state*: 100 prompts/answers generated in `truthguard_100_unannotated.csv`; Cohen's Kappa script `compute_kappa.py` created.
   - *Missing*: Completed adjudication dataset and evaluation against sentence-level vs. atomic baselines.

---

### 2.3 Features Described in Reports but Missing from Code
1. **Citation Verification Module**: Completely absent from both backend and frontend. Cannot verify academic DOIs, arXiv IDs, author attributions, publication years, or detect fabricated citations.
2. **Multilingual Hallucination Detection**: Current pipeline is hardcoded for English spaCy models (`en_core_web_sm`). No language detection, Hindi support, or cross-lingual verification.
3. **Temporal Reasoning Engine**: No concept of temporal validity (e.g. distinguishing past vs. current CEOs, changing office holders, demographic numbers over time).
4. **Multi-Evidence Joint Reasoning**: Claims requiring synthesis across multiple distinct retrieved passages are evaluated individually per passage without multi-hop joint reasoning.
5. **Knowledge Graph Extraction & Verification**: Relationship triples (Subject $\to$ Predicate $\to$ Object) described in architecture are not implemented.

---

### 2.4 Incorrect or Incomplete NLP Implementations
1. **Coreference Resolution (`truthguard/decompose.py`)**:
   - Uses a naive rule checking `dep_ == 'subj'` within the same sentence doc. In multi-sentence documents, pronouns (*"She"*, *"It"*) are frequently unbound or bound to incorrect secondary nouns.
2. **Subjective Opinion Filtering**:
   - Naively filters text containing words like *"I believe"* only if sentence length is $< 8$ words. Longer sentences with opinion hedges pass through to NLI, triggering false `CONTRADICTED` or `NEI` classifications.
3. **Similarity Verifier Contradiction Blindness**:
   - Cosine similarity cannot model directional entailment. While an ad-hoc regex check was added, it lacks full semantic negation handling.

---

### 2.5 Research Methodology Inconsistencies

#### CRITICAL MATHEMATICAL SCORING FORMULA DISCREPANCY:
The repository contains two conflicting mathematical formulations for Answer Reliability $R(A)$:
- **Formula A (Original Prompt Specification)**:
  $$R_A(A) = \min\left( \frac{1}{|C|} \sum_{i=1}^{|C|} \rho(c_i), \; 1 - \max_{i} P_C(c_i) \right)$$
  *Behavior*: Continuous monotonic penalty proportional to the strongest contradiction probability.
- **Formula B (Published Research Report)**:
  $$R_B(A) = \begin{cases} 
  \bar{\rho} & \text{if } \max_i P_C(c_i) < \tau_c \\
  \min(\bar{\rho}, 0.15) & \text{if } \max_i P_C(c_i) \ge \tau_c
  \end{cases}$$
  *Behavior*: Discontinuous step penalty capping reliability at 15% upon any threshold breach.

*Audit Resolution*: Neither formula should be discarded arbitrarily. TruthGuard 3.0 must implement both scoring methods as configurable strategies (`non_compensatory_step` vs `non_compensatory_linear`), evaluate them on benchmarks, and provide comparative empirical analysis.

---

### 2.6 Dataset Leakage Possibilities
1. **Curated Knowledge Base vs. Test Sets (`truthguard/knowledge_base.py`)**:
   - In `truthguard/knowledge_base.py`, gold evidence sentences from `fever_eval.jsonl`, `halueval_eval.jsonl`, and `ragtruth_eval.jsonl` were loaded into the default retrieval corpus.
   - *Risk*: When evaluating retrieval on benchmark dev/test splits, having gold evidence pre-indexed in the open-domain knowledge base creates artificial 100% recall and evaluation leakage!
   - *Required Fix*: Isolate evaluation retrieval corpora strictly from evaluation test queries. The open-domain knowledge base must only be used in live interactive mode or open-domain benchmarks, never as a shortcut for isolated RAG evaluation.

---

### 2.7 Evaluation Errors & Gaps
1. **Evaluation Script Execution (`eval/run_experiments.py`)**:
   - Baseline wrappers (`SelfCheckGPT` and `AlignScore`) in `baselines/` rely on external dependencies and mock wrappers rather than real standalone models.
   - Small eval datasets (`data/*_eval.jsonl`) contain 10-20 sample rows rather than complete benchmark splits.
2. **Metrics Coverage**:
   - Retrieval metrics currently only report Recall@5 in logs; missing MRR, nDCG, Precision@K, and Recall@1/10.

---

### 2.8 Performance Bottlenecks
1. **Sequential NLI Execution**: Claims are verified one-by-one in a Python `for` loop. For a 20-claim document on CPU, DeBERTa-v3 takes ~18 seconds.
2. **Unbatched Cross-Encoder**: Evidence reranking runs pairs sequentially rather than in tensor batches.
3. **Database Caching**: Repeated queries for identical entity evidence re-query Wikipedia and dense indexes without a Redis or in-memory LRU cache.

---

### 2.9 Security & Robustness Considerations
1. **Math Engine AST Safety**: Verified: `truthguard/math_engine.py` uses `ast.parse` and whitelisted operators without raw `eval()`. Safe.
2. **JWT Secret Key**: Uses a default secret in development; must be enforced via `.env`.
3. **Rate Limiting**: Missing on public endpoints (`/api/auth/login`, `/api/verification`).

---

### 2.10 Duplicate or Unnecessary Code
1. `backend/server.py` and `backend/app/main.py` both have server entrypoints; delegate clearly.
2. Residual legacy test files in `eval/` reference old directory structures.

---

## 3. Audit Verdict & Transition to Implementation

TruthGuard has a functional core that can be systematically upgraded to TruthGuard 3.0 without rewriting the platform from scratch. 

Proceeding to create:
1. `IMPLEMENTATION_STATUS.md`
2. `RESEARCH_GAPS.md`
3. `DEVELOPMENT_ROADMAP.md`
4. `DEVELOPMENT_PROGRESS.md`
Followed immediately by **Phase 1: M1 Claim Decomposition Improvements**.
