"""Parity-gap analytics for claimflow workflows."""

from __future__ import annotations

import pandas as pd


def parity_table(df: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    """Compute denial-rate gaps versus the population average."""

    d = df.copy()
    d["is_denied"] = d["claim_status"].eq("denied")
    overall = d["is_denied"].mean()
    grouped = (
        d.groupby(dimensions)
        .agg(
            claims=("encounter_id", "count"),
            denials=("is_denied", "sum"),
            avg_documentation_score=("documentation_score", "mean"),
            avg_expected_reimbursement=("expected_reimbursement", "mean"),
        )
        .reset_index()
    )
    grouped["denial_rate"] = grouped["denials"] / grouped["claims"]
    grouped["parity_gap"] = grouped["denial_rate"] - overall
    grouped["excess_denials_vs_average"] = (grouped["parity_gap"].clip(lower=0) * grouped["claims"]).round(1)
    grouped["estimated_excess_value"] = (grouped["excess_denials_vs_average"] * grouped["avg_expected_reimbursement"]).round(2)
    return grouped.sort_values(["estimated_excess_value", "parity_gap"], ascending=[False, False]).reset_index(drop=True)
