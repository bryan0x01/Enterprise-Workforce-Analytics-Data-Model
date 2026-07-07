# Power BI Setup

This project does not create a `.pbix` file. The report should be built manually from the generated outputs so the model and visuals can be inspected.

## Option 1: Import CSV Exports

1. Run the pipeline:

```bash
python src/run_pipeline.py
```

2. Open Power BI Desktop.
3. Select **Get Data > Text/CSV**.
4. Import CSV files from `data/output`.
5. For a fast dashboard build, start with the view exports:
   - `vw_current_workforce.csv`
   - `vw_monthly_headcount.csv`
   - `vw_hires_and_terminations.csv`
   - `vw_turnover_summary.csv`
   - `vw_compensation_summary.csv`
   - `vw_tenure_distribution.csv`
   - `vw_department_workforce.csv`
   - `vw_location_workforce.csv`
   - `vw_actual_vs_plan.csv`
   - `vw_data_quality_summary.csv`

This option is easiest because the views already use business-friendly field names.

## Option 2: Import The Star Schema

Import these tables from `data/output`:

- Dimensions: all `dim_*.csv` files
- Facts: all `fact_*.csv` files
- Optional: `reconciliation_summary.csv`

Create relationships:

| From fact table | Field | To dimension | Field |
|---|---|---|---|
| fact_employee_snapshot | employee_key | dim_employee | employee_key |
| fact_employee_snapshot | snapshot_month_key | dim_date | date_key |
| fact_employee_snapshot | department_key | dim_department | department_key |
| fact_employee_snapshot | location_key | dim_location | location_key |
| fact_employee_snapshot | job_key | dim_job | job_key |
| fact_employee_snapshot | manager_key | dim_manager | manager_key |
| fact_employee_snapshot | employment_type_key | dim_employment_type | employment_type_key |
| fact_employment_event | event_date_key | dim_date | date_key |
| fact_employment_event | employee_key | dim_employee | employee_key |
| fact_employment_event | department_key | dim_department | department_key |
| fact_employment_event | job_key | dim_job | job_key |
| fact_compensation | employee_key | dim_employee | employee_key |
| fact_compensation | effective_date_key | dim_date | date_key |
| fact_compensation | compensation_band_key | dim_compensation_band | compensation_band_key |
| fact_workforce_plan | plan_month_key | dim_date | date_key |
| fact_workforce_plan | department_key | dim_department | department_key |

Use one-to-many relationships from dimensions to facts. Keep filter direction single unless a specific visual needs otherwise.

## Date Handling

Use `dim_date` as the main date table if building from the star schema. In Power BI, mark it as a date table using `full_date`.

For view-based reports, the exported views already include month fields.

## Suggested Report Pages

The report specification is in `powerbi/dashboard_requirements.md`. Recommended visuals are in `powerbi/recommended_visuals.md`, and DAX measures are in `powerbi/dax_measures.md`.
