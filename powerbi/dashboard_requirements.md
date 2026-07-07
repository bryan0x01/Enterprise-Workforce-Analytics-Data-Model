# Power BI Dashboard Requirements

## Page 1: Executive Workforce Overview

Purpose: Give a high-level view of workforce size, cost, tenure, and plan performance.

Include:

- Active headcount
- Total annual compensation
- Average salary
- Average tenure
- Hires
- Terminations
- Headcount trend
- Headcount by department
- Headcount by location
- Actual versus planned headcount

Recommended data:

- `vw_current_workforce`
- `vw_monthly_headcount`
- `vw_turnover_summary`
- `vw_actual_vs_plan`

## Page 2: Workforce Movement

Purpose: Show hiring, termination, and net movement over time.

Include:

- Monthly hires
- Monthly terminations
- Net workforce change
- Turnover trend
- Termination type
- Department movement
- Job-level movement

Recommended data:

- `vw_hires_and_terminations`
- `vw_turnover_summary`
- `fact_employment_event` with dimensions, if using the star schema

## Page 3: Compensation Analysis

Purpose: Analyze pay levels and compensation-band alignment.

Include:

- Average salary
- Total compensation
- Salary by department
- Salary by job level
- Compensation-band distribution
- Employees outside compensation bands

Recommended data:

- `vw_compensation_summary`
- `fact_compensation`
- `dim_compensation_band`
- `dim_job`

## Page 4: Organizational Analysis

Purpose: Understand department, manager, job-family, employment-type, and location structure.

Include:

- Department hierarchy
- Manager span of control
- Headcount by manager
- Headcount by job family
- Employment-type distribution
- Location distribution

Recommended data:

- `vw_current_workforce`
- `vw_department_workforce`
- `vw_location_workforce`

## Page 5: Workforce Planning

Purpose: Compare actual workforce levels against plan.

Include:

- Actual versus planned headcount
- Variance by month
- Variance by department
- Departments above plan
- Departments below plan
- Hiring demand

Recommended data:

- `vw_actual_vs_plan`
- `fact_workforce_plan`
- `fact_employee_snapshot`
- `dim_department`
- `dim_date`

## Page 6: Data Quality

Purpose: Make validation and reconciliation issues visible instead of hiding them.

Include:

- Total issues
- Issues by severity
- Issues by source file
- Issues by validation rule
- Validation pass rate
- Reconciliation status
- Unresolved issues

Recommended data:

- `vw_data_quality_summary`
- `fact_data_quality_issue`
- `reconciliation_summary`
