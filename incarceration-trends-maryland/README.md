# Incarceration Trends (Maryland)



## Project Overview
This notebook explores incarceration and recidivism patterns across Maryland counties over time.
It includes:
- trend analysis and county comparisons
- correlation analysis (incarceration ↔ recidivism)
- a baseline model to estimate recidivism using socioeconomic context

## Dataset
This repo includes a synthetic county-year dataset so the notebook runs with no external downloads.

### Data Dictionary
| Column | Meaning |
|---|---|
| county | County name (messy strings included intentionally) |
| year | Year |
| incarceration_rate_per_100k | Incarceration rate per 100,000 residents |
| recidivism_rate_pct | Recidivism rate (%) **target** |
| unemployment_rate_pct | Unemployment (%) |
| poverty_rate_pct | Poverty (%) |
| college_education_pct | % with college education |
| police_per_1k | Police per 1,000 residents |
| violent_crime_rate_per_100k | Violent crime rate per 100,000 |

## What’s inside
- `notebooks/01_incarceration_trends.ipynb` — full workflow (cleaning → EDA → correlation → model)
- `reports/cleaned_incarceration_md.csv` — cleaned export created by the notebook
