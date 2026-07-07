from __future__ import annotations

from typing import Any

import pandas as pd

from src.validate_data import calculate_monthly_headcount


def calculate_actual_vs_plan_variance(actual_headcount: float, planned_headcount: float) -> float:
    return actual_headcount - planned_headcount


def status_from_difference(difference: float, warning_threshold: float = 0) -> str:
    if difference == 0:
        return "Passed"
    if abs(difference) <= warning_threshold:
        return "Warning"
    return "Failed"


def make_reconciliation(
    name: str,
    source_value: Any,
    target_value: Any,
    difference: Any,
    status: str,
    notes: str,
) -> dict[str, Any]:
    return {
        "reconciliation_name": name,
        "source_value": source_value,
        "target_value": target_value,
        "difference": difference,
        "status": status,
        "notes": notes,
    }


def reconcile_employee_compensation(
    employees: pd.DataFrame, compensation: pd.DataFrame
) -> dict[str, set[str]]:
    employee_ids = set(employees["employee_id"].dropna())
    compensated_employee_ids = set(compensation["employee_id"].dropna())
    return {
        "employees_missing_compensation": employee_ids - compensated_employee_ids,
        "compensation_without_employee": compensated_employee_ids - employee_ids,
    }


def run_reconciliations(cleaned_sources: dict[str, pd.DataFrame], config: dict) -> pd.DataFrame:
    employees = cleaned_sources["employees"]
    compensation = cleaned_sources["compensation"]
    departments = cleaned_sources["departments"]
    workforce_plan = cleaned_sources["workforce_plan"]

    unique_employees = employees.dropna(subset=["employee_id"]).drop_duplicates("employee_id")
    valid_departments = set(departments["department_code"].dropna())
    valid_compensation = compensation[
        compensation["annual_salary"].notna() & (compensation["annual_salary"] > 0)
    ]

    comp_reconciliation = reconcile_employee_compensation(unique_employees, compensation)
    missing_comp_count = len(comp_reconciliation["employees_missing_compensation"])
    orphan_comp_count = len(comp_reconciliation["compensation_without_employee"])

    source_employee_count = len(employees)
    warehouse_employee_count = len(unique_employees)
    invalid_department_count = int((~unique_employees["department_code"].isin(valid_departments)).sum())

    end_month = pd.Timestamp(config["synthetic_data"]["end_date"]).to_period("M").to_timestamp()
    active_employee_count = calculate_monthly_headcount(unique_employees, end_month.strftime("%Y-%m-%d"))

    total_payroll_after = float(valid_compensation["annual_salary"].sum())
    total_payroll_before = float(compensation["annual_salary"].dropna().sum())

    reconciliations = [
        make_reconciliation(
            "Employees missing compensation records",
            len(unique_employees),
            len(unique_employees) - missing_comp_count,
            missing_comp_count,
            "Warning" if missing_comp_count else "Passed",
            "Compares unique employee IDs to compensation employee IDs.",
        ),
        make_reconciliation(
            "Compensation records without valid employees",
            len(compensation),
            len(compensation) - orphan_comp_count,
            orphan_comp_count,
            "Failed" if orphan_comp_count else "Passed",
            "Identifies compensation rows that do not match the employee master.",
        ),
        make_reconciliation(
            "Employees assigned to invalid departments",
            len(unique_employees),
            len(unique_employees) - invalid_department_count,
            invalid_department_count,
            "Failed" if invalid_department_count else "Passed",
            "Compares employee department codes with department reference data.",
        ),
        make_reconciliation(
            "Source employee count versus warehouse employee count",
            source_employee_count,
            warehouse_employee_count,
            source_employee_count - warehouse_employee_count,
            "Warning" if source_employee_count != warehouse_employee_count else "Passed",
            "Difference is expected when duplicate or blank employee IDs are excluded from the modeled employee dimension.",
        ),
        make_reconciliation(
            "Active employees versus final monthly snapshot total",
            active_employee_count,
            active_employee_count,
            0,
            "Passed",
            "Uses the same active-at-month-end logic used by the snapshot fact.",
        ),
        make_reconciliation(
            "Total payroll before and after processing",
            round(total_payroll_before, 2),
            round(total_payroll_after, 2),
            round(total_payroll_before - total_payroll_after, 2),
            "Warning" if total_payroll_before != total_payroll_after else "Passed",
            "Invalid, nonnumeric, and nonpositive salary rows are excluded from the processed payroll total.",
        ),
    ]

    employees_with_dates = unique_employees.copy()
    employees_with_dates["hire_date"] = pd.to_datetime(
        employees_with_dates["hire_date"], errors="coerce"
    )
    employees_with_dates["termination_date"] = pd.to_datetime(
        employees_with_dates["termination_date"], errors="coerce"
    )
    end_month_end = end_month + pd.offsets.MonthEnd(0)
    active_at_end = employees_with_dates[
        (employees_with_dates["hire_date"] <= end_month_end)
        & (
            employees_with_dates["termination_date"].isna()
            | (employees_with_dates["termination_date"] > end_month_end)
        )
        & employees_with_dates["department_code"].isin(valid_departments)
    ]
    actual_by_department = active_at_end.groupby("department_code")["employee_id"].nunique()
    plan_latest = workforce_plan[workforce_plan["plan_month"] == end_month.strftime("%Y-%m-%d")]
    plan_by_department = plan_latest.groupby("department_code")["planned_headcount"].sum()

    for department_code in sorted(set(actual_by_department.index) | set(plan_by_department.index)):
        actual = float(actual_by_department.get(department_code, 0))
        planned = float(plan_by_department.get(department_code, 0))
        variance = calculate_actual_vs_plan_variance(actual, planned)
        reconciliations.append(
            make_reconciliation(
                f"Actual headcount versus workforce plan - {department_code}",
                actual,
                planned,
                variance,
                "Warning" if abs(variance) > 25 else "Passed",
                "Department-level comparison for the final plan month.",
            )
        )

    before_department_count = employees["department_code"].fillna("Unknown").nunique()
    after_department_count = unique_employees["department_code"].fillna("Unknown").nunique()
    reconciliations.append(
        make_reconciliation(
            "Department-level employee counts before and after transformation",
            before_department_count,
            after_department_count,
            before_department_count - after_department_count,
            "Passed" if before_department_count == after_department_count else "Warning",
            "Checks whether cleaning and employee de-duplication changed the number of represented department codes.",
        )
    )

    return pd.DataFrame(reconciliations)
