"""Metric calculations for claimflow workflows."""

from __future__ import annotations

import pandas as pd


AVOIDABLE_REASONS = {"documentation", "coding", "eligibility", "timely filing"}


def add_cycle_time(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with cycle-time columns in days."""

    out = df.copy()
    out["request_date"] = pd.to_datetime(out["request_date"])
    out["finalized_date"] = pd.to_datetime(out["finalized_date"])
    out["cycle_days"] = (out["finalized_date"] - out["request_date"]).dt.days
    return out


def metric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute top-level operations metrics."""

    d = add_cycle_time(df)
    denied = d["claim_status"].eq("denied")
    appealed = d["appealed"].astype(bool)
    overturned = d["overturned"].astype(bool)
    avoidable = d["denial_reason"].isin(AVOIDABLE_REASONS)
    rows = [
        ("claim_volume", len(d), "completed authorization-to-claim workflows"),
        ("denial_rate", denied.mean(), "denied claims / all claims"),
        ("avoidable_denial_share", (denied & avoidable).sum() / max(denied.sum(), 1), "avoidable denials / denied claims"),
        ("appeal_rate", (denied & appealed).sum() / max(denied.sum(), 1), "appealed denials / denied claims"),
        ("overturn_rate", (appealed & overturned).sum() / max(appealed.sum(), 1), "overturned appeals / appealed denials"),
        ("median_cycle_days", d["cycle_days"].median(), "median days from request to finalized claim"),
        ("denied_reimbursement_at_risk", d.loc[denied, "expected_reimbursement"].sum(), "expected reimbursement attached to denied claims"),
    ]
    return pd.DataFrame(rows, columns=["metric", "value", "definition"])


def group_denial_rates(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """Compute denial rates and value at risk by grouping dimensions."""

    d = df.copy()
    d["is_denied"] = d["claim_status"].eq("denied")
    grouped = (
        d.groupby(by, dropna=False)
        .agg(
            claims=("encounter_id", "count"),
            denials=("is_denied", "sum"),
            avg_documentation_score=("documentation_score", "mean"),
            avg_expected_reimbursement=("expected_reimbursement", "mean"),
            denied_reimbursement=("expected_reimbursement", lambda s: s[d.loc[s.index, "is_denied"]].sum()),
        )
        .reset_index()
    )
    grouped["denial_rate"] = grouped["denials"] / grouped["claims"]
    return grouped.sort_values(["denial_rate", "claims"], ascending=[False, False]).reset_index(drop=True)


def drift_table(df: pd.DataFrame, by: list[str], recent_days: int = 45) -> pd.DataFrame:
    """Compare recent and baseline denial rates for the requested dimensions."""

    d = df.copy()
    d["request_date"] = pd.to_datetime(d["request_date"])
    cutoff = d["request_date"].max() - pd.Timedelta(days=recent_days)
    d["window"] = d["request_date"].ge(cutoff).map({True: "recent", False: "baseline"})
    d["is_denied"] = d["claim_status"].eq("denied")
    grouped = d.groupby(by + ["window"]).agg(claims=("encounter_id", "count"), denials=("is_denied", "sum")).reset_index()
    grouped["denial_rate"] = grouped["denials"] / grouped["claims"]
    pivot = grouped.pivot(index=by, columns="window", values=["claims", "denials", "denial_rate"]).fillna(0)
    pivot.columns = ["_".join(col).strip("_") for col in pivot.columns.to_flat_index()]
    out = pivot.reset_index()
    for col in ["claims_baseline", "claims_recent", "denials_baseline", "denials_recent", "denial_rate_baseline", "denial_rate_recent"]:
        if col not in out:
            out[col] = 0
    out["drift_delta"] = out["denial_rate_recent"] - out["denial_rate_baseline"]
    out["recent_volume"] = out["claims_recent"]
    return out.sort_values(["drift_delta", "recent_volume"], ascending=[False, False]).reset_index(drop=True)


def intervention_backlog(df: pd.DataFrame) -> pd.DataFrame:
    """Rank operational fixes by avoidable denial value."""

    d = df.copy()
    d["avoidable"] = d["claim_status"].eq("denied") & d["denial_reason"].isin(AVOIDABLE_REASONS)
    candidates = []
    for reason, confidence, fix in [
        ("documentation", 0.72, "Launch pre-submit documentation completeness checklist"),
        ("coding", 0.58, "Add coding edit rules before claim submission"),
        ("eligibility", 0.64, "Automate eligibility refresh before service date"),
        ("timely filing", 0.49, "Create aging queue for claims near filing deadline"),
    ]:
        subset = d[d["denial_reason"].eq(reason)]
        candidates.append(
            {
                "intervention": fix,
                "denial_reason": reason,
                "avoidable_denials": int(len(subset)),
                "reimbursement_at_risk": round(float(subset["expected_reimbursement"].sum()), 2),
                "confidence_weight": confidence,
                "impact_score": round(float(len(subset) * subset["expected_reimbursement"].mean() * confidence), 2) if len(subset) else 0.0,
            }
        )
    return pd.DataFrame(candidates).sort_values("impact_score", ascending=False).reset_index(drop=True)
