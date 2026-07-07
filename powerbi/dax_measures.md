# DAX Measures

These measures assume the star schema tables are imported. If using only view exports, many of these calculations are already pre-aggregated in the views.

```DAX
Active Headcount =
SUM ( fact_employee_snapshot[headcount] )
```

```DAX
Hires =
CALCULATE (
    SUM ( fact_employment_event[event_count] ),
    fact_employment_event[event_type] = "Hire"
)
```

```DAX
Terminations =
CALCULATE (
    SUM ( fact_employment_event[event_count] ),
    fact_employment_event[event_type] = "Termination"
)
```

```DAX
Voluntary Terminations =
CALCULATE (
    [Terminations],
    fact_employment_event[termination_type] = "Voluntary"
)
```

```DAX
Involuntary Terminations =
CALCULATE (
    [Terminations],
    fact_employment_event[termination_type] = "Involuntary"
)
```

```DAX
Average Salary =
AVERAGE ( fact_compensation[annual_salary] )
```

```DAX
Total Annual Compensation =
SUM ( fact_compensation[annual_salary] )
```

```DAX
Average Tenure Years =
AVERAGE ( fact_employee_snapshot[tenure_months] ) / 12
```

```DAX
Planned Headcount =
SUM ( fact_workforce_plan[planned_headcount] )
```

```DAX
Headcount Variance =
[Active Headcount] - [Planned Headcount]
```

```DAX
Beginning Headcount =
CALCULATE (
    [Active Headcount],
    DATEADD ( dim_date[full_date], -1, MONTH )
)
```

```DAX
Average Headcount =
DIVIDE ( [Beginning Headcount] + [Active Headcount], 2 )
```

```DAX
Turnover Rate =
DIVIDE ( [Terminations], [Average Headcount] )
```

```DAX
Data Quality Issue Count =
COUNTROWS ( fact_data_quality_issue )
```

```DAX
Data Quality Error Count =
CALCULATE (
    [Data Quality Issue Count],
    fact_data_quality_issue[severity] IN { "Error", "Critical" }
)
```

```DAX
Unresolved Issues =
CALCULATE (
    [Data Quality Issue Count],
    fact_data_quality_issue[resolution_status] = "Open"
)
```

```DAX
Compensation Band Penetration =
VAR Salary = AVERAGE ( fact_compensation[annual_salary] )
VAR BandMin = AVERAGE ( dim_compensation_band[band_min] )
VAR BandMax = AVERAGE ( dim_compensation_band[band_max] )
RETURN
    DIVIDE ( Salary - BandMin, BandMax - BandMin )
```
