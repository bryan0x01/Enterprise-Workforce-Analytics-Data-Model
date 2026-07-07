# Metric Definitions

This project uses month-end workforce reporting logic. The monthly snapshot fact stores one row per active employee per month with `headcount = 1`.

| Metric | Definition |
|---|---|
| Active headcount | Count of employees active at the end of the selected month. An employee is active when hire date is on or before month end and termination date is blank or after month end. |
| Beginning headcount | Ending headcount from the previous month. For the first month in the dataset, beginning headcount is set equal to ending headcount. |
| Ending headcount | Active headcount at the end of the selected month. |
| Average headcount | `(Beginning headcount + Ending headcount) / 2`. |
| Hires | Count of employment events where `event_type = Hire`. |
| Terminations | Count of employment events where `event_type = Termination`. |
| Voluntary terminations | Count of termination events where `termination_type = Voluntary`. |
| Involuntary terminations | Count of termination events where `termination_type = Involuntary`. |
| Turnover rate | `Terminations / Average headcount`. This avoids using only ending headcount, which can overstate or understate turnover when headcount changes during the month. |
| Average salary | Average annual salary for employees with valid compensation records. |
| Total annual compensation | Sum of annual salary. Bonus target is available separately as total target compensation in `fact_compensation`. |
| Average tenure | Average tenure in years: `AVG(tenure_months / 12.0)` for active employees. |
| Actual headcount | Active headcount from `fact_employee_snapshot`. |
| Planned headcount | Planned headcount from `fact_workforce_plan`. |
| Headcount variance | `Actual headcount - Planned headcount`. Positive means actual is above plan. |
| Compensation-band penetration | `(Annual salary - Band minimum) / (Band maximum - Band minimum)`, usually shown only when both band limits are available. |
| Data-quality error count | Count of validation issues where severity is `Error` or `Critical`. |
| Validation pass rate | `(Validation checks passed / Total validation checks evaluated)`. In this project, issue counts are stored directly, so a report can approximate this as `1 - Issue count / Records checked` for selected validation groups. |

## Turnover Example

If a department starts the month with 100 employees, ends with 90 employees, and has 5 terminations:

```text
Average headcount = (100 + 90) / 2 = 95
Turnover rate = 5 / 95 = 5.26%
```

Using ending headcount only would give `5 / 90 = 5.56%`, which is less consistent when workforce size is changing.
