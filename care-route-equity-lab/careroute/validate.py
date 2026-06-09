"""Data-quality checks for specialty-referral workflows."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


REQUIRED_COLUMNS = {
    "referral_id",
    "patient_segment",
    "region",
    "payer",
    "specialty",
    "urgency",
    "referral_source",
    "referral_date",
    "authorization_required",
    "network_status",
    "capacity_score",
    "community_need_index",
    "appointment_date",
    "completion_status",
    "leakage_reason",
    "wait_days",
    "care_gap_days",
    "referral_leaked",
    "no_show",
    "completed",
    "expected_visit_value",
}


@dataclass(frozen=True)
class ValidationResult:
    """Structured validation result."""

    passed: bool
    errors: list[str]


def validate_referrals(df: pd.DataFrame) -> ValidationResult:
    """Validate referral data shape and workflow rules."""

    errors: list[str] = []
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        return ValidationResult(False, [f"missing required columns: {', '.join(missing)}"])

    if df["referral_id"].duplicated().any():
        errors.append("referral_id must be unique")

    referral_date = pd.to_datetime(df["referral_date"], errors="coerce")
    appointment_date = pd.to_datetime(df["appointment_date"], errors="coerce")
    if referral_date.isna().any() or appointment_date.isna().any():
        errors.append("referral_date and appointment_date must be valid dates")
    elif (appointment_date < referral_date).any():
        errors.append("appointment_date must be on or after referral_date")

    allowed_status = {"completed", "no-show", "cancelled", "leaked"}
    if not df["completion_status"].isin(allowed_status).all():
        errors.append("completion_status contains invalid values")

    leaked = df["referral_leaked"].astype(bool)
    if not df.loc[leaked, "completion_status"].eq("leaked").all():
        errors.append("referral_leaked rows must have completion_status leaked")
    if not df.loc[~leaked, "leakage_reason"].eq("none").all():
        errors.append("non-leaked rows must have leakage_reason none")

    no_show = df["no_show"].astype(bool)
    if not df.loc[no_show, "completion_status"].eq("no-show").all():
        errors.append("no_show rows must have completion_status no-show")

    completed = df["completed"].astype(bool)
    if not df.loc[completed, "completion_status"].eq("completed").all():
        errors.append("completed rows must have completion_status completed")

    if df["wait_days"].lt(0).any() or df["care_gap_days"].lt(0).any():
        errors.append("wait_days and care_gap_days must be non-negative")

    if df["capacity_score"].lt(0).any() or df["capacity_score"].gt(100).any():
        errors.append("capacity_score must be between 0 and 100")

    if df["community_need_index"].lt(0).any() or df["community_need_index"].gt(100).any():
        errors.append("community_need_index must be between 0 and 100")

    if df["expected_visit_value"].le(0).any():
        errors.append("expected_visit_value must be positive")

    return ValidationResult(not errors, errors)


def require_valid(df: pd.DataFrame) -> None:
    """Raise ValueError when referrals fail validation."""

    result = validate_referrals(df)
    if not result.passed:
        raise ValueError("; ".join(result.errors))
