# ClaimFlow Parity Lab - Executive Insights

Synthetic data only. This report summarizes a generated prior-authorization and claims workflow dataset.

## Headline Metrics

- Claim volume: 5,000
- Denial rate: 18.8%
- Avoidable denial share: 76.1%
- Appeal rate: 30.3%
- Overturn rate: 39.6%
- Median cycle time: 26 days
- Denied reimbursement at risk: $1,166,371

## Biggest Drift Signal

The largest recent denial-rate increase is `Meridian Choice` / `Behavioral Health` with a drift delta of 18.7%. This is the cohort to inspect first for policy changes, staffing gaps, or documentation friction.

## Largest Access-Parity Gap

The largest estimated excess-denial value appears in `Medicare` / `Meridian Choice` / `Oncology`. The model estimates $22,664 in excess value versus the population-average denial rate.

## Recommended First Bet

**Launch pre-submit documentation completeness checklist**

- Denial reason: `documentation`
- Avoidable denials: 226
- Reimbursement at risk: $272,193
- Impact score: 195,979

## Artifacts

- `reports/metric_summary.csv`
- `reports/drift_table.csv`
- `reports/parity_table.csv`
- `reports/intervention_backlog.csv`
- `reports/figures/denial_heatmap.svg`
- `reports/figures/drift_bars.svg`
