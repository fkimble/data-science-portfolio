# Incarceration Trends Maryland

## Project Overview

This project analyzes synthetic Maryland county incarceration and recidivism trends. The upgraded version reframes the notebook as a public-sector analytics brief for reentry planning, with clear interpretation guardrails.

The project is intentionally descriptive. It identifies counties and indicators worth deeper investigation, but it does not claim that correlation proves causation.

## Policy Questions

- Which counties show the highest recidivism gaps versus the portfolio average?
- Which socioeconomic indicators are most associated with recidivism in the synthetic data?
- How should a policy analyst prioritize counties for deeper reentry-program discovery?
- What additional data would be needed before evaluating intervention effectiveness?

## Dataset

The project uses a synthetic county-year dataset.

| Column | Meaning |
| --- | --- |
| `county` | Maryland county label with intentional messy casing |
| `year` | Reporting year |
| `incarceration_rate_per_100k` | Incarceration rate per 100,000 |
| `recidivism_rate_pct` | Recidivism rate target |
| `unemployment_rate_pct` | Unemployment rate |
| `poverty_rate_pct` | Poverty rate |
| `college_education_pct` | College education share |
| `police_per_1k` | Police per 1,000 residents |
| `violent_crime_rate_per_100k` | Violent crime rate per 100,000 |

## Senior Analyst Deliverables

- [Executive summary](reports/EXECUTIVE_SUMMARY.md)
- [Metric dictionary](reports/METRIC_DICTIONARY.md)
- [Policy brief](reports/POLICY_BRIEF.md)
- [Data quality profile](reports/data_quality_profile.csv)
- [County reentry priority table](reports/county_reentry_priority.csv)
- [Recidivism driver correlations](reports/recidivism_driver_correlations.csv)
- [Statewide yearly trends](reports/statewide_yearly_trends.csv)

## Key Readout

- 180 county-year records cover 12 counties and 15 years.
- The project now includes a social-risk index and county priority ranking.
- Correlations are presented with explicit guardrails so the analysis reads as professional policy analytics, not overclaimed modeling.

## How to Run

From the portfolio root:

```powershell
python scripts/build_portfolio_reports.py
```

The original notebook remains in `notebooks/`, while `reports/` contains the policy-facing outputs.
