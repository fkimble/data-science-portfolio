"""Synthetic specialty-referral workflow generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd


PATIENT_SEGMENTS = ["Commercial", "Medicaid", "Medicare", "Uninsured"]
REGIONS = ["Baltimore", "Capital", "Eastern Shore", "Western MD"]
PAYERS = ["Aster Health", "Blue Harbor", "CivicCare", "Meridian Choice"]
SPECIALTIES = ["Cardiology", "Dermatology", "Behavioral Health", "Orthopedics", "Neurology", "Endocrinology", "Oncology", "Imaging"]
URGENCY = ["routine", "urgent"]
SOURCES = ["Harbor Primary Care", "Eastside Family", "County Health Clinic", "University Internal Medicine", "Community Pediatrics"]
NETWORK_STATUS = ["in-network", "narrow-network", "out-of-network"]


@dataclass(frozen=True)
class GeneratorConfig:
    """Configuration for synthetic referral rows."""

    referrals: int = 6000
    days: int = 180
    seed: int = 42
    start: date = date(2025, 1, 1)


def _choice(rng: np.random.Generator, values: list[str], size: int, p: list[float] | None = None) -> np.ndarray:
    return rng.choice(values, size=size, p=p)


def generate_referrals(config: GeneratorConfig) -> pd.DataFrame:
    """Generate synthetic specialty-referral access workflows.

    The generator includes one intentional recent drift pattern: Medicaid
    behavioral-health referrals in lower-capacity regions become slower and
    leak more often in the final 45 days. That gives the analysis a realistic
    signal to detect without using real patient data.
    """

    rng = np.random.default_rng(config.seed)
    n = config.referrals
    offsets = rng.integers(0, config.days, size=n)
    referral_dates = pd.to_datetime([config.start + timedelta(days=int(x)) for x in offsets])

    df = pd.DataFrame(
        {
            "referral_id": [f"CR-{config.seed}-{i:06d}" for i in range(n)],
            "patient_segment": _choice(rng, PATIENT_SEGMENTS, n, [0.43, 0.25, 0.24, 0.08]),
            "region": _choice(rng, REGIONS, n, [0.44, 0.27, 0.17, 0.12]),
            "payer": _choice(rng, PAYERS, n, [0.33, 0.26, 0.24, 0.17]),
            "specialty": _choice(rng, SPECIALTIES, n, [0.14, 0.11, 0.16, 0.13, 0.12, 0.11, 0.08, 0.15]),
            "urgency": _choice(rng, URGENCY, n, [0.78, 0.22]),
            "referral_source": _choice(rng, SOURCES, n),
            "referral_date": referral_dates,
        }
    )

    need = rng.normal(48, 18, n)
    need += np.where(df["patient_segment"].eq("Medicaid"), rng.normal(15, 5, n), 0)
    need += np.where(df["patient_segment"].eq("Uninsured"), rng.normal(20, 5, n), 0)
    need += np.where(df["region"].isin(["Eastern Shore", "Western MD"]), rng.normal(10, 4, n), 0)
    df["community_need_index"] = np.clip(need, 0, 100).round(1)

    capacity = rng.normal(72, 13, n)
    capacity -= np.where(df["specialty"].isin(["Behavioral Health", "Neurology", "Oncology"]), rng.normal(12, 4, n), 0)
    capacity -= np.where(df["region"].isin(["Eastern Shore", "Western MD"]), rng.normal(10, 3, n), 0)
    df["capacity_score"] = np.clip(capacity, 10, 100).round(1)

    auth_required = df["payer"].isin(["Meridian Choice", "CivicCare"]) | df["specialty"].isin(["Oncology", "Imaging", "Orthopedics"])
    df["authorization_required"] = auth_required

    network_prob = np.where(df["payer"].eq("Meridian Choice"), 0.35, 0.18)
    network_prob += np.where(df["region"].isin(["Eastern Shore", "Western MD"]), 0.12, 0)
    narrow = rng.random(n) < np.clip(network_prob, 0, 0.65)
    out = narrow & (rng.random(n) < np.where(df["patient_segment"].eq("Uninsured"), 0.35, 0.16))
    df["network_status"] = np.where(out, "out-of-network", np.where(narrow, "narrow-network", "in-network"))

    base_wait = {
        "Cardiology": 24,
        "Dermatology": 38,
        "Behavioral Health": 34,
        "Orthopedics": 29,
        "Neurology": 44,
        "Endocrinology": 35,
        "Oncology": 16,
        "Imaging": 12,
    }
    wait = np.array([base_wait[s] for s in df["specialty"]], dtype=float)
    wait += np.where(df["urgency"].eq("urgent"), -8, 0)
    wait += np.where(df["authorization_required"], rng.normal(5, 2, n), 0)
    wait += np.where(df["network_status"].eq("narrow-network"), rng.normal(7, 3, n), 0)
    wait += np.where(df["network_status"].eq("out-of-network"), rng.normal(12, 4, n), 0)
    wait += np.where(df["capacity_score"].lt(55), rng.normal(10, 4, n), 0)
    wait += np.where(df["community_need_index"].gt(70), rng.normal(4, 2, n), 0)

    recent_cutoff = pd.Timestamp(config.start + timedelta(days=max(config.days - 45, 1)))
    drift_mask = (
        df["referral_date"].ge(recent_cutoff)
        & df["patient_segment"].eq("Medicaid")
        & df["specialty"].eq("Behavioral Health")
        & df["region"].isin(["Eastern Shore", "Western MD"])
    )
    wait += np.where(drift_mask, rng.normal(18, 4, n), 0)
    wait = np.clip(np.rint(wait + rng.normal(0, 5, n)), 1, 120).astype(int)
    df["wait_days"] = wait
    df["appointment_date"] = df["referral_date"] + pd.to_timedelta(wait, unit="D")
    df["care_gap_days"] = np.clip(df["wait_days"] - np.where(df["urgency"].eq("urgent"), 14, 30), 0, None)

    leakage_logit = -2.5
    leakage_logit += np.where(df["wait_days"].gt(30), 0.75, 0)
    leakage_logit += np.where(df["wait_days"].gt(45), 0.65, 0)
    leakage_logit += np.where(df["network_status"].eq("narrow-network"), 0.6, 0)
    leakage_logit += np.where(df["network_status"].eq("out-of-network"), 1.0, 0)
    leakage_logit += np.where(df["patient_segment"].isin(["Medicaid", "Uninsured"]), 0.4, 0)
    leakage_logit += np.where(drift_mask, 0.9, 0)
    leakage_probability = 1 / (1 + np.exp(-leakage_logit))
    leaked = rng.random(n) < leakage_probability

    no_show_logit = -2.7
    no_show_logit += np.where(df["wait_days"].gt(30), 0.35, 0)
    no_show_logit += np.where(df["community_need_index"].gt(70), 0.6, 0)
    no_show_logit += np.where(df["patient_segment"].isin(["Medicaid", "Uninsured"]), 0.35, 0)
    no_show_probability = 1 / (1 + np.exp(-no_show_logit))
    no_show = (~leaked) & (rng.random(n) < no_show_probability)
    cancelled = (~leaked) & (~no_show) & (rng.random(n) < 0.05)
    completed = (~leaked) & (~no_show) & (~cancelled)

    df["completion_status"] = np.select(
        [leaked, no_show, cancelled, completed],
        ["leaked", "no-show", "cancelled", "completed"],
        default="completed",
    )
    df["referral_leaked"] = leaked
    df["no_show"] = no_show
    df["completed"] = completed

    reasons = []
    for row in df.itertuples():
        if not row.referral_leaked:
            reasons.append("none")
        elif row.network_status == "out-of-network":
            reasons.append("payer network mismatch")
        elif row.wait_days > 45:
            reasons.append("wait too long")
        elif row.capacity_score < 50:
            reasons.append("no local capacity")
        elif row.authorization_required:
            reasons.append("authorization friction")
        else:
            reasons.append("patient preference")
    df["leakage_reason"] = reasons

    value_base = {
        "Cardiology": 520,
        "Dermatology": 260,
        "Behavioral Health": 220,
        "Orthopedics": 610,
        "Neurology": 700,
        "Endocrinology": 360,
        "Oncology": 1350,
        "Imaging": 480,
    }
    df["expected_visit_value"] = [
        round(float(value_base[row.specialty] * rng.lognormal(0, 0.2)), 2)
        for row in df.itertuples()
    ]
    return df.sort_values("referral_date").reset_index(drop=True)
