"""Synthetic prior-authorization and claims workflow generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


PATIENT_SEGMENTS = ["Commercial", "Medicaid", "Medicare", "Uninsured"]
REGIONS = ["Baltimore", "Capital", "Eastern Shore", "Western MD"]
PAYERS = ["Aster Health", "Blue Harbor", "CivicCare", "Meridian Choice"]
SERVICE_LINES = ["Imaging", "Cardiology", "Behavioral Health", "Orthopedics", "Oncology", "Primary Care"]
DENIAL_REASONS = ["documentation", "coding", "eligibility", "medical necessity", "timely filing", "none"]


@dataclass(frozen=True)
class GeneratorConfig:
    """Configuration for synthetic claimflow rows."""

    patients: int = 5000
    days: int = 180
    seed: int = 42
    start: date = date(2025, 1, 1)


def _choice(rng: np.random.Generator, values: list[str], size: int, p: list[float] | None = None) -> np.ndarray:
    return rng.choice(values, size=size, p=p)


def generate_claimflows(config: GeneratorConfig) -> pd.DataFrame:
    """Generate completed prior-authorization and claims workflows.

    The generator intentionally creates a recent denial-rate shift for Meridian
    Choice behavioral-health claims with lower documentation scores. This gives
    the drift detector a meaningful pattern to catch while staying fully
    synthetic and reproducible.
    """

    rng = np.random.default_rng(config.seed)
    n = config.patients
    offsets = rng.integers(0, config.days, size=n)
    request_dates = pd.to_datetime([config.start + timedelta(days=int(x)) for x in offsets])

    df = pd.DataFrame(
        {
            "encounter_id": [f"CF-{config.seed}-{i:06d}" for i in range(n)],
            "patient_segment": _choice(rng, PATIENT_SEGMENTS, n, [0.44, 0.24, 0.24, 0.08]),
            "region": _choice(rng, REGIONS, n, [0.42, 0.28, 0.18, 0.12]),
            "payer": _choice(rng, PAYERS, n, [0.32, 0.27, 0.24, 0.17]),
            "service_line": _choice(rng, SERVICE_LINES, n, [0.22, 0.16, 0.15, 0.17, 0.10, 0.20]),
            "request_date": request_dates,
        }
    )

    doc_base = rng.normal(78, 12, n)
    doc_base -= np.where(df["patient_segment"].eq("Medicaid"), rng.normal(6, 3, n), 0)
    doc_base -= np.where(df["service_line"].eq("Behavioral Health"), rng.normal(4, 2, n), 0)
    df["documentation_score"] = np.clip(doc_base, 15, 100).round(1)

    auth_required = ~df["service_line"].isin(["Primary Care"])
    auth_denial_logit = -2.2
    auth_denial_logit += np.where(df["documentation_score"].lt(65), 0.9, 0)
    auth_denial_logit += np.where(df["payer"].eq("Meridian Choice"), 0.35, 0)
    auth_denial_logit += np.where(df["service_line"].eq("Behavioral Health"), 0.35, 0)
    auth_denial_probability = 1 / (1 + np.exp(-auth_denial_logit))
    auth_denied = auth_required & (rng.random(n) < auth_denial_probability)
    df["auth_status"] = np.where(~auth_required, "not required", np.where(auth_denied, "denied", "approved"))

    auth_lag = rng.integers(1, 9, n) + np.where(df["auth_status"].eq("denied"), rng.integers(2, 8, n), 0)
    claim_lag = rng.integers(1, 12, n)
    final_lag = rng.integers(4, 26, n)
    df["decision_date"] = df["request_date"] + pd.to_timedelta(auth_lag, unit="D")
    df["claim_date"] = df["decision_date"] + pd.to_timedelta(claim_lag, unit="D")
    df["finalized_date"] = df["claim_date"] + pd.to_timedelta(final_lag, unit="D")

    recent_cutoff = pd.Timestamp(config.start + timedelta(days=max(config.days - 45, 1)))
    base_denial_logit = -2.0
    base_denial_logit += np.where(df["documentation_score"].lt(60), 1.15, 0)
    base_denial_logit += np.where(df["auth_status"].eq("denied"), 0.95, 0)
    base_denial_logit += np.where(df["patient_segment"].eq("Medicaid"), 0.45, 0)
    base_denial_logit += np.where(df["payer"].eq("Meridian Choice"), 0.25, 0)
    base_denial_logit += np.where(df["service_line"].eq("Behavioral Health"), 0.30, 0)
    drift_mask = (
        df["request_date"].ge(recent_cutoff)
        & df["payer"].eq("Meridian Choice")
        & df["service_line"].eq("Behavioral Health")
    )
    base_denial_logit += np.where(drift_mask, 1.2, 0)
    claim_denial_probability = 1 / (1 + np.exp(-base_denial_logit))
    denied = rng.random(n) < claim_denial_probability
    df["claim_status"] = np.where(denied, "denied", "paid")

    reason_weights = np.vstack(
        [
            np.where(df["documentation_score"].lt(65), 0.40, 0.18),
            np.full(n, 0.18),
            np.where(df["patient_segment"].eq("Uninsured"), 0.30, 0.14),
            np.where(df["service_line"].isin(["Oncology", "Behavioral Health"]), 0.28, 0.18),
            np.full(n, 0.12),
        ]
    ).T
    reason_weights = reason_weights / reason_weights.sum(axis=1, keepdims=True)
    reasons = [DENIAL_REASONS[int(rng.choice(5, p=reason_weights[i]))] for i in range(n)]
    df["denial_reason"] = np.where(denied, reasons, "none")

    appeal_probability = np.where(df["denial_reason"].isin(["medical necessity", "documentation"]), 0.44, 0.25)
    df["appealed"] = denied & (rng.random(n) < appeal_probability)
    overturn_probability = np.where(df["denial_reason"].eq("documentation"), 0.55, 0.32)
    df["overturned"] = df["appealed"] & (rng.random(n) < overturn_probability)

    reimbursement_base = {
        "Primary Care": 180,
        "Imaging": 620,
        "Behavioral Health": 340,
        "Cardiology": 1450,
        "Orthopedics": 2200,
        "Oncology": 3900,
    }
    df["expected_reimbursement"] = [
        round(float(reimbursement_base[row.service_line] * rng.lognormal(0, 0.25)), 2)
        for row in df.itertuples()
    ]
    return df.sort_values("request_date").reset_index(drop=True)


def write_claimflows(path: Path, config: GeneratorConfig) -> pd.DataFrame:
    """Generate workflows and write them to CSV."""

    df = generate_claimflows(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df
