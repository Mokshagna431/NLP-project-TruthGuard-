# TruthGuard 3.0: Model Documentation & Neural Inventory

## 1. Primary Neural & Symbolic Models

| Component | Architecture / Model ID | Parameter Count | Task / Function | License / Reference |
| :--- | :--- | :---: | :--- | :--- |
| **NLI Verifier (Primary)** | `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` | 434M | 3-Class NLI Verification (Entailment, Contradiction, Neutral) | MIT / He et al. (2023) |
| **NLI Verifier (CPU Fallback)** | `typeform/distilbert-base-uncased-mnli` | 66M | Fast CPU inference fallback when memory is constrained | Apache-2.0 / Sanh et al. (2019) |
| **Dense Retriever** | `sentence-transformers/all-MiniLM-L6-v2` | 22.7M | 384-dimensional dense semantic sentence embeddings | Apache-2.0 / Reimers & Gurevych (2019) |
| **Cross-Encoder Reranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` | 22.7M | Sequence pair candidate passage reranking | Apache-2.0 |
| **Dependency Parser & NER** | `spacy/en_core_web_sm` | 13.0M | AST clause decomposition, token alignment, POS tagging | MIT / Honnibal et al. |
| **Symbolic Math Engine** | Safe Python AST Visitor | — | Arithmetic equation validation, numeric discrepancy detection | Python PSF |

---

## 2. Dynamic Config Discovery (id2label)
To prevent critical label-misalignment bugs, `ClaimVerifier` dynamically inspects `model.config.id2label` at runtime:
```python
id2label = self.model.config.id2label
for idx, lbl in id2label.items():
    lbl_lower = lbl.lower()
    if "entail" in lbl_lower:
        self.label_map["entailment"] = int(idx)
    elif "contra" in lbl_lower:
        self.label_map["contradiction"] = int(idx)
    elif "neut" in lbl_lower:
        self.label_map["neutral"] = int(idx)
```

---

## 3. Hardware Requirements & Performance Profiling

| Execution Device | Verifier Latency / Claim | RAM Footprint | VRAM Footprint | Max Batch Size |
| :--- | :---: | :---: | :---: | :---: |
| **CPU (Intel Core i7/i9 12-core)** | 180 ms – 320 ms | ~2.4 GB | 0 GB | 16 |
| **GPU (NVIDIA RTX 3080/4090 / T4)** | 22 ms – 45 ms | ~1.8 GB | ~1.6 GB | 64 |
| **CPU Fallback (DistilBERT)** | 35 ms – 65 ms | ~850 MB | 0 GB | 32 |
