from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd


def make_issue(
    source_file: str,
    record_identifier: Any,
    column_name: str,
    rule_name: str,
    severity: str,
    issue_description: str,
    resolution_status: str = "Open",
) -> dict[str, Any]:
    return {
        "issue_id": "",
        "source_file": source_file,
        "record_identifier": "" if record_identifier is None else str(record_identifier),
        "column_name": column_name,
        "rule_name": rule_name,
        "severity": severity,
        "issue_description": issue_description,
        "detected_timestamp": datetime.now().replace(microsecond=0).isoformat(),
        "resolution_status": resolution_status,
    }


def find_duplicate_employee_ids(employees: pd.DataFrame) -> list[str]:
    valid_ids = employees["employee_id"].dropna()
    duplicated_ids = valid_ids[valid_ids.duplicated(keep=False)]
    return sorted(duplicated_ids.unique().tolist())


def is_valid_salary(salary: Any, min_salary: float = 30000, max_salary: float = 250000) -> bool:
    if salary is None or pd.isna(salary):
        return False
    try:
        salary_value = float(salary)
    except (TypeError, ValueError):
        return False
    return min_salary <= salary_value <= max_salary


def calculate_monthly_headcount(employees: pd.DataFrame, month_start: str) -> int:
    month_start_ts = pd.Timestamp(month_start)
    month_end_ts = month_start_ts + pd.offsets.MonthEnd(0)
    employee_dates = employees.copy()
    employee_dates["hire_date"] = pd.to_datetime(employee_dates["hire_date"], errors="coerce")
    employee_dates["termination_date"] = pd.to_datetime(
        employee_dates["termination_date"], errors="coerce"
    )
    active_mask = (employee_dates["hire_date"] <= month_end_ts) & (
        employee_dates["termination_date"].isna()
        | (employee_dates["termination_date"] > month_end_ts)
    )
    return int(employee_dates.loc[active_mask, "employee_id"].dropna().nunique())


def calculate_turnover_rate(
    beginning_headcount: float, ending_headcount: float, terminations: float
) -> float:
    average_headcount = (beginning_headcount + ending_headcount) / 2
    if average_headcount <= 0:
        return 0.0
    return terminations / average_headcount


def assign_issue_ids(issues: list[dict[str, Any]]) -> pd.DataFrame:
    columns = [
        "issue_id",
        "source_file",
        "record_identifier",
        "column_name",
        "rule_name",
        "severity",
        "issue_description",
        "detected_timestamp",
        "resolution_status",
    ]
    if not issues:
        return pd.DataFrame(columns=columns)

    for index, issue in enumerate(issues, start=1):
        issue["issue_id"] = f"DQ{index:06d}"
        issue.setdefault("detected_timestamp", datetime.now().replace(microsecond=0).isoformat())
        issue.setdefault("resolution_status", "Open")
    return pd.DataFrame(issues)


def validate_all(
    cleaned_sources: dict[str, pd.DataFrame],
    config: dict,
    required_column_issues: list[dict[str, Any]] | None = None,
) -> pd.DataFrame:
    issues: list[dict[str, Any]] = []
    if required_column_issues:
        issues.extend(required_column_issues)

    employees = cleaned_sources["employees"]
    departments = cleaned_sources["departments"]
    locations = cleaned_sources["locations"]
    jobs = cleaned_sources["job_roles"]
    compensation = cleaned_sources["compensation"]
    events = cleaned_sources["employment_events"]
    managers = cleaned_sources["manager_hierarchy"]
    workforce_plan = cleaned_sources["workforce_plan"]

    valid_employee_ids = set(employees["employee_id"].dropna())
    valid_department_codes = set(departments["department_code"].dropna())
    valid_location_codes = set(locations["location_code"].dropna())
    valid_job_codes = set(jobs["job_code"].dropna())
    end_date = pd.Timestamp(config["synthetic_data"]["end_date"])
    min_salary = config["salary"]["min_realistic"]
    max_salary = config["salary"]["max_realistic"]

    for _, row in employees.iterrows():
        record_id = row.get("source_row_id")
        employee_id = row.get("employee_id")
        hire_date = pd.to_datetime(row.get("hire_date"), errors="coerce")
        termination_date = pd.to_datetime(row.get("termination_date"), errors="coerce")

        if not employee_id:
            issues.append(
                make_issue(
                    "employees.csv",
                    record_id,
                    "employee_id",
                    "employee_id_present",
                    "Critical",
                    "Employee ID is missing in the employee master file.",
                )
            )
        if pd.isna(hire_date):
            issues.append(
                make_issue(
                    "employees.csv",
                    employee_id or record_id,
                    "hire_date",
                    "hire_date_valid",
                    "Error",
                    "Hire date is missing or not a valid date.",
                )
            )
        if pd.notna(hire_date) and pd.notna(termination_date) and termination_date < hire_date:
            issues.append(
                make_issue(
                    "employees.csv",
                    employee_id,
                    "termination_date",
                    "termination_not_before_hire",
                    "Error",
                    "Termination date is earlier than hire date.",
                )
            )
        if (
            str(row.get("employment_status")) == "Active"
            and pd.notna(termination_date)
            and termination_date <= end_date
        ):
            issues.append(
                make_issue(
                    "employees.csv",
                    employee_id,
                    "termination_date",
                    "active_employee_no_past_termination",
                    "Warning",
                    "Employee is marked active but has a past termination date.",
                )
            )
        if row.get("department_code") not in valid_department_codes:
            issues.append(
                make_issue(
                    "employees.csv",
                    employee_id or record_id,
                    "department_code",
                    "department_code_exists",
                    "Error",
                    "Employee department code does not exist in departments.csv.",
                )
            )
        if row.get("location_code") not in valid_location_codes:
            issues.append(
                make_issue(
                    "employees.csv",
                    employee_id or record_id,
                    "location_code",
                    "location_code_exists",
                    "Error",
                    "Employee location code does not exist in locations.csv.",
                )
            )
        if row.get("job_code") not in valid_job_codes:
            issues.append(
                make_issue(
                    "employees.csv",
                    employee_id or record_id,
                    "job_code",
                    "job_code_exists",
                    "Error",
                    "Employee job code does not exist in job_roles.csv.",
                )
            )

    for employee_id in find_duplicate_employee_ids(employees):
        issues.append(
            make_issue(
                "employees.csv",
                employee_id,
                "employee_id",
                "employee_id_unique",
                "Critical",
                "Employee ID appears more than once in the employee master file.",
            )
        )

    for _, row in compensation.iterrows():
        employee_id = row.get("employee_id")
        salary = row.get("annual_salary")
        if employee_id not in valid_employee_ids:
            issues.append(
                make_issue(
                    "compensation.csv",
                    employee_id,
                    "employee_id",
                    "compensation_employee_id_exists",
                    "Error",
                    "Compensation record references an employee ID not found in employees.csv.",
                )
            )
        if salary is None or pd.isna(salary):
            issues.append(
                make_issue(
                    "compensation.csv",
                    employee_id,
                    "annual_salary",
                    "salary_numeric",
                    "Error",
                    "Salary is missing or cannot be parsed as a number.",
                )
            )
        elif float(salary) <= 0:
            issues.append(
                make_issue(
                    "compensation.csv",
                    employee_id,
                    "annual_salary",
                    "salary_positive",
                    "Error",
                    "Salary must be greater than zero.",
                )
            )
        elif not is_valid_salary(salary, min_salary, max_salary):
            issues.append(
                make_issue(
                    "compensation.csv",
                    employee_id,
                    "annual_salary",
                    "salary_realistic_range",
                    "Warning",
                    f"Salary is outside the configured realistic range of {min_salary} to {max_salary}.",
                )
            )

    for _, row in events.iterrows():
        if row.get("employee_id") not in valid_employee_ids:
            issues.append(
                make_issue(
                    "employment_events.csv",
                    row.get("employee_id"),
                    "employee_id",
                    "employment_event_employee_exists",
                    "Error",
                    "Employment event references an employee ID not found in employees.csv.",
                )
            )

    for _, row in managers.iterrows():
        employee_id = row.get("employee_id")
        manager_employee_id = row.get("manager_employee_id")
        if employee_id not in valid_employee_ids:
            issues.append(
                make_issue(
                    "manager_hierarchy.csv",
                    employee_id,
                    "employee_id",
                    "manager_assignment_employee_exists",
                    "Error",
                    "Manager assignment references an employee not found in employees.csv.",
                )
            )
        if manager_employee_id and manager_employee_id not in valid_employee_ids:
            issues.append(
                make_issue(
                    "manager_hierarchy.csv",
                    employee_id,
                    "manager_employee_id",
                    "manager_employee_id_exists",
                    "Error",
                    "Manager employee ID does not exist in employees.csv.",
                )
            )

    conflicting_manager_ids = managers.groupby("employee_id")["manager_employee_id"].nunique()
    for employee_id in conflicting_manager_ids[conflicting_manager_ids > 1].index:
        issues.append(
            make_issue(
                "manager_hierarchy.csv",
                employee_id,
                "manager_employee_id",
                "single_current_manager_assignment",
                "Warning",
                "Employee has more than one manager assignment in the current hierarchy file.",
            )
        )

    for _, row in workforce_plan.iterrows():
        if row.get("department_code") not in valid_department_codes:
            issues.append(
                make_issue(
                    "workforce_plan.csv",
                    row.get("department_code"),
                    "department_code",
                    "plan_department_exists",
                    "Error",
                    "Workforce plan references a department not found in departments.csv.",
                )
            )
        if pd.isna(row.get("planned_headcount")) or row.get("planned_headcount") < 0:
            issues.append(
                make_issue(
                    "workforce_plan.csv",
                    f"{row.get('department_code')}|{row.get('plan_month')}",
                    "planned_headcount",
                    "planned_headcount_nonnegative",
                    "Error",
                    "Planned headcount must be nonnegative.",
                )
            )

    return assign_issue_ids(issues)
