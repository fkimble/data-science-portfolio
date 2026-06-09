from __future__ import annotations

import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def money(value: float) -> str:
    return f"${value:,.2f}"


def pct(value: float) -> str:
    return f"{value:.1f}%"


def write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.strip() + "\n", encoding="utf-8")


def quality_profile(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        rows.append(
            {
                "column": col,
                "dtype": str(df[col].dtype),
                "rows": len(df),
                "missing": int(df[col].isna().sum()),
                "missing_pct": round(float(df[col].isna().mean() * 100), 2),
                "distinct_values": int(df[col].nunique(dropna=True)),
                "sample_value": "" if df[col].dropna().empty else str(df[col].dropna().iloc[0]),
            }
        )
    return pd.DataFrame(rows)


def normalize_label(value: object) -> str:
    label = " ".join(str(value).strip().title().split())
    replacements = {
        "It": "IT",
        "Md": "MD",
        "Hr": "HR",
    }
    return replacements.get(label, label)


def build_audio() -> None:
    project = ROOT / "audio-storage-system-migration"
    df = pd.read_csv(project / "data" / "access_export_audio_records.csv")
    df["department_clean"] = df["department"].map(normalize_label)
    df["recording_type_clean"] = df["recording_type"].map(normalize_label)
    df["created_date"] = pd.to_datetime(df["created_date"])
    df["duration_hours"] = df["duration_sec"] / 3600
    df["cost_per_gb_month"] = df["storage_cost_usd_month"] / (df["file_size_mb"] / 1024)

    reports = project / "reports"
    reports.mkdir(exist_ok=True)
    quality_profile(df).to_csv(reports / "data_quality_profile.csv", index=False)

    control_totals = pd.DataFrame(
        [
            {"control": "source_rows", "value": len(df)},
            {"control": "unique_record_ids", "value": df["record_id"].nunique()},
            {"control": "duplicate_record_ids", "value": int(df["record_id"].duplicated().sum())},
            {"control": "departments_after_standardization", "value": df["department_clean"].nunique()},
            {"control": "recording_types_after_standardization", "value": df["recording_type_clean"].nunique()},
            {"control": "total_storage_gb", "value": round(float(df["file_size_mb"].sum() / 1024), 2)},
            {"control": "monthly_storage_cost_usd", "value": round(float(df["storage_cost_usd_month"].sum()), 4)},
        ]
    )
    control_totals.to_csv(reports / "migration_control_totals.csv", index=False)

    dept = (
        df.groupby("department_clean")
        .agg(
            records=("record_id", "count"),
            storage_gb=("file_size_mb", lambda s: round(float(s.sum() / 1024), 2)),
            monthly_cost=("storage_cost_usd_month", "sum"),
            avg_duration_min=("duration_sec", lambda s: round(float(s.mean() / 60), 1)),
            archive_share=("storage_tier", lambda s: round(float((s == "Archive").mean() * 100), 1)),
        )
        .reset_index()
        .sort_values("monthly_cost", ascending=False)
    )
    dept["monthly_cost"] = dept["monthly_cost"].round(4)
    dept.to_csv(reports / "department_storage_risk.csv", index=False)

    tier = (
        df.groupby("storage_tier")
        .agg(records=("record_id", "count"), storage_gb=("file_size_mb", lambda s: round(float(s.sum() / 1024), 2)), monthly_cost=("storage_cost_usd_month", "sum"))
        .reset_index()
        .sort_values("monthly_cost", ascending=False)
    )
    tier["monthly_cost"] = tier["monthly_cost"].round(4)
    tier.to_csv(reports / "storage_tier_summary.csv", index=False)

    top_dept = dept.iloc[0]
    archive_gap = 100 - float(dept["archive_share"].mean())
    write_text(
        reports / "EXECUTIVE_SUMMARY.md",
        f"""
# Executive Summary - Audio Storage System Migration

## Decision Context

The migration question is not simply whether a flat Microsoft Access export can be moved into Oracle. A stronger analyst view asks whether the migration preserves row-level integrity, reduces operational reporting risk, and creates a governed model that can support cost optimization.

## Senior Analyst Readout

- Source control total: **{len(df):,} records** with **{df['record_id'].nunique():,} unique record IDs** and **{int(df['record_id'].duplicated().sum())} duplicate IDs**.
- Standardization reduced operational reporting to **{df['department_clean'].nunique()} clean departments** and **{df['recording_type_clean'].nunique()} clean recording types**.
- Total managed storage is **{df['file_size_mb'].sum() / 1024:,.2f} GB** with modeled monthly cost of **{money(float(df['storage_cost_usd_month'].sum()))}**.
- Highest-cost department: **{top_dept['department_clean']}** with **{top_dept['records']:,} records**, **{top_dept['storage_gb']:,.2f} GB**, and **{money(float(top_dept['monthly_cost']))}** monthly cost.
- Mean archive placement is **{pct(float(dept['archive_share'].mean()))}**. The remaining **{pct(archive_gap)}** average non-archive share is the main cost-review queue.

## Recommendation

Treat the Oracle migration as a controlled data product: publish control totals, enforce lookup-table ownership, add a reconciliation query to deployment, and create a monthly storage-tier exception report for large standard-tier files that may be archive candidates.

## Artifacts

- `reports/data_quality_profile.csv`
- `reports/migration_control_totals.csv`
- `reports/department_storage_risk.csv`
- `reports/storage_tier_summary.csv`
- `schema/normalized_schema.sql`
""",
    )

    write_text(
        reports / "METRIC_DICTIONARY.md",
        """
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
""",
    )

    write_text(
        project / "schema" / "senior_reconciliation_queries.sql",
        """
-- Senior analyst reconciliation checks for the Access-to-Oracle migration.

-- 1. Source-to-target row reconciliation.
SELECT COUNT(*) AS migrated_audio_files
FROM AudioFiles;

-- 2. Primary-key uniqueness guardrail.
SELECT record_id, COUNT(*) AS duplicate_count
FROM AudioFiles
GROUP BY record_id
HAVING COUNT(*) > 1;

-- 3. Department-level storage and cost exposure.
SELECT
  d.dept_name,
  COUNT(*) AS records,
  ROUND(SUM(a.file_size_mb) / 1024, 2) AS storage_gb,
  ROUND(SUM(a.storage_cost_usd_month), 4) AS monthly_cost
FROM AudioFiles a
JOIN Departments d ON a.dept_id = d.dept_id
GROUP BY d.dept_name
ORDER BY monthly_cost DESC;

-- 4. Cost optimization queue: large standard-tier files.
SELECT
  a.record_id,
  a.file_name,
  d.dept_name,
  a.file_size_mb,
  a.storage_cost_usd_month
FROM AudioFiles a
JOIN Departments d ON a.dept_id = d.dept_id
JOIN StorageTiers s ON a.tier_id = s.tier_id
WHERE s.tier_name = 'Standard'
  AND a.file_size_mb >= 100
ORDER BY a.storage_cost_usd_month DESC;
""",
    )


def build_emissions() -> None:
    project = ROOT / "emissions-decision-support-system"
    df = pd.read_csv(project / "data" / "raw_emissions_maryland.csv")
    df["county_clean"] = df["county"].map(normalize_label)
    df["sector_clean"] = df["sector"].map(normalize_label)
    df["emissions_per_capita"] = df["emissions_mtco2e"] / df["population"]
    df["emissions_per_gdp_billion"] = df["emissions_mtco2e"] / df["gdp_billions_usd"]

    reports = project / "reports"
    reports.mkdir(exist_ok=True)
    quality_profile(df).to_csv(reports / "data_quality_profile.csv", index=False)

    county = (
        df.groupby("county_clean")
        .agg(
            records=("county_clean", "count"),
            total_emissions=("emissions_mtco2e", "sum"),
            avg_emissions_per_capita=("emissions_per_capita", "mean"),
            avg_emissions_per_gdp_billion=("emissions_per_gdp_billion", "mean"),
            population=("population", "mean"),
        )
        .reset_index()
        .sort_values("total_emissions", ascending=False)
    )
    county["total_emissions"] = county["total_emissions"].round(2)
    county["avg_emissions_per_capita"] = county["avg_emissions_per_capita"].round(5)
    county["avg_emissions_per_gdp_billion"] = county["avg_emissions_per_gdp_billion"].round(2)
    county.to_csv(reports / "county_emissions_priority.csv", index=False)

    sector = (
        df.groupby("sector_clean")
        .agg(records=("sector_clean", "count"), total_emissions=("emissions_mtco2e", "sum"), avg_emissions=("emissions_mtco2e", "mean"))
        .reset_index()
        .sort_values("total_emissions", ascending=False)
    )
    sector[["total_emissions", "avg_emissions"]] = sector[["total_emissions", "avg_emissions"]].round(2)
    sector.to_csv(reports / "sector_emissions_summary.csv", index=False)

    yearly = df.groupby("year").agg(total_emissions=("emissions_mtco2e", "sum")).reset_index().sort_values("year")
    first, last = yearly.iloc[0], yearly.iloc[-1]
    trend_pct = ((last["total_emissions"] - first["total_emissions"]) / first["total_emissions"]) * 100
    yearly["total_emissions"] = yearly["total_emissions"].round(2)
    yearly.to_csv(reports / "yearly_emissions_trend.csv", index=False)

    top_county = county.iloc[0]
    top_sector = sector.iloc[0]
    write_text(
        reports / "EXECUTIVE_SUMMARY.md",
        f"""
# Executive Summary - Emissions Decision Support System

## Decision Context

This project is framed as a decision-support layer for county leaders who need to prioritize emissions-reduction attention across counties, sectors, and time. The senior analyst version emphasizes standardization, KPI definitions, ranking logic, and dashboard-ready outputs.

## Senior Analyst Readout

- Dataset size: **{len(df):,} county-sector-year records** covering **{df['county_clean'].nunique()} counties**, **{df['sector_clean'].nunique()} sectors**, and **{df['year'].nunique()} years**.
- Total modeled emissions: **{df['emissions_mtco2e'].sum():,.0f} MTCO2e**.
- Highest-emission county: **{top_county['county_clean']}** with **{top_county['total_emissions']:,.0f} MTCO2e**.
- Highest-emission sector: **{top_sector['sector_clean']}** with **{top_sector['total_emissions']:,.0f} MTCO2e**.
- Portfolio emissions changed **{trend_pct:,.1f}%** from **{int(first['year'])}** to **{int(last['year'])}**.

## Recommendation

Use the county-priority table as the executive ranking layer, then pair it with sector-specific drilldowns in Power BI. For governance, publish the cleaned county and sector labels, track emissions per capita and emissions per GDP billion, and flag counties that rank high on both total emissions and normalized intensity.

## Artifacts

- `reports/data_quality_profile.csv`
- `reports/county_emissions_priority.csv`
- `reports/sector_emissions_summary.csv`
- `reports/yearly_emissions_trend.csv`
- `reports/METRIC_DICTIONARY.md`
- `reports/POWER_BI_SPEC.md`
""",
    )

    write_text(
        reports / "METRIC_DICTIONARY.md",
        """
# Metric Dictionary - Emissions Decision Support

| Metric | Definition | Use |
| --- | --- | --- |
| Total emissions | Sum of `emissions_mtco2e` | Executive prioritization and trend reporting |
| Emissions per capita | `emissions_mtco2e / population` | Normalizes county comparison by population |
| Emissions per GDP billion | `emissions_mtco2e / gdp_billions_usd` | Normalizes by economic activity proxy |
| Sector share | Sector emissions divided by total emissions | Identifies which sector drives the footprint |
| Year-over-year change | Current-year emissions minus prior-year emissions, divided by prior year | Detects trend direction and pacing |
| Priority county | County ranking high on total and normalized emissions | Directs stakeholder attention |
""",
    )

    write_text(
        reports / "POWER_BI_SPEC.md",
        """
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
""",
    )


def build_incarceration() -> None:
    project = ROOT / "incarceration-trends-maryland"
    df = pd.read_csv(project / "data" / "incarceration_md_synthetic.csv")
    df["county_clean"] = df["county"].map(normalize_label)
    df["social_risk_index"] = (
        df["unemployment_rate_pct"].rank(pct=True)
        + df["poverty_rate_pct"].rank(pct=True)
        + df["violent_crime_rate_per_100k"].rank(pct=True)
        + (1 - df["college_education_pct"].rank(pct=True))
    ) / 4
    df["recidivism_gap_vs_state_avg"] = df["recidivism_rate_pct"] - df["recidivism_rate_pct"].mean()

    reports = project / "reports"
    reports.mkdir(exist_ok=True)
    quality_profile(df).to_csv(reports / "data_quality_profile.csv", index=False)

    county = (
        df.groupby("county_clean")
        .agg(
            years=("year", "nunique"),
            avg_incarceration_rate=("incarceration_rate_per_100k", "mean"),
            avg_recidivism_rate=("recidivism_rate_pct", "mean"),
            avg_social_risk_index=("social_risk_index", "mean"),
            avg_violent_crime_rate=("violent_crime_rate_per_100k", "mean"),
        )
        .reset_index()
    )
    county["recidivism_gap_vs_state_avg"] = county["avg_recidivism_rate"] - df["recidivism_rate_pct"].mean()
    county = county.sort_values(["recidivism_gap_vs_state_avg", "avg_social_risk_index"], ascending=[False, False])
    county = county.round(3)
    county.to_csv(reports / "county_reentry_priority.csv", index=False)

    corr_cols = [
        "recidivism_rate_pct",
        "incarceration_rate_per_100k",
        "unemployment_rate_pct",
        "poverty_rate_pct",
        "college_education_pct",
        "police_per_1k",
        "violent_crime_rate_per_100k",
        "social_risk_index",
    ]
    corr = df[corr_cols].corr(numeric_only=True)["recidivism_rate_pct"].sort_values(ascending=False).reset_index()
    corr.columns = ["feature", "correlation_with_recidivism"]
    corr["correlation_with_recidivism"] = corr["correlation_with_recidivism"].round(3)
    corr.to_csv(reports / "recidivism_driver_correlations.csv", index=False)

    yearly = (
        df.groupby("year")
        .agg(avg_incarceration_rate=("incarceration_rate_per_100k", "mean"), avg_recidivism_rate=("recidivism_rate_pct", "mean"))
        .reset_index()
        .round(3)
    )
    yearly.to_csv(reports / "statewide_yearly_trends.csv", index=False)

    top_county = county.iloc[0]
    strongest_driver = corr[corr["feature"].ne("recidivism_rate_pct")].iloc[0]
    trend_change = yearly.iloc[-1]["avg_recidivism_rate"] - yearly.iloc[0]["avg_recidivism_rate"]
    write_text(
        reports / "EXECUTIVE_SUMMARY.md",
        f"""
# Executive Summary - Maryland Incarceration Trends

## Decision Context

This project is repositioned as a public-sector analytics brief for reentry planning. The senior analyst version separates descriptive trend monitoring from causal claims, defines risk indicators clearly, and translates county-level patterns into policy questions.

## Senior Analyst Readout

- Dataset size: **{len(df):,} county-year records** across **{df['county_clean'].nunique()} counties** and **{df['year'].nunique()} years**.
- Average statewide recidivism rate: **{df['recidivism_rate_pct'].mean():.1f}%**.
- Average statewide incarceration rate: **{df['incarceration_rate_per_100k'].mean():.1f} per 100k**.
- Highest reentry-priority county: **{top_county['county_clean']}**, with recidivism **{top_county['recidivism_gap_vs_state_avg']:.1f} points above** the portfolio average.
- Strongest observed recidivism correlate in this synthetic dataset: **{strongest_driver['feature']}** at **{strongest_driver['correlation_with_recidivism']:.3f}**.
- Average recidivism changed **{trend_change:+.2f} percentage points** from the first to latest year.

## Recommendation

Use the county priority output to focus reentry-program discovery, not to imply causality. The next analyst step would be to join program availability, supervision intensity, housing access, and workforce placement data so the model can move from descriptive risk scoring to intervention evaluation.

## Artifacts

- `reports/data_quality_profile.csv`
- `reports/county_reentry_priority.csv`
- `reports/recidivism_driver_correlations.csv`
- `reports/statewide_yearly_trends.csv`
- `reports/METRIC_DICTIONARY.md`
- `reports/POLICY_BRIEF.md`
""",
    )

    write_text(
        reports / "METRIC_DICTIONARY.md",
        """
# Metric Dictionary - Incarceration Trends

| Metric | Definition | Interpretation Guardrail |
| --- | --- | --- |
| Incarceration rate | Incarcerated population per 100,000 residents | Descriptive volume/intensity metric |
| Recidivism rate | Percent returning to incarceration in the synthetic dataset | Outcome proxy, not a causal measure |
| Social risk index | Percentile composite of unemployment, poverty, violent crime, and inverse college education | Screening feature for prioritization |
| Recidivism gap vs state average | County average recidivism minus portfolio average | Identifies counties above/below baseline |
| Driver correlation | Pearson correlation with recidivism | Directional association only |
| Reentry priority | County ranking by recidivism gap and social risk | Helps focus discovery and stakeholder interviews |
""",
    )

    write_text(
        reports / "POLICY_BRIEF.md",
        """
# Policy Brief - Reentry Analytics Use Case

## Question

Which Maryland counties should be prioritized for deeper reentry-program analysis based on recidivism, incarceration intensity, and socioeconomic risk indicators?

## Analyst Position

The current dataset is appropriate for descriptive prioritization and stakeholder discovery. It is not sufficient for causal claims about policing, poverty, education, or program effectiveness.

## Recommended Next Data Joins

- Reentry program capacity and completion rates
- Housing stability after release
- Workforce placement and wage records
- Supervision intensity and violation types
- Behavioral-health and substance-use service availability

## Decision Use

Use the county priority table to identify where to ask better operational questions: which services exist, who is being reached, where waitlists exist, and where outcomes diverge from similar counties.
""",
    )


def main() -> None:
    build_audio()
    build_emissions()
    build_incarceration()
    print("Built senior analyst reports for audio, emissions, and incarceration projects.")


if __name__ == "__main__":
    main()
