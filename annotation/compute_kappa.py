"""
TruthGuard-100 Tooling: Cohen's Kappa Inter-Annotator Agreement & Gold Adjudication
Calculates Cohen's kappa between annotator 1 and annotator 2 on TruthGuard-100,
flags disagreements for author resolution, and outputs adjudicated gold labels.
"""

import os
import csv
import pandas as pd
from sklearn.metrics import cohen_kappa_score


def compute_agreement(csv_path: str = "annotation/truthguard_100_unannotated.csv"):
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)

    # Check if annotations are present
    labels1 = df["label_annotator1"].dropna().astype(str).str.strip().str.upper()
    labels2 = df["label_annotator2"].dropna().astype(str).str.strip().str.upper()

    if len(labels1) == 0 or len(labels2) == 0:
        print("[Notice] Annotation sheet has not been filled by human annotators yet.")
        print(f"Please fill 'label_annotator1' and 'label_annotator2' in {csv_path} per GUIDELINES.md.")
        return

    # Filter to rows where both annotators provided labels
    valid_mask = (df["label_annotator1"].astype(str).str.strip() != "") & (df["label_annotator2"].astype(str).str.strip() != "")
    valid_df = df[valid_mask]

    if len(valid_df) == 0:
        print("[Notice] No overlapping annotated rows found.")
        return

    a1 = valid_df["label_annotator1"].str.strip().str.upper().tolist()
    a2 = valid_df["label_annotator2"].str.strip().str.upper().tolist()

    kappa = cohen_kappa_score(a1, a2)
    print("=" * 80)
    print("TRUTHGUARD-100 INTER-ANNOTATOR AGREEMENT REPORT")
    print("=" * 80)
    print(f"Total Evaluated Claims: {len(valid_df)}")
    print(f"Cohen's Kappa (kappa):  {kappa:.4f}")

    # Agreement categories
    if kappa > 0.8:
        strength = "Almost Perfect Agreement"
    elif kappa > 0.6:
        strength = "Substantial Agreement"
    elif kappa > 0.4:
        strength = "Moderate Agreement"
    else:
        strength = "Fair to Poor Agreement"
    print(f"Interpretation:         {strength}")

    # Identify disagreements
    disagreements = valid_df[valid_df["label_annotator1"].str.strip().str.upper() != valid_df["label_annotator2"].str.strip().str.upper()]
    print(f"\nDisagreements Found:    {len(disagreements)} / {len(valid_df)} ({len(disagreements)/len(valid_df)*100:.1f}%)")

    disagree_out = os.path.join(os.path.dirname(csv_path), "disagreements_for_adjudication.csv")
    disagreements.to_csv(disagree_out, index=False)
    print(f"Saved disagreements to: {disagree_out}")
    print("=" * 80)


if __name__ == "__main__":
    compute_agreement()
