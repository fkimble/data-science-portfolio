# Executive Summary - Emissions Decision Support System

## Decision Context

This project is framed as a decision-support layer for county leaders who need to prioritize emissions-reduction attention across counties, sectors, and time. The senior analyst version emphasizes standardization, KPI definitions, ranking logic, and dashboard-ready outputs.

## Senior Analyst Readout

- Dataset size: **600 county-sector-year records** covering **10 counties**, **7 sectors**, and **10 years**.
- Total modeled emissions: **685,995 MTCO2e**.
- Highest-emission county: **Frederick** with **104,761 MTCO2e**.
- Highest-emission sector: **Transportation** with **198,049 MTCO2e**.
- Portfolio emissions changed **8.6%** from **2015** to **2024**.

## Recommendation

Use the county-priority table as the executive ranking layer, then pair it with sector-specific drilldowns in Power BI. For governance, publish the cleaned county and sector labels, track emissions per capita and emissions per GDP billion, and flag counties that rank high on both total emissions and normalized intensity.

## Artifacts

- `reports/data_quality_profile.csv`
- `reports/county_emissions_priority.csv`
- `reports/sector_emissions_summary.csv`
- `reports/yearly_emissions_trend.csv`
- `reports/METRIC_DICTIONARY.md`
- `reports/POWER_BI_SPEC.md`
