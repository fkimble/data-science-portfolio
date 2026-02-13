# Audio Storage System (Access → Oracle Migration)



## Project Overview
This project simulates a real Access-to-Oracle migration workflow using a flat “Access export” table, then:
1) cleans messy text fields,  
2) normalizes the structure (3NF-style lookup tables), and  
3) builds a regression model to estimate monthly storage cost from file metadata.

The notebook is designed to be a portfolio piece you can demo quickly at a career fair.

## Dataset
This repo includes a synthetic Access export so everything runs end-to-end.

### Data Dictionary (Access Export)
| Column | Meaning |
|---|---|
| record_id | Unique record identifier |
| file_name | Audio file name |
| department | Owning department (messy strings included intentionally) |
| recording_type | Category (incident, training, etc.) |
| duration_sec | Recording duration in seconds |
| sample_rate_hz | Sample rate (Hz) |
| channels | Mono/Stereo (1/2) |
| created_date | Record creation date |
| created_by | Creator role |
| file_size_mb | Estimated file size |
| storage_tier | Standard / Infrequent / Archive |
| storage_cost_usd_month | Estimated monthly storage cost **target** |

## What’s inside
- `notebooks/01_audio_migration_etl_model.ipynb` — ETL, normalization, EDA, model
- `schema/normalized_schema.sql` — example normalized schema
- `reports/` — cleaned + normalized outputs produced by the notebook

## How to run
Open the notebook and run all cells. Requires: pandas, numpy, matplotlib, seaborn, scikit-learn, scipy.
