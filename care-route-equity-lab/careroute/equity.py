"""Equity-gap analytics for specialty-referral workflows."""

from __future__ import annotations

import pandas as pd


def equity_gap_table(df: pd.DataFrame, dimensions: list[str]) -> pd.DataFrame:
    """Compute access gaps versus portfolio-average leakage and wait time."""

    overall_leakage = df["referral_leaked"].mean()
    overall_wait = df["wait_days"].median()
    grouped = (
        df.groupby(dimensions)
        .agg(
            referrals=("referral_id", "count"),
            leakage_rate=("referral_leaked", "mean"),
            completion_rate=("completed", "mean"),
            median_wait_days=("wait_days", "median"),
            avg_need_index=("community_need_index", "mean"),
            avg_capacity_score=("capacity_score", "mean"),
            avg_expected_visit_value=("expected_visit_value", "mean"),
        )
        .reset_index()
    )
    grouped["leakage_gap"] = grouped["leakage_rate"] - overall_leakage
    grouped["wait_gap_days"] = grouped["median_wait_days"] - overall_wait
    grouped["excess_leaked_referrals"] = (grouped["leakage_gap"].clip(lower=0) * grouped["referrals"]).round(1)
    grouped["estimated_excess_value"] = (grouped["excess_leaked_referrals"] * grouped["avg_expected_visit_value"]).round(2)
    return grouped.sort_values(["estimated_excess_value", "wait_gap_days"], ascending=[False, False]).reset_index(drop=True)
