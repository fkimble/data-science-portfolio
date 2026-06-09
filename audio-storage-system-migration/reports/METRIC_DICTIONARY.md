# Metric Dictionary - Audio Storage Migration

| Metric | Definition | Why it matters |
| --- | --- | --- |
| Source rows | Count of records in the Access export | Reconciliation control for migration completeness |
| Unique record IDs | Distinct `record_id` values | Confirms primary-key readiness |
| Duplicate record IDs | Duplicate `record_id` values | Blocks safe load into Oracle without remediation |
| Total storage GB | Sum of `file_size_mb` divided by 1,024 | Portfolio-level storage footprint |
| Monthly storage cost | Sum of `storage_cost_usd_month` | Financial impact of storage-tier policy |
| Archive share | Percent of department files in `Archive` tier | Indicates whether retention/cost policy is being applied |
| Cost per GB-month | Monthly cost divided by file size in GB | Normalizes cost comparisons across file sizes |
