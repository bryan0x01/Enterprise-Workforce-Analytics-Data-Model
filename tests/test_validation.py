import pandas as pd

from src.validate_data import (
    calculate_monthly_headcount,
    calculate_turnover_rate,
    find_duplicate_employee_ids,
    is_valid_salary,
    validate_all,
)


def test_duplicate_employee_detection_returns_duplicate_ids():
    employees = pd.DataFrame({"employee_id": ["E000001", "E000002", "E000001", None]})

    assert find_duplicate_employee_ids(employees) == ["E000001"]


def test_salary_validation_checks_numeric_positive_realistic_range():
    assert is_valid_salary(75000, 30000, 250000)
    assert not is_valid_salary(-5000, 30000, 250000)
    assert not is_valid_salary(999999, 30000, 250000)
    assert not is_valid_salary(None, 30000, 250000)


def test_validate_all_flags_termination_before_hire():
    cleaned_sources = {
        "employees": pd.DataFrame(
            [
                {
                    "source_row_id": 1,
                    "employee_id": "E000001",
                    "first_name": "Ava",
                    "last_name": "Smith",
                    "gender": "Female",
                    "age_group": "25-34",
                    "department_code": "ENG",
                    "location_code": "NYC",
                    "job_code": "ENG1",
                    "employment_type": "Full-Time",
                    "hire_date": "2024-03-01",
                    "termination_date": "2024-02-01",
                    "employment_status": "Terminated",
                    "source_system": "HRIS",
                    "synthetic_record": 1,
                }
            ]
        ),
        "departments": pd.DataFrame(
            [{"source_row_id": 1, "department_code": "ENG", "department_name": "Engineering", "division": "Technology"}]
        ),
        "locations": pd.DataFrame(
            [{"source_row_id": 1, "location_code": "NYC", "city": "New York", "state": "NY", "country": "United States", "region": "Northeast"}]
        ),
        "job_roles": pd.DataFrame(
            [{"source_row_id": 1, "job_code": "ENG1", "job_title": "Engineer", "job_family": "Engineering", "job_level": "L1", "band_min": 70000, "band_max": 95000}]
        ),
        "compensation": pd.DataFrame(
            [{"source_row_id": 1, "employee_id": "E000001", "annual_salary": 80000, "bonus_target_percent": 5, "effective_date": "2024-03-01", "currency": "USD", "pay_frequency": "Annual"}]
        ),
        "employment_events": pd.DataFrame(
            [{"source_row_id": 1, "employee_id": "E000001", "event_type": "Hire", "event_date": "2024-03-01", "department_code": "ENG", "job_code": "ENG1", "termination_type": None, "event_reason": "New Hire"}]
        ),
        "manager_hierarchy": pd.DataFrame(
            [{"source_row_id": 1, "employee_id": "E000001", "manager_employee_id": None, "effective_date": "2024-03-01", "end_date": None}]
        ),
        "workforce_plan": pd.DataFrame(
            [{"source_row_id": 1, "plan_month": "2024-03-01", "department_code": "ENG", "department_name": "Engineering", "planned_headcount": 1, "plan_version": "Plan"}]
        ),
    }
    config = {
        "synthetic_data": {"end_date": "2024-12-31"},
        "salary": {"min_realistic": 30000, "max_realistic": 250000},
    }

    issues = validate_all(cleaned_sources, config)

    assert "termination_not_before_hire" in set(issues["rule_name"])


def test_headcount_and_turnover_calculation():
    employees = pd.DataFrame(
        [
            {"employee_id": "E000001", "hire_date": "2024-01-01", "termination_date": None},
            {"employee_id": "E000002", "hire_date": "2024-01-15", "termination_date": "2024-03-01"},
            {"employee_id": "E000003", "hire_date": "2024-04-01", "termination_date": None},
        ]
    )

    assert calculate_monthly_headcount(employees, "2024-02-01") == 2
    assert calculate_monthly_headcount(employees, "2024-03-01") == 1
    assert calculate_turnover_rate(100, 90, 10) == 10 / 95
