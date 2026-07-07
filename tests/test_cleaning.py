import pandas as pd

from src.clean_data import (
    clean_text,
    normalize_employment_type,
    parse_date_series,
    parse_salary_value,
    standardize_column_names,
)


def test_standardize_column_names():
    df = pd.DataFrame(columns=[" Employee ID ", "Annual Salary ($)", "Hire-Date"])

    cleaned = standardize_column_names(df)

    assert list(cleaned.columns) == ["employee_id", "annual_salary", "hire_date"]


def test_clean_text_collapses_spaces_and_trims():
    assert clean_text("  Human   Resources  ") == "Human Resources"


def test_employment_type_mapping_variants():
    values = ["Full Time", "full-time", "FT", " Full-Time "]

    normalized = [normalize_employment_type(value) for value in values]

    assert normalized == ["Full-Time", "Full-Time", "Full-Time", "Full-Time"]


def test_salary_text_parses_common_formats():
    assert parse_salary_value("$85,000") == 85000
    assert parse_salary_value("USD 92,500") == 92500
    assert parse_salary_value("not available") is None


def test_parse_date_series_invalid_dates_become_missing():
    parsed = parse_date_series(pd.Series(["2024-01-15", "not-a-date"]))

    assert parsed.iloc[0] == "2024-01-15"
    assert parsed.iloc[1] is None
