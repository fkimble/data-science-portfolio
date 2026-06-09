"""Access metrics for specialty-referral workflows."""

from __future__ import annotations

import pandas as pd


def metric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute portfolio-level referral access metrics."""

    leaked = df["referral_leaked"].astype(bool)
    no_show = df["no_show"].astype(bool)
    completed = df["completed"].astype(bool)
    scheduled_not_leaked = ~leaked
    long_wait = df["wait_days"].gt(30)
    rows = [
        ("referral_volume", len(df), "all specialty referrals"),
        ("completion_rate", completed.mean(), "completed appointments / all referrals"),
        ("leakage_rate", leaked.mean(), "leaked referrals / all referrals"),
        ("no_show_rate", (scheduled_not_leaked & no_show).sum() / max(scheduled_not_leaked.sum(), 1), "no-shows / non-leaked scheduled referrals"),
        ("median_wait_days", df["wait_days"].median(), "median referral-to-appointment wait"),
        ("long_wait_share", long_wait.mean(), "referrals waiting more than 30 days"),
        ("deferred_visit_value", df.loc[leaked | no_show | long_wait, "expected_visit_value"].sum(), "expected value tied to leaked/no-show/long-wait referrals"),
    ]
    return pd.DataFrame(rows, columns=["metric", "value", "definition"])


def access_rates(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """Compute access rates by grouping dimensions."""

    d = df.copy()
    grouped = (
        d.groupby(by, dropna=False)
        .agg(
            referrals=("referral_id", "count"),
            completed=("completed", "sum"),
            leaked=("referral_leaked", "sum"),
            no_shows=("no_show", "sum"),
            median_wait_days=("wait_days", "median"),
            p90_wait_days=("wait_days", lambda s: s.quantile(0.9)),
            avg_capacity_score=("capacity_score", "mean"),
            avg_need_index=("community_need_index", "mean"),
            deferred_visit_value=("expected_visit_value", lambda s: s[d.loc[s.index, "completion_status"].isin(["leaked", "no-show"])].sum()),
        )
        .reset_index()
    )
    grouped["completion_rate"] = grouped["completed"] / grouped["referrals"]
    grouped["leakage_rate"] = grouped["leaked"] / grouped["referrals"]
    grouped["no_show_rate"] = grouped["no_shows"] / grouped["referrals"]
    return grouped.sort_values(["leakage_rate", "median_wait_days", "referrals"], ascending=[False, False, False]).reset_index(drop=True)


def drift_table(df: pd.DataFrame, by: list[str], recent_days: int = 45) -> pd.DataFrame:
    """Compare recent and baseline leakage/wait performance by cohort."""

    d = df.copy()
    d["referral_date"] = pd.to_datetime(d["referral_date"])
    cutoff = d["referral_date"].max() - pd.Timedelta(days=recent_days)
    d["window"] = d["referral_date"].ge(cutoff).map({True: "recent", False: "baseline"})
    grouped = (
        d.groupby(by + ["window"])
        .agg(referrals=("referral_id", "count"), leakage_rate=("referral_leaked", "mean"), median_wait_days=("wait_days", "median"))
        .reset_index()
    )
    pivot = grouped.pivot(index=by, columns="window", values=["referrals", "leakage_rate", "median_wait_days"]).fillna(0)
    pivot.columns = ["_".join(col).strip("_") for col in pivot.columns.to_flat_index()]
    out = pivot.reset_index()
    for col in [
        "referrals_baseline",
        "referrals_recent",
        "leakage_rate_baseline",
        "leakage_rate_recent",
        "median_wait_days_baseline",
        "median_wait_days_recent",
    ]:
        if col not in out:
            out[col] = 0
    out["leakage_drift_delta"] = out["leakage_rate_recent"] - out["leakage_rate_baseline"]
    out["wait_drift_days"] = out["median_wait_days_recent"] - out["median_wait_days_baseline"]
    return out.sort_values(["leakage_drift_delta", "wait_drift_days", "referrals_recent"], ascending=[False, False, False]).reset_index(drop=True)


def intervention_backlog(df: pd.DataFrame) -> pd.DataFrame:
    """Rank access interventions by impacted value and confidence."""

    d = df.copy()
    candidates = [
        ("wait too long", "Open specialty fast-track slots for long-wait referrals", 0.68),
        ("no local capacity", "Create regional capacity-sharing queue for scarce specialties", 0.62),
        ("payer network mismatch", "Negotiate network exception pathway for high-leakage payers", 0.58),
        ("authorization friction", "Add pre-visit authorization workqueue and SLA tracker", 0.55),
        ("no-show", "Launch high-need reminder and transportation outreach workflow", 0.52),
    ]
    rows = []
    for reason, intervention, confidence in candidates:
        if reason == "no-show":
            subset = d[d["completion_status"].eq("no-show")]
        else:
            subset = d[d["leakage_reason"].eq(reason)]
        value = float(subset["expected_visit_value"].sum())
        rows.append(
            {
                "intervention": intervention,
                "target_issue": reason,
                "affected_referrals": int(len(subset)),
                "expected_visit_value_at_risk": round(value, 2),
                "confidence_weight": confidence,
                "impact_score": round(value * confidence, 2),
            }
        )
    return pd.DataFrame(rows).sort_values("impact_score", ascending=False).reset_index(drop=True)
