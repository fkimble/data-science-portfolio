# Data Science Portfolio

This portfolio is a curated set of analytics and data-systems projects focused on healthcare, civic operations, public-sector decision support, and database migration. The projects are intentionally framed as end-to-end analyst work: define the decision, validate the data, produce metrics, communicate findings, and package outputs a stakeholder could actually use.

## Portfolio Positioning

I use this repository to demonstrate a mid-senior data analyst workflow:

- translating messy operational data into decision-ready metrics
- building reproducible cleaning, validation, and reporting pipelines
- defining KPI dictionaries and dashboard specs
- separating descriptive analysis from unsupported causal claims
- creating executive summaries, risk rankings, and recommendation backlogs
- using Python, SQL thinking, and data storytelling together

All datasets in this repository are synthetic unless noted otherwise.

## Highlighted Projects

### [ClaimFlow Parity Lab](claimflow-parity-lab)

Synthetic healthcare prior-authorization and claims-denial analytics project. It detects denial drift, access-parity gaps, reimbursement at risk, and ranked operational interventions. Includes CLI, tests, CI-ready package structure, sample reports, and SVG charts.

**Analyst signal:** healthcare operations analytics, KPI design, synthetic data generation, validation, parity analysis, executive reporting.

### [Audio Storage System Migration](audio-storage-system-migration)

Access-to-Oracle migration simulation for audio records. The upgraded version includes row-level migration controls, normalized schema design, department-level storage exposure, storage-tier cost review, reconciliation SQL, and executive migration reporting.

**Analyst signal:** data migration controls, SQL schema design, 3NF normalization, data quality, operational cost analysis.

### [Emissions Decision Support System](emissions-decision-support-system)

Maryland county emissions analysis for decision support. The upgraded version includes county/sector standardization, emissions intensity metrics, priority ranking, yearly trend outputs, metric dictionary, and Power BI dashboard specification.

**Analyst signal:** public-sector analytics, KPI normalization, dashboard design, data governance, stakeholder recommendations.

### [Incarceration Trends Maryland](incarceration-trends-maryland)

Synthetic Maryland incarceration and recidivism analysis. The upgraded version reframes the notebook as a public-sector reentry analytics brief, with county priority ranking, risk-index definitions, driver correlations, policy guardrails, and a policy brief.

**Analyst signal:** civic analytics, policy-safe interpretation, correlation guardrails, risk segmentation, executive communication.

## Repository Structure

```text
.
├── audio-storage-system-migration/
├── claimflow-parity-lab/
├── emissions-decision-support-system/
├── incarceration-trends-maryland/
└── scripts/
    └── build_portfolio_reports.py
```

## Reproducible Build

From the repository root:

```powershell
python -m pip install pandas numpy
python scripts/build_portfolio_reports.py
$env:PYTHONPATH = "claimflow-parity-lab"
python -m unittest discover -s claimflow-parity-lab/tests
```

The report builder regenerates the senior analyst artifacts under each existing project `reports/` folder.

## Core Skills Represented

- Python: pandas, NumPy, data validation, synthetic data generation
- SQL/data modeling: Oracle-style schema design, reconciliation queries, 3NF thinking
- Analytics: KPI definition, trend analysis, cohort/group comparisons, ranking models
- Communication: executive summaries, metric dictionaries, dashboard specs, policy briefs
- Data governance: control totals, label standardization, quality profiles, interpretation guardrails

## Purpose

This portfolio is meant to show that I can go beyond isolated notebooks and build decision-support assets: the kind of analysis package a stakeholder, manager, or technical reviewer can understand, audit, and reuse.
