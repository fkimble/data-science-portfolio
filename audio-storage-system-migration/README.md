# Audio Storage System Migration

## Project Overview

This project simulates a migration from a flat Microsoft Access audio-record export into an Oracle-style normalized schema. The upgraded version treats the migration like a controlled analytics/data-governance engagement, not just a notebook exercise.

The analyst objective is to prove that the migration preserves record integrity, reduces reporting ambiguity, and creates a data model that can support storage-cost monitoring.

## Business Questions

- Did every Access export row survive the migration with a unique primary key?
- Which departments own the largest storage and cost exposure?
- Which storage tiers should be reviewed for cost optimization?
- What reconciliation checks should run before stakeholders trust the Oracle target?

## Dataset

The project uses a synthetic Access export so the workflow runs end to end without private data.

| Column | Meaning |
| --- | --- |
| `record_id` | Unique source record identifier |
| `file_name` | Audio file name |
| `department` | Owning department with intentional messy labels |
| `recording_type` | Recording category |
| `duration_sec` | Duration in seconds |
| `sample_rate_hz` | Sample rate |
| `channels` | Mono/stereo count |
| `created_date` | Source creation date |
| `created_by` | Creator role |
| `file_size_mb` | File size |
| `storage_tier` | Standard, infrequent, or archive |
| `storage_cost_usd_month` | Modeled monthly storage cost |

## Senior Analyst Deliverables

- [Executive summary](reports/EXECUTIVE_SUMMARY.md)
- [Metric dictionary](reports/METRIC_DICTIONARY.md)
- [Data quality profile](reports/data_quality_profile.csv)
- [Migration control totals](reports/migration_control_totals.csv)
- [Department storage risk table](reports/department_storage_risk.csv)
- [Storage-tier summary](reports/storage_tier_summary.csv)
- [Normalized schema](schema/normalized_schema.sql)
- [Reconciliation SQL](schema/senior_reconciliation_queries.sql)

## Key Readout

- 1,500 source records reconcile to 1,500 unique record IDs.
- Standardized department and recording-type labels create governed reporting dimensions.
- Department-level storage exposure and archive-share metrics create a practical cost-review queue.
- Reconciliation SQL gives the project an audit trail a data migration lead would expect.

## How to Run

From the portfolio root:

```powershell
python scripts/build_portfolio_reports.py
```

The original notebook remains in `notebooks/`, while the `reports/` folder contains the senior analyst outputs.
