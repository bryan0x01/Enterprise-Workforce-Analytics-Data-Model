# Project Walkthrough

## What The Project Does

This project starts with synthetic HR source files and turns them into clean reporting data. The goal is not just to make a dashboard dataset, but to show the steps that usually happen before a dashboard is trustworthy: cleaning, validation, reconciliation, dimensional modeling, and metric definitions.

## Source Data

The pipeline generates eight raw files:

- `employees.csv`
- `compensation.csv`
- `departments.csv`
- `locations.csv`
- `job_roles.csv`
- `employment_events.csv`
- `manager_hierarchy.csv`
- `workforce_plan.csv`

The raw files intentionally include issues such as duplicate employees, invalid references, inconsistent labels, and salary values stored as text. This gives the validation and reconciliation code something meaningful to catch.

## Cleaning

The cleaning layer standardizes columns, trims text, normalizes IDs, parses dates, cleans salary fields, and maps employment type labels. For example, `FT`, `full-time`, and `Full Time` all become `Full-Time`.

The code does not simply drop problem records. It preserves records where possible and records issues for review.

## Validation

Validation rules check whether key business rules are being followed. Examples include:

- Employee IDs should be present and unique.
- Termination dates should not be before hire dates.
- Department, location, job, and manager references should exist.
- Salary should be numeric, positive, and realistic.
- Workforce plan headcount should not be negative.

Validation results are stored in `fact_data_quality_issue`.

## Reconciliation

Reconciliation checks compare source and target values. The project checks examples like:

- Employees missing compensation.
- Compensation records without valid employees.
- Source employee counts versus modeled warehouse employees.
- Total payroll before and after processing.
- Actual headcount versus planned headcount by department.

These results are stored in `reconciliation_summary` and exported for Power BI.

## Data Model

The warehouse uses a star schema. Dimensions hold descriptive fields, and facts hold measurable events or snapshots.

The main trend table is `fact_employee_snapshot`, which has one row per active employee per month. This makes monthly headcount and tenure reporting straightforward.

## Reporting Layer

SQL views provide business-friendly datasets so a Power BI user does not need to understand every staging or warehouse table. For example, `vw_current_workforce` combines employee, department, job, manager, location, tenure, and compensation fields into one current workforce dataset.
