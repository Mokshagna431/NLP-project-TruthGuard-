"""
End-to-End Pipeline Acceptance Test for TruthGuard
Tests full pipeline on the iconic Eiffel Tower example from the report:
"The Eiffel Tower was constructed in 1892 and was designed by Leonardo da Vinci."
"""

import sys
import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from truthguard.pipeline import TruthGuardPipeline

CONTEXT = (
    "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. "
    "It was constructed from 1887 to 1889 as the centerpiece of the 1889 World's Fair. "
    "The tower was designed by Maurice Koechlin and Emile Nouguier, and built by Gustave Eiffel's civil engineering company."
)

ANSWER = "The Eiffel Tower was constructed in 1892 and was designed by Leonardo da Vinci."


def test_e2e():
    pipeline = TruthGuardPipeline(
        decomposition_method="atomic_llm",
        retrieval_mode="hybrid",
        verifier_type="nli"
    )

    print("\nRunning TruthGuard Pipeline on:")
    print("Answer: ", ANSWER)
    print("Context:", CONTEXT)
    
    result = pipeline.run(ANSWER, rag_context=CONTEXT)

    print("\n--- Pipeline Execution Output ---")
    print(f"Reliability Score R(a): {result['reliability_score']:.4f}")
    print(f"Claim Counts: {result['counts']}")
    print(f"Corrected Answer: {result['corrected_answer']}")
    print(f"Latency: {result['latency_sec']:.2f}s\n")

    for i, c in enumerate(result["claims"], 1):
        print(f"Claim {i}: {c['claim']}")
        print(f"  Label: {c['label']} (P_E={c['p_e']:.2f}, P_C={c['p_c']:.2f}, P_N={c['p_n']:.2f})")
        print(f"  Reliability rho: {c['rho']:.2f}")
        print(f"  Evidence: {c['evidence']}")
        if c['error_spans']:
            print(f"  Error Spans: {c['error_spans']}")
        if c['correction']:
            print(f"  Correction: Edit='{c['correction']['edit']}', Status={c['correction']['status']}")
        print()

    # Assertions
    assert len(result["claims"]) >= 2, "Decomposition should produce at least 2 atomic claims!"
    assert result["counts"]["n_C"] >= 1, "At least one claim should be identified as CONTRADICTED!"
    assert result["reliability_score"] < 0.5, "Contradicted claims should heavily penalize R(a) via capping!"
    print("End-to-End Test PASSED successfully!")


if __name__ == "__main__":
    test_e2e()
