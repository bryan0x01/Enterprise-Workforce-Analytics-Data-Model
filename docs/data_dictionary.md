# Data Dictionary

This dictionary focuses on the major fields used for modeling and reporting. Technical staging columns are intentionally limited.

| Table | Column | Type | Description | Example | Required | Key | Source |
|---|---|---|---|---|---|---|---|
| dim_employee | employee_key | Integer | Surrogate key for employee dimension. | 102 | Yes | Primary key | Warehouse |
| dim_employee | employee_id | Text | Synthetic source employee identifier. | E000102 | Yes | Business key | employees.csv |
| dim_employee | full_name | Text | Cleaned employee display name. | Maya Chen | No | No | employees.csv |
| dim_employee | gender | Text | Synthetic demographic field. | Female | No | No | employees.csv |
| dim_employee | age_group | Text | Synthetic age group bucket. | 25-34 | No | No | employees.csv |
| dim_employee | hire_date | Text | Employee hire date. | 2022-06-15 | Yes | No | employees.csv |
| dim_employee | termination_date | Text | Termination date when available. | 2024-09-30 | No | No | employees.csv |
| dim_employee | employment_status | Text | Cleaned employee status. | Active | Yes | No | employees.csv |
| dim_department | department_key | Integer | Surrogate key for department. | 4 | Yes | Primary key | Warehouse |
| dim_department | department_code | Text | Department business code. | ENG | Yes | Business key | departments.csv |
| dim_department | department_name | Text | Cleaned department name. | Engineering | Yes | No | departments.csv |
| dim_department | division | Text | Higher-level organization group. | Technology | No | No | departments.csv |
| dim_location | location_key | Integer | Surrogate key for location. | 2 | Yes | Primary key | Warehouse |
| dim_location | location_code | Text | Location business code. | NYC | Yes | Business key | locations.csv |
| dim_location | city | Text | City or remote label. | New York | Yes | No | locations.csv |
| dim_location | region | Text | Regional grouping. | Northeast | No | No | locations.csv |
| dim_job | job_key | Integer | Surrogate key for job. | 8 | Yes | Primary key | Warehouse |
| dim_job | job_code | Text | Job role business code. | ENG2 | Yes | Business key | job_roles.csv |
| dim_job | job_title | Text | Cleaned job title. | Software Engineer II | Yes | No | job_roles.csv |
| dim_job | job_family | Text | Job family for reporting. | Engineering | No | No | job_roles.csv |
| dim_job | job_level | Text | Job level. | L2 | No | No | job_roles.csv |
| dim_job | band_min | Real | Minimum salary for the job role. | 90000 | No | No | job_roles.csv |
| dim_job | band_max | Real | Maximum salary for the job role. | 125000 | No | No | job_roles.csv |
| dim_manager | manager_key | Integer | Surrogate key for manager. | 12 | Yes | Primary key | Warehouse |
| dim_manager | manager_employee_id | Text | Manager source employee ID. | E000045 | No | Business key | manager_hierarchy.csv |
| dim_manager | manager_name | Text | Manager display name when found. | Jordan Rivera | No | No | employees.csv |
| dim_employment_type | employment_type_key | Integer | Surrogate key for employment type. | 1 | Yes | Primary key | Warehouse |
| dim_employment_type | employment_type | Text | Normalized employment type. | Full-Time | Yes | Business key | employees.csv |
| dim_date | date_key | Integer | Date key in YYYYMMDD format. | 20250101 | Yes | Primary key | Generated |
| dim_date | full_date | Text | Calendar date. | 2025-01-01 | No | No | Generated |
| dim_date | month_start_date | Text | First day of the month. | 2025-01-01 | No | No | Generated |
| dim_compensation_band | compensation_band_key | Integer | Surrogate key for compensation band. | 3 | Yes | Primary key | Warehouse |
| dim_compensation_band | compensation_band | Text | Salary band label. | Senior Band | Yes | Business key | Warehouse |
| fact_employee_snapshot | snapshot_key | Integer | Surrogate key for monthly employee snapshot row. | 9001 | Yes | Primary key | Warehouse |
| fact_employee_snapshot | snapshot_month_key | Integer | Month start date key. | 20251201 | Yes | Foreign key | dim_date |
| fact_employee_snapshot | employee_key | Integer | Employee dimension key. | 102 | Yes | Foreign key | dim_employee |
| fact_employee_snapshot | headcount | Integer | Snapshot headcount value, usually 1 per row. | 1 | Yes | No | Warehouse |
| fact_employee_snapshot | tenure_months | Integer | Months between hire date and snapshot month end. | 28 | No | No | Warehouse |
| fact_employment_event | event_key | Integer | Surrogate key for event row. | 410 | Yes | Primary key | Warehouse |
| fact_employment_event | event_date_key | Integer | Date key for the event. | 20240415 | Yes | Foreign key | dim_date |
| fact_employment_event | event_type | Text | Event category. | Hire | Yes | No | employment_events.csv |
| fact_employment_event | termination_type | Text | Voluntary or involuntary termination type. | Voluntary | No | No | employment_events.csv |
| fact_employment_event | event_count | Integer | Count value for aggregation. | 1 | Yes | No | Warehouse |
| fact_compensation | compensation_key | Integer | Surrogate key for compensation row. | 250 | Yes | Primary key | Warehouse |
| fact_compensation | effective_date_key | Integer | Effective date key for compensation. | 20250301 | Yes | Foreign key | dim_date |
| fact_compensation | annual_salary | Real | Cleaned annual salary. | 95000 | No | No | compensation.csv |
| fact_compensation | total_target_compensation | Real | Annual salary plus bonus target percentage. | 104500 | No | No | compensation.csv |
| fact_workforce_plan | plan_key | Integer | Surrogate key for plan row. | 88 | Yes | Primary key | Warehouse |
| fact_workforce_plan | plan_month_key | Integer | Month date key for the plan. | 20251201 | Yes | Foreign key | dim_date |
| fact_workforce_plan | planned_headcount | Real | Planned headcount value. | 215 | Yes | No | workforce_plan.csv |
| fact_data_quality_issue | issue_key | Integer | Surrogate key for validation issue. | 42 | Yes | Primary key | Warehouse |
| fact_data_quality_issue | issue_id | Text | Human-readable issue ID. | DQ000042 | Yes | Business key | Validation |
| fact_data_quality_issue | source_file | Text | Source file where issue was found. | employees.csv | Yes | No | Validation |
| fact_data_quality_issue | rule_name | Text | Validation rule that produced the issue. | employee_id_unique | Yes | No | Validation |
| fact_data_quality_issue | severity | Text | Warning, Error, or Critical. | Error | Yes | No | Validation |
| fact_data_quality_issue | resolution_status | Text | Current issue status. | Open | Yes | No | Validation |
| reconciliation_summary | reconciliation_name | Text | Name of reconciliation check. | Employees missing compensation records | Yes | No | Reconciliation |
| reconciliation_summary | source_value | Real | Source side of comparison. | 2982 | No | No | Reconciliation |
| reconciliation_summary | target_value | Real | Target side of comparison. | 2870 | No | No | Reconciliation |
| reconciliation_summary | difference | Real | Source minus target or actual minus plan depending on check. | 112 | No | No | Reconciliation |
| reconciliation_summary | status | Text | Passed, Warning, or Failed. | Warning | Yes | No | Reconciliation |
