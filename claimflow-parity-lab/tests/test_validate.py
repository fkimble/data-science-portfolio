from __future__ import annotations

import unittest

import pandas as pd

from claimflow.validate import validate_claimflows


def valid_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "encounter_id": ["a"],
            "patient_segment": ["Medicaid"],
            "region": ["Baltimore"],
            "payer": ["P1"],
            "service_line": ["Imaging"],
            "request_date": ["2025-01-01"],
            "decision_date": ["2025-01-02"],
            "claim_date": ["2025-01-03"],
            "finalized_date": ["2025-01-04"],
            "auth_status": ["approved"],
            "claim_status": ["denied"],
            "denial_reason": ["documentation"],
            "appealed": [True],
            "overturned": [False],
            "documentation_score": [80],
            "expected_reimbursement": [100.0],
        }
    )


class ValidationTests(unittest.TestCase):
    def test_valid_frame_passes(self) -> None:
        self.assertTrue(validate_claimflows(valid_frame()).passed)

    def test_paid_claim_cannot_have_denial_reason(self) -> None:
        df = valid_frame()
        df["claim_status"] = "paid"
        result = validate_claimflows(df)
        self.assertFalse(result.passed)
        self.assertTrue(any("denial_reason" in error for error in result.errors))

    def test_date_order_is_enforced(self) -> None:
        df = valid_frame()
        df["decision_date"] = "2024-12-31"
        result = validate_claimflows(df)
        self.assertFalse(result.passed)
        self.assertTrue(any("workflow dates" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
