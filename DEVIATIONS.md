# TruthGuard: Log of Deviations from Report and Prompt Specification

This document logs every deviation from the initial draft report (`TruthGuard_report.pdf` / `main.tex`) and implementation prompt specification, detailing the engineering rationale and exact resolution.

---

### 1. Hardware & Execution Environment
- **Report Specification**: Assumed high-end GPU cluster (`[GPU model / memory / CPU / RAM to be filled]`) and prompt assumed an A100-class (40–80 GB) GPU with `vLLM` server.
- **Actual Hardware**: Windows 11 x64, Intel 12-core CPU, 15.65 GB RAM, no NVIDIA CUDA GPU available (`CUDA available: False`).
- **Deviation & Resolution**: 
  - `vLLM` does not support Windows CPU inference natively.
  - Per the prompt's explicit fallback instruction ("*The prompt falls back to Qwen2.5 if you can't get it... and the prompt assumes an A100-class GPU, so tell the LLM what hardware you actually have*"), we adopt `Qwen/Qwen2.5-7B-Instruct` / `Qwen2.5-3B-Instruct` and HuggingFace PyTorch CPU pipelines with multi-threading and batched evaluations.
  - NLI verifier and Cross-Encoder batch sizes are calibrated for multi-threaded CPU processing.

### 2. User Interface: Professional Full-Stack App instead of Streamlit
- **Report / Prompt Specification**: Streamlit (or Gradio) demo (`app/`).
- **User Instruction**: The user explicitly instructed: *"build full project with proffesional UI not with streamlit with frontend and backend commands"*.
- **Deviation & Resolution**: Built a modern full-stack application:
  - **Backend**: FastAPI REST API (`backend/server.py`) serving endpoints for decomposition, retrieval, verification, scoring, grounded correction, and benchmark metrics exploration.
  - **Frontend**: High-performance React + Vite + Tailwind CSS dashboard (`frontend/`) featuring interactive claim cards, claim-evidence cross-examination drawers, token-level span error diffs, non-compensatory reliability score gauges ($R(a)$), and benchmark comparison charts.
  - Provided dedicated launch commands: `run_backend.bat` and `run_frontend.bat`.

### 3. Sentence Max Probability Aggregation Tie-Breaking (Eq. 1 & 2)
- **Report Specification**: Eq. (1) aggregates $P_E(c) = \max_j p_E^j$, $P_C(c) = \max_j p_C^j$, and $P_N(c) = \max(0, 1 - P_E - P_C)$.
- **Deviation & Resolution**: In rare cases where sentences in evidence yield conflicting signals such that $P_E \ge \tau_E$ and $P_C \ge \tau_C$ simultaneously with $P_E = P_C$, Eq. (2) left tie-breaking undefined. We resolve ties conservatively to `NOT-ENOUGH-INFO` (`NEI`) to adhere to Rule 3 (lack of unambiguous consensus is not proof of falsehood).

### 4. Similarity Baseline (V1) Probability Definition for M4 Reliability
- **Report Specification**: V1 uses cosine similarity between claim and evidence.
- **Deviation & Resolution**: Cosine similarity is a scalar $s \in [-1, 1]$ and cannot detect semantic contradiction ($P_C \equiv 0$). Per Prompt Phase 4, we define $P_E = \mathbb{I}[s \ge \tau_{sim}]$, $P_C = 0$, and $P_N = 1 - P_E$.

### 5. Multi-Claim Sentence Merging in Grounded Correction (M5)
- **Report Specification**: "Accepted edits are merged back into the original sentence."
- **Deviation & Resolution**: When a sentence generates multiple atomic claims and more than one is contradicted and rewritten, simple string replacement causes offset collisions. We sort accepted claim replacements by character start offset in descending order (right-to-left substitution), ensuring zero string offset drift.

### 6. TruthGuard-100 Tooling Boundary (Rule 7)
- **Prompt Specification**: "Do not annotate the human evaluation set yourself. TruthGuard-100 labels must come from the two human authors. Build the tooling; leave the labelling to us."
- **Deviation & Resolution**: Followed strictly. We generate 100 diverse open-domain LLM answers, run M1 decomposition, export the unlabelled CSV (`annotation/truthguard_100_unannotated.csv`), write comprehensive guidelines (`annotation/GUIDELINES.md`), and provide the Cohen's $\kappa$ adjudication script (`annotation/compute_kappa.py`).
