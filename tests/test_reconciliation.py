import pandas as pd

from src.reconcile_data import calculate_actual_vs_plan_variance, reconcile_employee_compensation


def test_employee_compensation_reconciliation_finds_missing_and_orphans():
    employees = pd.DataFrame({"employee_id": ["E000001", "E000002", "E000003"]})
    compensation = pd.DataFrame({"employee_id": ["E000001", "E000003", "X00001"]})

    result = reconcile_employee_compensation(employees, compensation)

    assert result["employees_missing_compensation"] == {"E000002"}
    assert result["compensation_without_employee"] == {"X00001"}


def test_actual_vs_plan_variance():
    assert calculate_actual_vs_plan_variance(105, 100) == 5
    assert calculate_actual_vs_plan_variance(92, 100) == -8
