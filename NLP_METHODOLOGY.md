# TruthGuard 3.0: NLP Research Methodology & Algorithmic Formulations

## 1. Mathematical Formulations

### 1.1 Atomic Claim Decomposition & Span Offsets
Given a generated document $A$ comprising sentences $S = \{s_1, s_2, \dots, s_m\}$, the decomposition operator $\mathcal{D}$ maps $A$ into a set of atomic factual claims:
$$\mathcal{D}(A) = \{c_1, c_2, \dots, c_n\}$$
where each $c_i = (t_i, \text{start}_i, \text{end}_i, \tau_i, \text{subj}_i, \text{pred}_i)$ retains:
- $t_i$: Self-contained atomic claim string with resolved pronominal antecedents.
- $[\text{start}_i, \text{end}_i]$: Exact character span offsets within original text $A$.
- $\tau_i \in \{\text{Math}, \text{Num}, \text{Temp}, \text{Geo}, \text{Entity}, \text{Sci}, \text{Rel}, \text{Opinion}, \text{Pred}, \text{NonVerif}\}$: Claim category.

### 1.2 Hybrid Retrieval Fusion (RRF)
For claim $c_i$, sparse BM25 scores and dense semantic cosine similarities produce two distinct rankings over candidate premise corpus $\mathcal{K}$. The Reciprocal Rank Fusion score for premise passage $d$ is:
$$\text{RRF}(d, c_i) = \sum_{m \in \{\text{BM25}, \text{Dense}\}} \frac{1}{k_{\text{rrf}} + r_m(d)}, \quad k_{\text{rrf}} = 60$$
The top candidates from RRF are re-ranked using a Cross-Encoder scoring model $f_{\text{ce}}(c_i, d)$. Retrieval gating applies threshold $\tau_r = 0.10$:
$$\text{Gate}(c_i) = \begin{cases} \text{NEI} & \text{if } \max_d \sigma(f_{\text{ce}}(c_i, d)) < \tau_r \\ \text{Verify} & \text{otherwise} \end{cases}$$

### 1.3 Calibrated NLI Verification
For an evidence premise $e_j$ and claim hypothesis $c_i$, DeBERTa-v3 Large outputs uncalibrated logits $z_{ij} \in \mathbb{R}^3$. Temperature scaling calibration applies temperature parameter $T > 0$:
$$P(y = k \mid e_j, c_i) = \frac{\exp(z_{ij,k} / T)}{\sum_{l=1}^3 \exp(z_{ij,l} / T)}$$
where $k \in \{\text{Entailment} (E), \text{Neutral} (N), \text{Contradiction} (C)\}$.

Temperature $T^*$ is learned on validation data $\mathcal{D}_{\text{val}}$ via L-BFGS optimization:
$$T^* = \arg\min_T -\sum_{(e, c, y^*) \in \mathcal{D}_{\text{val}}} \log P(y = y^* \mid e, c; T)$$

Sentence-level aggregation across retrieved premises $\{e_1, \dots, e_K\}$ uses maximum pooling:
$$P_E(c_i) = \max_{j} p_{ij,E}, \quad P_C(c_i) = \max_{j} p_{ij,C}, \quad P_N(c_i) = \max(0, 1 - P_E(c_i) - P_C(c_i))$$

Final discrete verdict assignment follows calibrated decision thresholds $\tau_e = 0.70$ and $\tau_c = 0.70$:
$$\hat{y}(c_i) = \begin{cases} \text{SUPPORTED} & \text{if } P_E(c_i) \ge \tau_e \text{ and } P_E(c_i) > P_C(c_i) \\ \text{CONTRADICTED} & \text{if } P_C(c_i) \ge \tau_c \text{ and } P_C(c_i) > P_E(c_i) \\ \text{NOT ENOUGH INFO (NEI)} & \text{otherwise} \end{cases}$$

### 1.4 Non-Compensatory Reliability Scoring
Individual claim reliability $\rho(c_i)$ assigns partial credit $\lambda_{\text{NEI}} = 0.50$ to unverifiable assertions:
$$\rho(c_i) = P_E(c_i) + \lambda_{\text{NEI}} P_N(c_i)$$

Overall answer reliability $R(A)$ enforces a non-compensatory penalty where strong contradictions cannot be masked by averaging over benign claims:
- **Formula A (Continuous Linear)**:
  $$R_A(A) = \min\left(\frac{1}{n}\sum_{i=1}^n \rho(c_i), \; 1 - \max_{i=1\dots n} P_C(c_i)\right)$$
- **Formula B (Step Capping)**:
  $$R_B(A) = \begin{cases} \min(\bar\rho, 0.15) & \text{if } \max_i P_C(c_i) \ge \tau_c \\ \bar\rho & \text{otherwise} \end{cases}$$

---

## 2. Experimental Verification & Calibration Metrics

### 2.1 Expected Calibration Error (ECE)
Samples are partitioned into $M=15$ equal-width confidence bins $B_1, \dots, B_M \subset (0, 1]$:
$$\text{ECE} = \sum_{m=1}^M \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

### 2.2 Brier Score
Multi-class quadratic calibration loss:
$$\text{Brier} = \frac{1}{N}\sum_{i=1}^N \sum_{k=1}^3 (p_{ik} - y_{ik}^*)^2$$

### 2.3 Information Retrieval Evaluation
Evaluated over gold premise indices:
- **Precision@K**: $\frac{|\text{Retrieved}_K \cap \text{Gold}|}{K}$
- **Recall@K**: $\frac{|\text{Retrieved}_K \cap \text{Gold}|}{|\text{Gold}|}$
- **MRR (Mean Reciprocal Rank)**: $\frac{1}{\text{rank}_{\text{first relevant}}}$
- **nDCG@K (Normalized Discounted Cumulative Gain)**:
  $$\text{DCG}_K = \sum_{r=1}^K \frac{2^{\text{rel}_r} - 1}{\log_2(r + 1)}, \quad \text{nDCG}_K = \frac{\text{DCG}_K}{\text{IDCG}_K}$$
