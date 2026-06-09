# CareRoute Equity Lab - Executive Insights

Synthetic data only. This report summarizes specialty-referral access, leakage, and wait-time patterns.

## Headline Metrics

- Referral volume: 6,000
- Completion rate: 69.1%
- Referral leakage rate: 18.7%
- No-show rate: 10.3%
- Median wait days: 36
- Long-wait share: 65.1%
- Deferred visit value: $2,097,859

## Biggest Drift Signal

The largest leakage drift is `Medicaid` / `Behavioral Health` with a leakage delta of 11.9% and wait drift of 5.0 days.

## Largest Equity Gap

The largest estimated excess leakage value appears in `Medicaid` / `Aster Health` / `Neurology`. The model estimates $5,581 in excess leaked referral value versus the portfolio-average leakage rate.

## Recommended First Bet

**Launch high-need reminder and transportation outreach workflow**

- Target issue: `no-show`
- Affected referrals: 501
- Expected visit value at risk: $279,971
- Impact score: 145,585

## Artifacts

- `reports/metric_summary.csv`
- `reports/access_rates.csv`
- `reports/drift_table.csv`
- `reports/equity_gap_table.csv`
- `reports/intervention_backlog.csv`
- `reports/figures/leakage_heatmap.svg`
- `reports/figures/wait_drift_bars.svg`
