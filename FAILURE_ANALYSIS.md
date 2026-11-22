# TruthGuard 3.0: Qualitative Failure Analysis & Edge Cases

## 1. Analysis of 10 Critical Factual Scenarios

### Scenario 1: Mathematical Hallucination ($2+2=7$)
- **Input**: `"2+2=7"`
- **Old Failure Mode**: Classified as NEI ($P_N=1.0, P_C=0.0$) with Reliability 50.0% because open-domain textual Wikipedia retrieval had no text passage stating `"2+2=7"`.
- **TruthGuard 3.0 Fix**: Routed to `MathEngine`. AST evaluates $2+2=4 \neq 7$.
- **Result**: `CONTRADICTED` ($P_C=0.99$), Reliability clamped to $0.005$ (0.5%), Error span `"7"` isolated, Grounded edit `"2+2=4."` accepted.

### Scenario 2: Temporal Inconsistency (Eiffel Tower in 1950)
- **Input**: `"The Eiffel Tower was completed in 1950."`
- **Retrieved Evidence**: `"The Eiffel Tower was constructed from 1887 to 1889..."`
- **Resolution**: Temporal reasoning extracts claim year `1950` vs. evidence years `{1887, 1889}`, triggering temporal discrepancy.
- **Verdict**: `CONTRADICTED` ($P_C \ge 0.92$).

### Scenario 3: Named Entity Inversion (Apollo 11)
- **Input**: `"Buzz Aldrin was the first person to walk on the lunar surface."`
- **Retrieved Evidence**: `"Commander Neil Armstrong was the first person to walk on the lunar surface..."`
- **Resolution**: Subject `Buzz Aldrin` contradicts gold attribute `Neil Armstrong`.
- **Verdict**: `CONTRADICTED` ($P_C = 0.96$). M5 substitutes `Buzz Aldrin` with `Neil Armstrong`.

### Scenario 4: Outdated Executive Information (CEO Drift)
- **Input**: `"John Doe is the current CEO of TechCorp."`
- **Retrieved Evidence**: `"In 2015, John Doe served as CEO of TechCorp."` (Publication Date: 2016)
- **Resolution**: Evidence publication date is older than temporal anchor `"current"`.
- **Verdict**: `NOT ENOUGH INFORMATION (NEI)` with temporal uncertainty flag.

### Scenario 5: Subjective Opinion Protection
- **Input**: `"In my opinion, the Mona Lisa is the most fascinating painting ever created."`
- **Resolution**: Detected as `Subjective opinion` via evaluative hedges.
- **Verdict**: Protected from hallucination penalties; marked as NEI ($P_C=0.0, \rho=0.50$).

### Scenario 6: Conflicting Sources (Date/Number Divergence)
- **Evidence A**: `"The treaty was signed in 1919."` (Tier 1 Archive)
- **Evidence B**: `"The treaty was signed in 1923."` (Tier 4 Web)
- **Resolution**: Evidence conflict detector flags `Date/Year Inconsistency` and preserves both citations.

### Scenario 7: Fabricated Academic Citation
- **Input**: `"Harrison & Vance (2023). Quantum Wormhole Routing. DOI: 10.9999/fake.quantum.2023.8888"`
- **Resolution**: Crossref and Semantic Scholar APIs return 404; landmark registry has no record.
- **Verdict**: `POTENTIALLY_FABRICATED` (Confidence: 0.94).

### Scenario 8: Non-Compensatory Penalty Clamping
- **Input**: 4 supported statements + 1 blatant contradiction ($P_C=0.98$).
- **Old Failure Mode**: Average reliability $= (4 \times 1.0 + 0.0) / 5 = 80\%$ (misleadingly high).
- **TruthGuard 3.0 Fix**: $R_A = \min(0.80, 1 - 0.98) = 0.02$ (2.0%). Factual accuracy cannot be averaged out.

### Scenario 9: Coreference Subject Recovery
- **Input**: `"Marie Curie was a chemist. She won two Nobel Prizes."`
- **Resolution**: Pronoun `She` in sentence 2 is expanded to `Marie Curie` before M2 retrieval.
- **Verdict**: Prevents `She won two Nobel Prizes` from failing retrieval due to missing named entity anchors.

### Scenario 10: Verify-Then-Accept Guardrail
- **Input**: `"The capital of France is Lyon."`
- **Revision Attempt**: Replaces `Lyon` with `Paris`. Complete sentence `"The capital of France is Paris."` re-verified through M3.
- **Verdict**: Confirmed as `SUPPORTED` ($P_E \ge 0.99$). Accepted and merged right-to-left.
