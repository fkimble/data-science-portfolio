from __future__ import annotations

import unittest

import pandas as pd

from claimflow.metrics import drift_table, group_denial_rates, intervention_backlog, metric_summary


class MetricTests(unittest.TestCase):
    def setUp(self) -> None:
        self.df = pd.DataFrame(
            {
                "encounter_id": ["a", "b", "c", "d"],
                "patient_segment": ["Medicaid", "Medicaid", "Commercial", "Commercial"],
                "region": ["Baltimore"] * 4,
                "payer": ["P1", "P1", "P2", "P2"],
                "service_line": ["Imaging", "Imaging", "Primary Care", "Primary Care"],
                "request_date": ["2025-01-01", "2025-01-02", "2025-03-01", "2025-03-02"],
                "decision_date": ["2025-01-02", "2025-01-03", "2025-03-02", "2025-03-03"],
                "claim_date": ["2025-01-03", "2025-01-04", "2025-03-03", "2025-03-04"],
                "finalized_date": ["2025-01-10", "2025-01-11", "2025-03-10", "2025-03-11"],
                "auth_status": ["approved"] * 4,
                "claim_status": ["denied", "paid", "denied", "paid"],
                "denial_reason": ["documentation", "none", "coding", "none"],
                "appealed": [True, False, False, False],
                "overturned": [True, False, False, False],
                "documentation_score": [55, 80, 70, 85],
                "expected_reimbursement": [1000.0, 900.0, 200.0, 220.0],
            }
        )

    def test_summary_known_answers(self) -> None:
        summary = dict(zip(metric_summary(self.df)["metric"], metric_summary(self.df)["value"]))
        self.assertEqual(summary["claim_volume"], 4)
        self.assertAlmostEqual(summary["denial_rate"], 0.5)
        self.assertAlmostEqual(summary["avoidable_denial_share"], 1.0)
        self.assertAlmostEqual(summary["appeal_rate"], 0.5)
        self.assertAlmostEqual(summary["overturn_rate"], 1.0)

    def test_group_denial_rates(self) -> None:
        rates = group_denial_rates(self.df, ["payer"])
        p1 = rates[rates["payer"].eq("P1")].iloc[0]
        self.assertEqual(p1["claims"], 2)
        self.assertAlmostEqual(p1["denial_rate"], 0.5)

    def test_drift_table_has_delta(self) -> None:
        drift = drift_table(self.df, ["payer"], recent_days=30)
        self.assertIn("drift_delta", drift.columns)
        self.assertEqual(len(drift), 2)

    def test_backlog_ranks_avoidable_reasons(self) -> None:
        backlog = intervention_backlog(self.df)
        self.assertIn("documentation", set(backlog["denial_reason"]))
        self.assertGreaterEqual(backlog.iloc[0]["impact_score"], backlog.iloc[-1]["impact_score"])


if __name__ == "__main__":
    unittest.main()
