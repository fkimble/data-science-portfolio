# Emissions Decision Support System

## Project Overview

This project analyzes synthetic Maryland county emissions data and packages the results as a decision-support asset for public-sector stakeholders. The upgraded version emphasizes KPI design, standardized dimensions, priority ranking, and dashboard-ready outputs.

The goal is to move beyond exploratory charts and answer: which counties and sectors should receive the most attention, and which metrics should leadership track over time?

## Business Questions

- Which counties contribute the highest total emissions?
- Which sectors drive the portfolio footprint?
- How do rankings change when emissions are normalized by population or economic proxy?
- What should a Power BI dashboard expose to leaders and analysts?

## Dataset

The project uses a synthetic county-sector-year dataset with intentional label inconsistencies.

| Column | Meaning |
| --- | --- |
| `county` | Maryland county label with intentional messy casing/spacing |
| `year` | Reporting year |
| `sector` | Emissions sector |
| `emissions_mtco2e` | Greenhouse gas emissions target |
| `population` | County population estimate |
| `gdp_billions_usd` | Economic activity proxy |

## Senior Analyst Deliverables

- [Executive summary](reports/EXECUTIVE_SUMMARY.md)
- [Metric dictionary](reports/METRIC_DICTIONARY.md)
- [Power BI dashboard specification](reports/POWER_BI_SPEC.md)
- [Data quality profile](reports/data_quality_profile.csv)
- [County emissions priority table](reports/county_emissions_priority.csv)
- [Sector emissions summary](reports/sector_emissions_summary.csv)
- [Yearly emissions trend](reports/yearly_emissions_trend.csv)

## Key Readout

- 600 county-sector-year records cover 10 counties, 7 sectors, and 10 years.
- The reporting layer now includes total emissions, emissions per capita, and emissions per GDP billion.
- The county priority output supports executive ranking, while the dashboard spec defines a clear stakeholder-facing Power BI build.

## How to Run

From the portfolio root:

```powershell
python scripts/build_portfolio_reports.py
```

The original notebook remains in `notebooks/`, while `reports/` contains the decision-support package.
