# TruthGuard 3.0: Research Gaps and Theoretical Inconsistencies

**Document Focus**: Theoretical, algorithmic, and methodological discrepancies identified between the research proposal, published findings, and software implementation.

---

## 1. Mathematical Scoring Formula Inconsistency

### 1.1 The Theoretical Discrepancy
Two distinct mathematical definitions of the Answer Reliability Score $R(A)$ exist in the project documentation:

1. **Continuous Monotonic Penalty (Specification Formula)**:
   $$R_A(A) = \min\left( \frac{1}{|C|} \sum_{i=1}^{|C|} \rho(c_i), \; 1 - \max_{i} P_C(c_i) \right)$$
   *Mathematical Properties*:
   - Continuous across $[0, 1]$.
   - The penalty scales continuously with the maximum contradiction probability $\max P_C$.
   - A single weak contradiction ($P_C = 0.72$) reduces the answer score ceiling to $0.28$, but does not force a cliff.

2. **Discontinuous Epistemic Boundary (Published Report Formula)**:
   $$R_B(A) = \begin{cases} 
   \bar{\rho} & \text{if } \max_i P_C(c_i) < \tau_c \\
   \min(\bar{\rho}, 0.15) & \text{if } \max_i P_C(c_i) \ge \tau_c
   \end{cases}$$
   *Mathematical Properties*:
   - Piecewise step function with a discontinuity at $P_C = \tau_c$.
   - Enforces a strict upper bound of $15\%$ reliability whenever any claim breaches the contradiction threshold.

### 1.2 Impact & Research Resolution
- *Problem*: Reporting numbers calculated under Formula B while citing Formula A violates experimental reproducibility.
- *Resolution in TruthGuard 3.0*:
  - Implement both methods in `truthguard/score.py` under a unified configuration parameter `scoring_strategy: 'non_compensatory_step' | 'non_compensatory_linear'`.
  - Evaluate both formulas across FEVER and HaluEval-QA.
  - Document their AUROC and response-level F1 divergence explicitly in `EXPERIMENTAL_RESULTS.md`.

---

## 2. Evidence Retrieval vs. Evaluation Leakage

### 2.1 The Issue
In `truthguard/knowledge_base.py`, gold evidence sentences from benchmark datasets were imported into the global retrieval corpus. While convenient for interactive demos, running automated benchmarks against a corpus that contains the exact gold evidence sentences produces artificial $100\%$ Recall@5 and masks retrieval failure modes in real-world open-domain scenarios.

### 2.2 Resolution
- Strictly decouple **benchmark evaluation retrieval** from the **interactive open-domain knowledge base**.
- When executing `eval/run_experiments.py`, retrieval must only query the document context specifically designated for that dataset item (e.g. Wikipedia candidate pools for FEVER, passage documents for RAGTruth).
- The open-domain multi-domain knowledge base is reserved for interactive platform verification when no context document is supplied by the user.

---

## 3. Atomic Decomposition: Granularity vs. Context Preservation

### 3.1 The Trade-Off
A core dilemma in factual claim decomposition is:
- **Over-splitting**: Breaking text into fragments so small that crucial relational context is lost (e.g. splitting *"Albert Einstein received the Nobel Prize in Physics in 1921"* into *"Albert Einstein received the Nobel Prize"* and *"The prize was in 1921"* creates an ungrounded orphan claim).
- **Under-splitting**: Leaving compound sentences intact, which forces a verifier to evaluate multiple facts simultaneously and creates ambiguity in error span localization.

### 3.2 Resolution in TruthGuard 3.0
Implement **Context-Preserving Atomic Decomposition**:
Every decomposed atomic claim must be a fully formed, independent grammatical proposition containing:
- Full explicit Subject (no unresolved third-person pronouns).
- Predicate verb phrase.
- Direct/Indirect Objects.
- Spatiotemporal anchor (Date, Year, Location) bound directly into the predicate.
Example:
Input:
> *"Albert Einstein was born in Germany in 1879, developed the theory of relativity, and received the Nobel Prize in Physics in 1921."*

Extracted Atomic Claims:
1. `Albert Einstein was born in Germany.` [Entity/Geo]
2. `Albert Einstein was born in 1879.` [Temporal]
3. `Albert Einstein developed the theory of relativity.` [Relational/Scientific]
4. `Albert Einstein received the Nobel Prize in Physics in 1921.` [Relational/Temporal]

---

## 4. Multi-Evidence Joint Synthesis Gap

### 4.1 The Issue
The current M3 verifier uses max-pooling over individual evidence sentences:
$$P_E = \max_j p_{j,\text{entail}}$$
In multi-hop claims (e.g. *"The inventor of Python worked at Google"*), verifying the claim requires synthesizing two distinct evidence passages:
- Passage 1: *"Python was created by Guido van Rossum."*
- Passage 2: *"Guido van Rossum was employed by Google from 2005 to 2012."*

Individually, neither passage entails the claim ($P_{1,E} \approx 0.1, P_{2,E} \approx 0.1$). Max-pooling yields `NEI` despite the fact that the combined evidence fully supports the claim.

### 4.2 Resolution in TruthGuard 3.0
Implement **Multi-Evidence Joint Concatenation**: When individual sentence probabilities yield borderline `NEI` for multi-hop or relational claims, M3 forms joint premise pairs:
$$\text{Premise}_{\text{joint}} = e_{j_1} \circ \text{" "} \circ e_{j_2}$$
and executes joint inference to capture cross-sentence entailment.

---

## 5. Temporal Validity and Factual Drift

### 5.1 The Issue
Standard NLI models treat all facts as timeless. However, real-world claims often depend on the temporal point of reference:
- *"Sundar Pichai is the CEO of Google."* (True currently; false in 2010).
- *"The population of India is 1.2 billion."* (True in 2011; outdated in 2026).

Without temporal awareness, a model might flag a valid historical statement as contradicted or accept an outdated statement as current truth.

### 5.2 Resolution in TruthGuard 3.0
Implement **Temporal Anchor Extraction & Reasoning**:
- Extract temporal anchors from the claim (e.g. *"current"*, *"in 2020"*, *"formerly"*).
- Extract publication dates and temporal metadata from retrieved evidence.
- Differentiate between historical truth and current truth, reporting temporal uncertainty when evidence publication dates are ambiguous or outdated.
