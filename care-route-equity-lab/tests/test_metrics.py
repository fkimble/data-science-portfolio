from __future__ import annotations

import unittest

import pandas as pd

from careroute.equity import equity_gap_table
from careroute.metrics import access_rates, drift_table, intervention_backlog, metric_summary


class MetricTests(unittest.TestCase):
    def setUp(self) -> None:
        self.df = pd.DataFrame(
            {
                "referral_id": ["a", "b", "c", "d"],
                "patient_segment": ["Medicaid", "Medicaid", "Commercial", "Commercial"],
                "region": ["Baltimore", "Baltimore", "Capital", "Capital"],
                "payer": ["P1", "P1", "P2", "P2"],
                "specialty": ["Behavioral Health", "Behavioral Health", "Imaging", "Imaging"],
                "urgency": ["routine", "routine", "urgent", "urgent"],
                "referral_source": ["Clinic"] * 4,
                "referral_date": ["2025-01-01", "2025-01-02", "2025-03-01", "2025-03-02"],
                "authorization_required": [True, True, False, False],
                "network_status": ["narrow-network", "in-network", "in-network", "in-network"],
                "capacity_score": [45, 75, 90, 95],
                "community_need_index": [80, 60, 30, 40],
                "appointment_date": ["2025-02-10", "2025-01-20", "2025-03-08", "2025-03-09"],
                "completion_status": ["leaked", "completed", "no-show", "completed"],
                "leakage_reason": ["wait too long", "none", "none", "none"],
                "wait_days": [40, 18, 7, 7],
                "care_gap_days": [10, 0, 0, 0],
                "referral_leaked": [True, False, False, False],
                "no_show": [False, False, True, False],
                "completed": [False, True, False, True],
                "expected_visit_value": [300.0, 250.0, 500.0, 500.0],
            }
        )

    def test_summary_known_answers(self) -> None:
        summary = dict(zip(metric_summary(self.df)["metric"], metric_summary(self.df)["value"]))
        self.assertEqual(summary["referral_volume"], 4)
        self.assertAlmostEqual(summary["completion_rate"], 0.5)
        self.assertAlmostEqual(summary["leakage_rate"], 0.25)
        self.assertAlmostEqual(summary["no_show_rate"], 1 / 3)

    def test_access_rates(self) -> None:
        rates = access_rates(self.df, ["patient_segment"])
        medicaid = rates[rates["patient_segment"].eq("Medicaid")].iloc[0]
        self.assertEqual(medicaid["referrals"], 2)
        self.assertAlmostEqual(medicaid["leakage_rate"], 0.5)

    def test_drift_table_has_expected_columns(self) -> None:
        drift = drift_table(self.df, ["patient_segment"], recent_days=30)
        self.assertIn("leakage_drift_delta", drift.columns)
        self.assertIn("wait_drift_days", drift.columns)

    def test_equity_gap_table_ranks_excess_value(self) -> None:
        equity = equity_gap_table(self.df, ["patient_segment", "payer", "specialty"])
        self.assertIn("estimated_excess_value", equity.columns)
        self.assertGreaterEqual(equity.iloc[0]["estimated_excess_value"], equity.iloc[-1]["estimated_excess_value"])

    def test_backlog_contains_wait_intervention(self) -> None:
        backlog = intervention_backlog(self.df)
        self.assertIn("wait too long", set(backlog["target_issue"]))


if __name__ == "__main__":
    unittest.main()
