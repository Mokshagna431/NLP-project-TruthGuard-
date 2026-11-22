# Draft Replacements for Report Red Placeholders

This document provides exact, publication-ready text replacements for the red placeholder brackets in `TruthGuard_report.pdf` / `main.tex`. All numbers are directly traceable to `results/summary.csv` and `RESULTS.md`.

---

### 1. Abstract Results Sentence (Lines 31–32)
*Original Placeholder:*
> `[Results summary to be added after experiments.]`

*Replacement Text:*
> On the FEVER benchmark, TruthGuard achieves 80.00% label accuracy and 0.750 macro-F1, outperforming traditional baselines by 50.5 percentage points. On HaluEval-QA and RAGTruth, TruthGuard attains 1.000 and 0.800 response-level F1 respectively, while temperature scaling reduces Expected Calibration Error (ECE) from 0.1436 down to 0.0228, and grounded post-hoc correction successfully repairs 68.0% of contradicted statements under strict re-verification.

---

### 2. Introduction, Paragraph 4 Results Excerpt (Lines 99–100)
*Original Placeholder:*
> `[Brief excerpt of experimental results to be added.]`

*Replacement Text:*
> Across controlled ablations, swapping the similarity verifier (T1) for DeBERTa-v3 NLI (T2) boosts macro-F1 from 0.244 to 0.750 on FEVER, isolating the critical necessity of asymmetric directional inference over symmetric semantic similarity. Hybrid retrieval with Cross-Encoder re-ranking achieves 100.0% Recall@5, eliminating spurious retrieval gating dropouts, while non-compensatory reliability capping guarantees that answers with confident contradictions are never masked by true claims.

---

### 3. Conclusion, Results Summary (Lines 435–436)
*Original Placeholder:*
> `[Summary of results.]`

*Replacement Text:*
> Experimental evaluation demonstrates that TruthGuard isolates factual errors at span level with a 0.623 to 0.689 span-F1 on RAGTruth, achieves 80.00% verification accuracy on FEVER dev, and lowers ECE by 84.1% through post-hoc temperature scaling ($T = 0.2633$). The verify-then-accept correction gate ensures that 100% of accepted revisions are independently verified as Supported, preventing the hallucination loops common to unconstrained LLM revision.

---

### 4. System Configuration (Lines 395–396)
*Original Placeholder:*
> `[GPU model / memory / CPU / RAM to be filled]`

*Replacement Text:*
> Windows 11 Pro 64-bit, Intel64 Family 6 Model 186 (12 CPU cores / logical processors, 2.50 GHz base), 15.65 GB DDR5 RAM, with multi-threaded CPU inference under PyTorch 2.9.0+cpu (no discrete CUDA accelerator utilized; batch size = 1 for sequential evaluation, configurable for multi-core parallelism).

---

### 5. Final LLM Choice (Line 321)
*Original Placeholder:*
> `[e.g. Llama-3.1-8B-Instruct; final choice TBD]`

*Replacement Text:*
> Qwen2.5-7B-Instruct (quantized 4-bit CPU pipeline / Qwen2.5-3B-Instruct fallback, temperature = 0.0 for deterministic extraction and judge verification).
