# TruthGuard 3.0: Dataset Documentation & Benchmark Splits

## 1. Benchmark Datasets

TruthGuard 3.0 is evaluated across four benchmark datasets following strict train/dev/test separation:

### 1.1 FEVER (Fact Extraction and VERification)
- **Source**: Thorne et al. (2018), EMNLP.
- **Evaluation Split**: 1,000 claims sampled uniformly across classes (SUPPORTS: 333, REFUTES: 333, NOT ENOUGH INFO: 334).
- **Format**: JSON Lines containing `id`, `claim`, `label`, `evidence_wiki_url`.
- **Target Task**: 3-class claim-level factual verification against open Wikipedia passages.

### 1.2 HaluEval-QA
- **Source**: Li et al. (2023), EMNLP.
- **Evaluation Split**: 1,000 question-answer pairs generated from user queries and evaluated for hallucinated content.
- **Format**: `question`, `knowledge`, `hallucinated_answer`, `right_answer`.
- **Target Task**: Distinguishing hallucinated answers from grounded answers in closed-domain QA.

### 1.3 RAGTruth
- **Source**: Wang et al. (2023), arXiv.
- **Evaluation Split**: 500 LLM responses across news summarization, QA, and data-to-text with word-level error span annotations.
- **Format**: `id`, `prompt`, `response`, `source_context`, `spans` (`start`, `end`, `label`).
- **Target Task**: Response-level classification (AUROC) and exact token/character error span F1.

### 1.4 TruthGuard-100 (Internal Benchmark)
- **Dataset Composition**: 100 manually curated, multi-sentence responses covering:
  - Coordinate compound sentences (e.g., Einstein, Marie Curie).
  - Mathematical and arithmetic assertions (e.g., $2+2=7$, percentage calculation).
  - Temporal drift assertions (e.g., changing CEOs, historical dates).
  - Geographical and entity inversion (e.g., Apollo 11, Statue of David).
  - Complex subjective opinions (hedged statements requiring protection).
- **Inter-Annotator Agreement**: Cohen's Kappa $\kappa = 0.864$ across two independent NLP annotators.

---

## 2. Leakage Prevention Protocol
1. **Corpus Isolation**: Gold test sentences and benchmark ground-truth labels are strictly prevented from entering the retrieval knowledge base (`truthguard/knowledge_base.py`).
2. **Context Gating**: During RAGTruth and HaluEval evaluations, the retriever queries exclusively within the designated source context of the test item.
3. **Seed Variance**: All benchmark runs are executed over three fixed random seeds ($N=3$: `42, 123, 999`), reporting $\text{Mean} \pm \text{Std}$.
