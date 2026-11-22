"""
TruthGuard Experiment Execution Runner (Phase 7)
Executes all benchmark configurations:
- T1 (BM25 + Similarity V1)
- T2 (BM25 + NLI V2)
- N1 (SBERT + NLI V2)
- N2 (Hybrid + Re-ranker + NLI V2 - Full TruthGuard)
- N3 (Hybrid + Re-ranker + LLM Judge V3)
- R1 (SelfCheckGPT-NLI)
- AlignScore
- Decomposition ablations (sentence vs rule-based vs LLM atomic with N2)

Evaluates on FEVER, HaluEval-QA, and RAGTruth across 3 random seeds [42, 123, 999].
Saves results/<config>/<dataset>/<seed>/ predictions, metrics, and generates results/summary.csv.
"""

import os
import json
import time
import subprocess
import yaml
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, precision_recall_curve, auc

from truthguard.pipeline import TruthGuardPipeline
from baselines.selfcheckgpt_wrapper import SelfCheckGPTNLI
from baselines.alignscore_wrapper import AlignScoreWrapper

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def get_git_commit() -> str:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
        return commit
    except Exception:
        return "git_commit_dev"


def compute_span_overlap(gold_spans: List[Dict], pred_spans: List[Dict], text_len: int) -> Tuple[float, float, float]:
    """Computes character-level precision, recall, and F1 between predicted and gold spans."""
    gold_mask = np.zeros(text_len, dtype=bool)
    pred_mask = np.zeros(text_len, dtype=bool)

    for g in gold_spans:
        s, e = g.get("start", 0), g.get("end", text_len)
        gold_mask[s:e] = True

    for p in pred_spans:
        s, e = p.get("char_start", 0), p.get("char_end", text_len)
        pred_mask[s:e] = True

    intersection = np.sum(gold_mask & pred_mask)
    gold_total = np.sum(gold_mask)
    pred_total = np.sum(pred_mask)

    if pred_total == 0 and gold_total == 0:
        return 1.0, 1.0, 1.0
    if pred_total == 0 or gold_total == 0:
        return 0.0, 0.0, 0.0

    prec = intersection / pred_total
    rec = intersection / gold_total
    f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    return float(prec), float(rec), float(f1)


def load_dataset(name: str) -> List[Dict]:
    path = os.path.join(DATA_DIR, f"{name}_eval.jsonl")
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def run_experiment_config(
    config_name: str,
    decomp_method: str = "atomic_llm",
    retrieval_mode: str = "hybrid",
    verifier_type: str = "nli",
    baseline_type: Optional[str] = None,
    seeds: List[int] = [42, 123, 999]
):
    print(f"\n================================================================================")
    print(f"RUNNING CONFIGURATION: {config_name}")
    print(f"Decomp: {decomp_method} | Retrieval: {retrieval_mode} | Verifier: {verifier_type} | Baseline: {baseline_type}")
    print(f"================================================================================")

    fever_data = load_dataset("fever")
    halueval_data = load_dataset("halueval")
    ragtruth_data = load_dataset("ragtruth")
    git_hash = get_git_commit()

    all_summary_rows = []

    for seed in seeds:
        np.random.seed(seed)
        print(f"\n>>> Executing Seed: {seed} <<<")

        # ----------------------------------------------------
        # 1. FEVER Evaluation
        # ----------------------------------------------------
        fever_pred_dir = os.path.join(RESULTS_DIR, config_name, "FEVER", str(seed))
        os.makedirs(fever_pred_dir, exist_ok=True)

        if baseline_type is None:
            pipeline = TruthGuardPipeline(
                decomposition_method=decomp_method,
                retrieval_mode=retrieval_mode,
                verifier_type=verifier_type
            )
            fever_preds = []
            gold_labels = []
            pred_labels = []
            fever_scores = []
            r5_hits = []

            for item in fever_data:
                gold_lbl = item["label"]
                gold_labels.append(gold_lbl)
                claim = item["claim"]
                context_sents = item["context_sentences"]
                gold_ev = set(item.get("gold_evidence", []))

                t0 = time.time()
                # Run retrieval
                retrieval = pipeline.retriever.retrieve_for_claim(claim, context_sents)
                retrieved_sents = retrieval["sentences"]

                # Check Recall@5 for evidence
                r5_hit = False
                if gold_ev:
                    r5_hit = any(ev in retrieved_sents[:5] for ev in gold_ev)
                    r5_hits.append(r5_hit)

                # Run verification
                verif = pipeline.verifier.verify_claim(claim, retrieved_sents)
                pred_lbl = verif["label"]
                # Map label format: SUPPORTED -> SUPPORTS, CONTRADICTED -> REFUTES, NEI -> NOT ENOUGH INFO
                fever_mapped_lbl = "SUPPORTS" if pred_lbl == "SUPPORTED" else ("REFUTES" if pred_lbl == "CONTRADICTED" else "NOT ENOUGH INFO")
                pred_labels.append(fever_mapped_lbl)

                # FEVER score: correct label AND (if S/R) gold evidence retrieved
                is_correct_label = (fever_mapped_lbl == gold_lbl)
                if gold_lbl in ("SUPPORTS", "REFUTES"):
                    f_score = is_correct_label and r5_hit
                else:
                    f_score = is_correct_label
                fever_scores.append(f_score)

                fever_preds.append({
                    "id": item["id"],
                    "claim": claim,
                    "gold_label": gold_lbl,
                    "pred_label": fever_mapped_lbl,
                    "is_correct": is_correct_label,
                    "fever_score": f_score,
                    "p_e": verif["p_e"],
                    "p_c": verif["p_c"],
                    "p_n": verif["p_n"]
                })

            fever_la = accuracy_score(gold_labels, pred_labels)
            fever_macro_f1 = f1_score(gold_labels, pred_labels, average="macro", zero_division=0)
            per_class_f1 = f1_score(gold_labels, pred_labels, labels=["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"], average=None, zero_division=0)
            f1_nei = per_class_f1[2]
            fever_acc_score = np.mean(fever_scores)
            recall_at_5 = np.mean(r5_hits) if r5_hits else 1.0

            fever_metrics = {
                "Recall@5": float(recall_at_5),
                "Label_Accuracy": float(fever_la),
                "Macro_F1": float(fever_macro_f1),
                "FEVER_Score": float(fever_acc_score),
                "F1_NEI": float(f1_nei),
                "F1_SUPPORTS": float(per_class_f1[0]),
                "F1_REFUTES": float(per_class_f1[1]),
                "git_commit": git_hash
            }

            with open(os.path.join(fever_pred_dir, "predictions.jsonl"), "w") as f:
                for p in fever_preds:
                    f.write(json.dumps(p) + "\n")
            with open(os.path.join(fever_pred_dir, "metrics.json"), "w") as f:
                json.dump(fever_metrics, f, indent=2)

            all_summary_rows.append({
                "config": config_name,
                "dataset": "FEVER",
                "seed": seed,
                "Recall@5": fever_metrics["Recall@5"],
                "Label_Accuracy": fever_metrics["Label_Accuracy"],
                "Macro_F1": fever_metrics["Macro_F1"],
                "FEVER_Score": fever_metrics["FEVER_Score"],
                "F1_NEI": fever_metrics["F1_NEI"],
                "Response_F1": None,
                "AUROC": None,
                "Span_F1": None
            })
            print(f"  [FEVER] LA: {fever_la*100:.1f}% | Macro-F1: {fever_macro_f1:.3f} | FEVER: {fever_acc_score*100:.1f}% | R@5: {recall_at_5*100:.1f}%")

        # ----------------------------------------------------
        # 2. HaluEval-QA Evaluation
        # ----------------------------------------------------
        halu_pred_dir = os.path.join(RESULTS_DIR, config_name, "HaluEval-QA", str(seed))
        os.makedirs(halu_pred_dir, exist_ok=True)

        halu_preds = []
        halu_gold = []
        halu_scores = []
        halu_binary_preds = []

        for item in halueval_data:
            gold = item["is_hallucinated"]
            halu_gold.append(gold)
            resp = item["response"]
            ctx = item["knowledge"]

            if baseline_type == "selfcheckgpt_nli":
                sc = SelfCheckGPTNLI(num_samples=20)
                res = sc.score_response([resp], [ctx])
                score = res["response_score"]
                pred = int(score >= 0.5)
            elif baseline_type == "alignscore":
                asc = AlignScoreWrapper()
                res = asc.score_response([resp], ctx)
                score = res["hallucination_score"]
                pred = int(score >= 0.5)
            else:
                p_res = pipeline.run(resp, rag_context=ctx)
                score = 1.0 - p_res["reliability_score"]
                # Rule: flag hallucinated if any claim is Contradicted
                pred = 1 if p_res["counts"]["n_C"] > 0 else 0

            halu_scores.append(score)
            halu_binary_preds.append(pred)
            halu_preds.append({
                "id": item["id"],
                "gold": gold,
                "pred": pred,
                "hallucination_score": score
            })

        halu_f1 = f1_score(halu_gold, halu_binary_preds, zero_division=0)
        try:
            halu_auroc = roc_auc_score(halu_gold, halu_scores)
        except Exception:
            halu_auroc = 0.5

        halu_metrics = {
            "Response_F1": float(halu_f1),
            "AUROC": float(halu_auroc),
            "git_commit": git_hash
        }

        with open(os.path.join(halu_pred_dir, "predictions.jsonl"), "w") as f:
            for p in halu_preds:
                f.write(json.dumps(p) + "\n")
        with open(os.path.join(halu_pred_dir, "metrics.json"), "w") as f:
            json.dump(halu_metrics, f, indent=2)

        all_summary_rows.append({
            "config": config_name,
            "dataset": "HaluEval-QA",
            "seed": seed,
            "Recall@5": None,
            "Label_Accuracy": None,
            "Macro_F1": None,
            "FEVER_Score": None,
            "F1_NEI": None,
            "Response_F1": halu_f1,
            "AUROC": halu_auroc,
            "Span_F1": None
        })
        print(f"  [HaluEval-QA] F1: {halu_f1:.3f} | AUROC: {halu_auroc:.3f}")

        # ----------------------------------------------------
        # 3. RAGTruth Evaluation (Response & Span Level)
        # ----------------------------------------------------
        ragtruth_pred_dir = os.path.join(RESULTS_DIR, config_name, "RAGTruth", str(seed))
        os.makedirs(ragtruth_pred_dir, exist_ok=True)

        rag_preds = []
        rag_gold_resp = []
        rag_pred_resp = []
        rag_scores = []
        span_f1s = []

        for item in ragtruth_data:
            gold_r = item["is_hallucinated"]
            rag_gold_resp.append(gold_r)
            resp = item["response"]
            ctx = item["context"]
            gold_spans = item.get("gold_spans", [])

            if baseline_type == "selfcheckgpt_nli":
                sc = SelfCheckGPTNLI(num_samples=20)
                res = sc.score_response([resp], [ctx])
                score = res["response_score"]
                pred_r = int(score >= 0.5)
                pred_spans = []
            elif baseline_type == "alignscore":
                asc = AlignScoreWrapper()
                res = asc.score_response([resp], ctx)
                score = res["hallucination_score"]
                pred_r = int(score >= 0.5)
                pred_spans = []
            else:
                p_res = pipeline.run(resp, rag_context=ctx)
                score = 1.0 - p_res["reliability_score"]
                pred_r = 1 if p_res["counts"]["n_C"] > 0 else 0
                pred_spans = []
                for c in p_res["claims"]:
                    pred_spans.extend(c.get("error_spans", []))

            rag_scores.append(score)
            rag_pred_resp.append(pred_r)

            # Compute span-level F1
            _, _, s_f1 = compute_span_overlap(gold_spans, pred_spans, len(resp))
            span_f1s.append(s_f1)

            rag_preds.append({
                "id": item["id"],
                "task_type": item["task_type"],
                "gold_response": gold_r,
                "pred_response": pred_r,
                "hallucination_score": score,
                "span_f1": s_f1
            })

        rag_resp_f1 = f1_score(rag_gold_resp, rag_pred_resp, zero_division=0)
        mean_span_f1 = float(np.mean(span_f1s))
        try:
            rag_auroc = roc_auc_score(rag_gold_resp, rag_scores)
        except Exception:
            rag_auroc = 0.5

        rag_metrics = {
            "Response_F1": float(rag_resp_f1),
            "Span_F1": mean_span_f1,
            "AUROC": float(rag_auroc),
            "git_commit": git_hash
        }

        with open(os.path.join(ragtruth_pred_dir, "predictions.jsonl"), "w") as f:
            for p in rag_preds:
                f.write(json.dumps(p) + "\n")
        with open(os.path.join(ragtruth_pred_dir, "metrics.json"), "w") as f:
            json.dump(rag_metrics, f, indent=2)

        all_summary_rows.append({
            "config": config_name,
            "dataset": "RAGTruth",
            "seed": seed,
            "Recall@5": None,
            "Label_Accuracy": None,
            "Macro_F1": None,
            "FEVER_Score": None,
            "F1_NEI": None,
            "Response_F1": rag_resp_f1,
            "AUROC": rag_auroc,
            "Span_F1": mean_span_f1
        })
        print(f"  [RAGTruth] Resp F1: {rag_resp_f1:.3f} | Span F1: {mean_span_f1:.3f} | AUROC: {rag_auroc:.3f}")

    return all_summary_rows


def run_all_benchmarks():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    summary_path = os.path.join(RESULTS_DIR, "summary.csv")
    all_rows = []

    configs = [
        # Main configurations from report
        {"name": "T1", "decomp": "atomic_llm", "retr": "bm25", "verif": "similarity"},
        {"name": "T2", "decomp": "atomic_llm", "retr": "bm25", "verif": "nli"},
        {"name": "N1", "decomp": "atomic_llm", "retr": "dense_sbert", "verif": "nli"},
        {"name": "N2", "decomp": "atomic_llm", "retr": "hybrid", "verif": "nli"},
        {"name": "N3", "decomp": "atomic_llm", "retr": "hybrid", "verif": "llm_judge"},
        # External baselines
        {"name": "R1_SelfCheckGPT", "baseline": "selfcheckgpt_nli"},
        {"name": "AlignScore", "baseline": "alignscore"},
        # Decomposition ablations (paired with N2)
        {"name": "TG_sentence_split", "decomp": "sentence_split", "retr": "hybrid", "verif": "nli"},
        {"name": "TG_rule_based", "decomp": "rule_based", "retr": "hybrid", "verif": "nli"}
    ]

    for cfg in configs:
        rows = run_experiment_config(
            config_name=cfg["name"],
            decomp_method=cfg.get("decomp", "atomic_llm"),
            retrieval_mode=cfg.get("retr", "hybrid"),
            verifier_type=cfg.get("verif", "nli"),
            baseline_type=cfg.get("baseline", None),
            seeds=[42, 123, 999]
        )
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df.to_csv(summary_path, index=False)
    print(f"\n================================================================================")
    print(f"ALL EXPERIMENTS EXECUTED! Summary successfully written to {summary_path}")
    print(f"================================================================================")


if __name__ == "__main__":
    run_all_benchmarks()
