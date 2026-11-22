# TruthGuard 3.0: Universal Hallucination Detection & Correction Engineering Audit

**Audit Date**: November 2026  
**Auditor**: Senior AI/ML Engineer, NLP Researcher, Backend Architect, Quality Engineer  
**System**: TruthGuard — Evidence-Grounded AI Hallucination Detection & Correction Platform  

---

## 1. Executive Summary

TruthGuard is a multi-stage verification architecture implementing M1 (Atomic Claim Decomposition), M2 (Hybrid Evidence Retrieval), M3 (NLI Verification), M4 (Reliability Scoring), and M5 (Verify-then-Accept Grounded Correction), supported by Citation Auditing and React 19 Frontend.

While the core pipeline principles (Parafact/Crosscheck dual UX, calibrated DeBERTa NLI, non-compensatory scoring $R(A) = \min(\text{mean}(\rho), 1 - \max(P_C))$, and verify-then-accept gating) are solid, the audit reveals **critical systemic weaknesses**:
1. **Hardcoded Domain Heuristics**: Specific `if "great wall" ... elif "jupiter" ...` branches exist in `retrieve.py` and `correct.py`, violating universal AI evaluation principles.
2. **Entity Ambiguity Vulnerability**: Lack of semantic context resolution for homonymous or similar entities (e.g. Taj Mahal monument in Agra vs Taj Mahal Palace hotel in Mumbai vs Bibi Ka Maqbara).
3. **Long Document Fragility**: Text is parsed as a single monolithic block without sliding window chunking, cross-chunk coreference context, or document-level completeness guarantees.
4. **General Factual Substitution in M5**: While rule-based entity/date replacement exists, complex sentence reconstruction still had hardcoded benchmark paragraph strings rather than a general semantic proposition generator.
5. **Retrieval Breadth**: Live retrieval relies on an offline 40-fact corpus plus a single-query Wikipedia fallback that needs robust multi-hop search, query expansion, and source authority evaluation.

---

## 2. Comprehensive Systemic Audit Across 15 Dimensions

| # | Dimension | Current State | Systemic Flaw & Severity | Required Engineering Fix |
|---|---|---|---|---|
| **1** | **Atomic Claim Extraction** | spaCy AST dependency parsing splits coordinate verbs and spatiotemporal prepositions. | **High**: Drops qualifiers in subordinate clauses (`because`, `although`, `if`); lacks stable claim IDs; lacks extraction metadata. | Implement recursive clause decomposition preserving conditions/qualifiers, deterministic hash-based claim IDs, and extraction metadata. |
| **2** | **Coreference Resolution** | Single-variable `salient_subject` tracked sequentially across sentences. | **Medium**: Multi-subject sentences cause antecedent drift; gender/number mismatch; resets incorrectly across paragraphs. | Implement contextual coreference tracker maintaining entity candidate stack with gender, number, and semantic salience. |
| **3** | **Entity Disambiguation** | Keyword overlap in `validate_evidence_relevance()`. | **High**: Homonymous entities (Taj Mahal Agra vs Mumbai hotel) cannot be disambiguated; relies on substring checks. | Implement semantic entity resolver checking entity category, geographic coordinates/LOC, and historical context. |
| **4** | **Evidence Retrieval** | Hybrid BM25 + SBERT + Cross-Encoder reranker. | **High**: Domain query heuristics hardcoded for Great Wall, Jupiter, India, vaccines. Fails on un-templated domains. | Replace hardcoded branches with universal Subject-Predicate-Object triple & counter-factual query generator. |
| **5** | **Source Credibility & Quality** | 5-tier authority registry (Tiers 1–5). | **Medium**: Evaluates domains statically via regex; lacks primary vs secondary source distinction and freshness checks. | Enhance registry with primary/secondary classification, institutional provenance scoring, and date freshness validation. |
| **6** | **Three-Class Decision Logic** | DeBERTa-v3 thresholds ($\tau_e=0.70, \tau_c=0.70$). | **Medium**: Thresholds can be brittle if evidence is partially relevant; missing retrieval needs strict NEI guarantee. | Formalize tripartite decision boundary with direct vs inferred evidence gating; ensure missing evidence $\to$ clean NEI. |
| **7** | **Confidence & Probability** | Softmax from decisive premise; calibrated scaling. | **Low (Fixed)**: Normalized $P_E+P_C+P_N=1.0$ implemented; needs clear distinction from frequentist probabilities in all views. | Ensure all UI views, exports, and API responses label scores as calibrated NLI confidence estimates. |
| **8** | **M5 Grounded Correction** | Verify-then-accept loop against M3 verifier. | **High**: Domain replacement branches hardcoded for 7 topics; fallback paragraph reconstruction had benchmark check. | Implement general entity/predicate substitution engine using verified evidence triples, with zero hardcoded domain checks. |
| **9** | **Duplicate Corrections** | Global deduplication in `reconstruct_paragraph()`. | **Low (Fixed)**: Semantic token overlap (>70%) deduplication successfully merges duplicate errors. | Retain and extend across multi-paragraph documents. |
| **10** | **Paragraph Reconstruction** | Sentence alignment with original text. | **Medium**: Punctuation fidelity and conjunction smoothing need universal grammar handling across arbitrary texts. | Implement grammar-preserving sentence merger with punctuation style synchronization. |
| **11** | **Citation Audit** | Regex extraction of DOIs, arXiv IDs, author-years. | **Medium**: Offline registry check is fast, but external lookup timeout can block verification if network is slow. | Implement asynchronous citation auditor with non-blocking cache and fallback registry. |
| **12** | **Conflicting Sources** | Numeric and negation conflict detector. | **Low (Fixed)**: Year discrepancy and negation polarity conflicts detected across pairs. | Add temporal conflict detection for outdated vs current state claims. |
| **13** | **Long Document Processing** | Parses entire text in one pass. | **High**: Degrades on documents > 1,500 words; memory spike and span offset drift across chunk boundaries. | Implement document chunker with 2-sentence overlap, global offset tracking, and completeness verification check. |
| **14** | **Inference & Overconfidence** | Added DIRECT vs INFERRED classification. | **Medium**: Inferred physical impossibility needs systematic confidence capping ($P_C \le 0.85$) across all domains. | Generalize inference confidence discount across medical, scientific, and legal reasoning. |
| **15** | **Frontend/Backend Sync** | React 19 + FastAPI with SQLite. | **Low**: Schema updated with claim categories, source quality, and citation audits. | Verify all endpoints, exports (PDF/CSV/JSON), and UI views render seamlessly with arbitrary inputs. |

---

## 3. Prioritized Implementation Roadmap

1. **Phase 2 & 3: Universal Claim Decomposer & Context/Entity Disambiguation**
   - Recursive clause splitting (coordinate, subordinate, conditional, temporal).
   - Document chunking for long texts with overlap and stable claim IDs.
   - Semantic entity disambiguation (e.g. Taj Mahal Agra vs Taj Mahal Mumbai).
2. **Phase 4 & 5: Universal Retrieval Engine & Source Authority**
   - Universal query generation from Subject-Predicate-Object triples without domain hardcoding.
   - Multi-hop open-domain retrieval across knowledge base and live encyclopedic endpoints.
3. **Phase 6, 7 & 8: Three-Class Verifier & Entailment Reasoning**
   - Direct vs Inferred evidence distinction applied universally across all domains.
   - Calibrated NLI confidence scoring with normalized probabilities.
4. **Phase 9: Universal M5 Grounded Correction**
   - Purely evidence-driven entity/predicate replacement engine (removing hardcoded domain replacement strings).
   - Verify-then-accept re-verification gate.
5. **Phase 10 & 11: Long Document & Citation Verification**
   - Multi-paragraph context management and complete citation auditor.
6. **Phase 12, 13 & 16: Comprehensive 30-Category Benchmark & Adversarial Validation**
   - Automated benchmark runner across 30 diverse categories with real empirical metrics.
