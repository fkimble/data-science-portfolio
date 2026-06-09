# Executive Summary - Maryland Incarceration Trends

## Decision Context

This project is repositioned as a public-sector analytics brief for reentry planning. The senior analyst version separates descriptive trend monitoring from causal claims, defines risk indicators clearly, and translates county-level patterns into policy questions.

## Senior Analyst Readout

- Dataset size: **180 county-year records** across **12 counties** and **15 years**.
- Average statewide recidivism rate: **41.1%**.
- Average statewide incarceration rate: **509.3 per 100k**.
- Highest reentry-priority county: **Calvert**, with recidivism **17.0 points above** the portfolio average.
- Strongest observed recidivism correlate in this synthetic dataset: **poverty_rate_pct** at **0.170**.
- Average recidivism changed **+0.17 percentage points** from the first to latest year.

## Recommendation

Use the county priority output to focus reentry-program discovery, not to imply causality. The next analyst step would be to join program availability, supervision intensity, housing access, and workforce placement data so the model can move from descriptive risk scoring to intervention evaluation.

## Artifacts

- `reports/data_quality_profile.csv`
- `reports/county_reentry_priority.csv`
- `reports/recidivism_driver_correlations.csv`
- `reports/statewide_yearly_trends.csv`
- `reports/METRIC_DICTIONARY.md`
- `reports/POLICY_BRIEF.md`
