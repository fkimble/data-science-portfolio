from __future__ import annotations

import unittest

import pandas as pd

from careroute.validate import validate_referrals


def valid_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "referral_id": ["r1"],
            "patient_segment": ["Medicaid"],
            "region": ["Baltimore"],
            "payer": ["P1"],
            "specialty": ["Behavioral Health"],
            "urgency": ["routine"],
            "referral_source": ["Clinic"],
            "referral_date": ["2025-01-01"],
            "authorization_required": [True],
            "network_status": ["in-network"],
            "capacity_score": [70],
            "community_need_index": [80],
            "appointment_date": ["2025-01-20"],
            "completion_status": ["completed"],
            "leakage_reason": ["none"],
            "wait_days": [19],
            "care_gap_days": [0],
            "referral_leaked": [False],
            "no_show": [False],
            "completed": [True],
            "expected_visit_value": [200.0],
        }
    )


class ValidationTests(unittest.TestCase):
    def test_valid_frame_passes(self) -> None:
        self.assertTrue(validate_referrals(valid_frame()).passed)

    def test_leaked_row_must_have_leaked_status(self) -> None:
        df = valid_frame()
        df["referral_leaked"] = True
        result = validate_referrals(df)
        self.assertFalse(result.passed)
        self.assertTrue(any("referral_leaked" in error for error in result.errors))

    def test_date_order_is_enforced(self) -> None:
        df = valid_frame()
        df["appointment_date"] = "2024-12-31"
        result = validate_referrals(df)
        self.assertFalse(result.passed)
        self.assertTrue(any("appointment_date" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
