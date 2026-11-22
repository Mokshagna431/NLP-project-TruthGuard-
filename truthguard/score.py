"""
M4: Reliability Scoring Module for TruthGuard
Implements equations (3) and (4) from the report:
- Claim reliability: rho(c) = P_E(c) + lambda * P_N(c), lambda in [0, 1]
- Answer reliability: R(a) = min( (1/n) * sum(rho(c_i)), 1 - max_i P_C(c_i) )
- Output counts: (n_S, n_C, n_NEI) alongside R(a)
- Support for V1 (similarity) and V3 (LLM judge) probability definitions.
"""

from typing import List, Dict, Any, Tuple


class ReliabilityScorer:
    def __init__(
        self,
        lambda_nei: float = 0.5,
        scoring_strategy: str = "non_compensatory_linear",
        tau_c: float = 0.70,
        contradiction_cap: float = 0.15
    ):
        """
        lambda_nei: Partial credit weight for unverifiable (NEI) claims in [0, 1].
        scoring_strategy:
            - 'non_compensatory_linear': R(a) = min(mean(rho), 1 - max(P_C))
            - 'non_compensatory_step': if max(P_C) >= tau_c then min(mean(rho), 0.15) else mean(rho)
            - 'average_only': R(a) = mean(rho) (linear baseline)
        """
        self.lambda_nei = lambda_nei
        self.scoring_strategy = scoring_strategy
        self.tau_c = tau_c
        self.contradiction_cap = contradiction_cap

    def score_claim(self, claim_verification: Dict[str, Any]) -> float:
        """
        Calibrated Evidence-Quality Weighted Claim Reliability:
        For SUPPORTED claims:
          rho(c) = w_auth * w_rel * P_E(c) + lambda * P_N(c)
        where:
          w_auth in [0.50, 1.0] reflects institutional source authority tier
          w_rel in [0.50, 1.0] reflects evidence relevance score
        For CONTRADICTED or NEI claims:
          rho(c) = P_E(c) + lambda * P_N(c)
        """
        p_e = claim_verification.get("p_e", 0.0)
        p_n = claim_verification.get("p_n", 0.0)
        label = claim_verification.get("label", "NEI")

        if label == "SUPPORTED":
            # Extract authority weight
            best_ev_item = claim_verification.get("best_evidence_item")
            if not best_ev_item and claim_verification.get("evidence_items"):
                best_ev_item = claim_verification["evidence_items"][0]

            w_auth = 0.95
            w_rel = 1.0

            if best_ev_item and isinstance(best_ev_item, dict):
                tier = best_ev_item.get("authority_tier", 1)
                tier_weights = {1: 1.0, 2: 0.95, 3: 0.90, 4: 0.80, 5: 0.65}
                w_auth = tier_weights.get(tier, 0.95)

                rel = best_ev_item.get("relevance_score") or best_ev_item.get("score")
                if rel is not None:
                    try:
                        raw_rel = min(max(float(rel), 0.0), 1.0)
                        w_rel = 0.85 + (0.15 * raw_rel)
                    except (ValueError, TypeError):
                        w_rel = 1.0
            elif claim_verification.get("math_evaluation", {}).get("is_math"):
                w_auth = 1.0
                w_rel = 1.0

            rho = (w_auth * w_rel * p_e) + (self.lambda_nei * p_n)
        else:
            rho = p_e + (self.lambda_nei * p_n)

        return float(min(max(rho, 0.0), 1.0))

    def score_answer(self, verified_claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates overall answer reliability using configured non-compensatory strategy,
        aggregates counts, and generates transparent rationale explanations.
        """
        if not verified_claims:
            return {
                "reliability_score": 1.0,
                "mean_rho": 1.0,
                "max_p_c": 0.0,
                "strategy_used": self.scoring_strategy,
                "counts": {"n_S": 0, "n_C": 0, "n_NEI": 0},
                "claim_reliabilities": [],
                "explanation": "No factual claims submitted for verification."
            }

        n_s = 0
        n_c = 0
        n_nei = 0

        rhos = []
        p_c_list = []
        contradicted_claims = []

        for c in verified_claims:
            lbl = c.get("label", "NEI")
            if lbl == "SUPPORTED":
                n_s += 1
            elif lbl == "CONTRADICTED":
                n_c += 1
                contradicted_claims.append(c.get("claim", ""))
            else:
                n_nei += 1

            rho_i = self.score_claim(c)
            rhos.append(rho_i)
            p_c_list.append(c.get("p_c", 0.0))

        mean_rho = float(sum(rhos) / len(rhos))
        max_p_c = float(max(p_c_list)) if p_c_list else 0.0
        # Calculate mean model confidence across claims: (1/n) * sum(max(p_e, p_c, p_n))
        conf_list = [float(max(c.get("p_e", 0.0), c.get("p_c", 0.0), c.get("p_n", 0.0))) for c in verified_claims]
        mean_confidence = float(sum(conf_list) / len(conf_list)) if conf_list else 1.0

        # Calculate score according to strategy
        if self.scoring_strategy == "non_compensatory_step":
            if max_p_c >= self.tau_c:
                r_a = min(mean_rho, self.contradiction_cap)
                is_capped = True
            else:
                r_a = mean_rho
                is_capped = False
        elif self.scoring_strategy == "average_only":
            r_a = mean_rho
            is_capped = False
        else:
            # Default: non_compensatory_linear
            linear_cap = 1.0 - max_p_c
            r_a = min(mean_rho, linear_cap)
            is_capped = (r_a < mean_rho)

        r_a = float(min(max(r_a, 0.0), 1.0))

        # Generate human-readable explanation
        explanation = self.generate_explanation(
            r_a=r_a,
            mean_rho=mean_rho,
            max_p_c=max_p_c,
            n_s=n_s,
            n_c=n_c,
            n_nei=n_nei,
            contradicted_claims=contradicted_claims,
            is_capped=is_capped
        )

        # Calculate secondary investigation & coverage metrics
        total_n = len(verified_claims)
        support_rate = float(n_s / total_n) if total_n > 0 else 0.0
        contradiction_rate = float(n_c / total_n) if total_n > 0 else 0.0
        verification_coverage = float((n_s + n_c) / total_n) if total_n > 0 else 0.0
        unverified_rate = float(n_nei / total_n) if total_n > 0 else 0.0

        ev_quality_scores = []
        for c in verified_claims:
            for item in c.get("evidence_items", []):
                tier = item.get("authority_tier", 4)
                tier_weights = {1: 1.0, 2: 0.95, 3: 0.85, 4: 0.70, 5: 0.50}
                ev_quality_scores.append(tier_weights.get(tier, 0.70))
        evidence_quality = float(sum(ev_quality_scores) / len(ev_quality_scores)) if ev_quality_scores else 0.85

        return {
            "reliability_score": r_a,
            "mean_rho": mean_rho,
            "mean_confidence": mean_confidence,
            "max_p_c": max_p_c,
            "is_capped": is_capped,
            "strategy_used": self.scoring_strategy,
            "counts": {
                "n_S": n_s,
                "n_C": n_c,
                "n_NEI": n_nei
            },
            "support_rate": support_rate,
            "evidence_backed_support_rate": support_rate,
            "contradiction_rate": contradiction_rate,
            "verification_coverage": verification_coverage,
            "unverified_rate": unverified_rate,
            "evidence_quality": evidence_quality,
            "claim_reliabilities": rhos,
            "explanation": explanation,
            "formula_tooltip": (
                "R(A) = min(mean(rho), 1 - max(P_C)), where claim reliability rho(c) = P_E(c) + lambda * P_N(c). "
                "Supported claims contribute positively, unverified (NEI) claims provide partial neutral credit (representing uncertainty), "
                "and any contradicted claim imposes a strict non-compensatory upper bound (1 - max(P_C)). "
                "Note: Individual claim scores (P_E, P_C, P_N) represent calibrated NLI model confidence estimates, "
                "and R(A) is an explainable composite reliability metric [0.0 - 1.0], not an uncalibrated frequentist probability."
            )
        }

    def generate_explanation(
        self,
        r_a: float,
        mean_rho: float,
        max_p_c: float,
        n_s: int,
        n_c: int,
        n_nei: int,
        contradicted_claims: List[str],
        is_capped: bool
    ) -> str:
        """Constructs an explainable natural language rationale for the reliability score."""
        score_pct = f"{r_a * 100:.1f}%"
        total = n_s + n_c + n_nei

        if n_c > 0:
            examples = f'"{contradicted_claims[0]}"' if contradicted_claims else "contradicted claim"
            if len(contradicted_claims) > 1:
                examples += f" and {len(contradicted_claims) - 1} other statement(s)"
            
            capping_note = (
                f" The non-compensatory penalty clamped the score from {mean_rho * 100:.1f}% to {score_pct} "
                f"because factual accuracy cannot be averaged out when direct falsehoods exist (max P_C={max_p_c * 100:.0f}%)."
                if is_capped else ""
            )
            return (
                f"Answer Reliability is {score_pct} ({n_s} supported, {n_c} contradicted, {n_nei} unverified). "
                f"Critical contradiction detected in: {examples}.{capping_note}"
            )
        elif n_nei > 0 and n_s > 0:
            return (
                f"Answer Reliability is {score_pct} ({n_s} supported, {n_nei} unverified). "
                f"All verifiable statements are grounded in evidence, with {n_nei} claim(s) lacking conclusive verification."
            )
        elif n_s == total:
            return (
                f"Answer Reliability is {score_pct}. All {total} atomic factual claims are fully supported by trusted evidence."
            )
        else:
            return (
                f"Answer Reliability is {score_pct}. Insufficient external evidence retrieved to establish factual veracity."
            )

    @staticmethod
    def tune_lambda(
        dev_samples: List[Dict[str, Any]],
        lambda_candidates: List[float] = [0.0, 0.25, 0.5]
    ) -> float:
        """
        Tunes lambda on development data by maximizing rank correlation or minimizing MSE
        against human or gold answer correctness fraction.
        """
        best_lambda = 0.5
        best_loss = float("inf")

        for lam in lambda_candidates:
            scorer = ReliabilityScorer(lambda_nei=lam)
            total_loss = 0.0
            for sample in dev_samples:
                res = scorer.score_answer(sample["verified_claims"])
                gold_score = sample.get("gold_reliability", 1.0)
                total_loss += (res["reliability_score"] - gold_score) ** 2
            
            mse = total_loss / max(len(dev_samples), 1)
            if mse < best_loss:
                best_loss = mse
                best_lambda = lam

        return best_lambda
