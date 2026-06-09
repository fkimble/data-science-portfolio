"""Data-quality checks for synthetic claimflow workflows."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS = {
    "encounter_id",
    "patient_segment",
    "region",
    "payer",
    "service_line",
    "request_date",
    "decision_date",
    "claim_date",
    "finalized_date",
    "auth_status",
    "claim_status",
    "denial_reason",
    "appealed",
    "overturned",
    "documentation_score",
    "expected_reimbursement",
}


@dataclass(frozen=True)
class ValidationResult:
    """Structured validation result."""

    passed: bool
    errors: list[str]


def validate_claimflows(df: pd.DataFrame) -> ValidationResult:
    """Validate workflow shape and basic temporal/business rules."""

    errors: list[str] = []
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        errors.append(f"missing required columns: {', '.join(missing)}")
        return ValidationResult(False, errors)

    if df["encounter_id"].duplicated().any():
        errors.append("encounter_id must be unique")

    for col in ["request_date", "decision_date", "claim_date", "finalized_date"]:
        parsed = pd.to_datetime(df[col], errors="coerce")
        if parsed.isna().any():
            errors.append(f"{col} contains invalid dates")

    req = pd.to_datetime(df["request_date"], errors="coerce")
    decision = pd.to_datetime(df["decision_date"], errors="coerce")
    claim = pd.to_datetime(df["claim_date"], errors="coerce")
    final = pd.to_datetime(df["finalized_date"], errors="coerce")
    if (decision < req).any() or (claim < decision).any() or (final < claim).any():
        errors.append("workflow dates must be ordered request <= decision <= claim <= finalized")

    if not df["claim_status"].isin(["paid", "denied"]).all():
        errors.append("claim_status must be paid or denied")

    paid_with_reason = df["claim_status"].eq("paid") & ~df["denial_reason"].eq("none")
    denied_without_reason = df["claim_status"].eq("denied") & df["denial_reason"].eq("none")
    if paid_with_reason.any() or denied_without_reason.any():
        errors.append("denial_reason must be none only for paid claims and populated for denied claims")

    if df["overturned"].astype(bool).any() and (df["overturned"].astype(bool) & ~df["appealed"].astype(bool)).any():
        errors.append("overturned claims must also be appealed")

    if df["documentation_score"].lt(0).any() or df["documentation_score"].gt(100).any():
        errors.append("documentation_score must be between 0 and 100")

    if df["expected_reimbursement"].le(0).any():
        errors.append("expected_reimbursement must be positive")

    return ValidationResult(not errors, errors)


def require_valid(df: pd.DataFrame) -> None:
    """Raise ValueError if workflows fail validation."""

    result = validate_claimflows(df)
    if not result.passed:
        raise ValueError("; ".join(result.errors))
