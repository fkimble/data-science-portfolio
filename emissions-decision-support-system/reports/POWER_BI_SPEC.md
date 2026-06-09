# Power BI Dashboard Specification

## Page 1 - Executive Overview

- KPI cards: total emissions, latest-year emissions, emissions per capita, top county, top sector.
- Line chart: total emissions by year.
- Bar chart: top 10 counties by total emissions.

## Page 2 - County Drilldown

- Filters: county, sector, year.
- Matrix: county x sector emissions.
- Scatter: population vs emissions with county labels.
- Conditional formatting: emissions per capita.

## Page 3 - Intervention Prioritization

- Ranking table: county, sector, total emissions, normalized intensity, trend direction.
- Insight callout: counties that are high on both absolute emissions and intensity.
- Export button target: `reports/county_emissions_priority.csv`.

## Data Governance Notes

- County and sector labels must be standardized before dashboard refresh.
- Invalid years, negative emissions, null population, and null GDP proxy should fail refresh validation.
