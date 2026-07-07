from __future__ import annotations

import re
from typing import Any

import pandas as pd


EMPLOYMENT_TYPE_MAP = {
    "fulltime": "Full-Time",
    "full": "Full-Time",
    "ft": "Full-Time",
    "parttime": "Part-Time",
    "pt": "Part-Time",
    "contractor": "Contractor",
    "contract": "Contractor",
    "cont": "Contractor",
    "intern": "Intern",
    "internship": "Intern",
    "temporary": "Temporary",
    "temp": "Temporary",
}

STATUS_MAP = {
    "active": "Active",
    "a": "Active",
    "terminated": "Terminated",
    "term": "Terminated",
    "inactive": "Terminated",
}


def standardize_column_name(column_name: str) -> str:
    cleaned_name = re.sub(r"[^0-9a-zA-Z]+", "_", column_name.strip().lower())
    return re.sub(r"_+", "_", cleaned_name).strip("_")


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.copy()
    renamed.columns = [standardize_column_name(column) for column in renamed.columns]
    return renamed


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).strip())
    return text if text else None


def title_case_text(value: Any) -> str | None:
    text = clean_text(value)
    return text.title() if text else None


def normalize_code(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    return re.sub(r"\s+", "", text.upper())


def normalize_employee_id(value: Any) -> str | None:
    text = normalize_code(value)
    if not text:
        return None
    digits = re.sub(r"[^0-9]", "", text)
    if text.startswith("E") and digits:
        return f"E{int(digits):06d}"
    if text.startswith("X") and digits:
        return f"X{int(digits):05d}"
    return text


def normalize_employment_type(value: Any) -> str:
    text = clean_text(value)
    if not text:
        return "Unknown"
    normalized_key = re.sub(r"[^a-zA-Z]", "", text).lower()
    return EMPLOYMENT_TYPE_MAP.get(normalized_key, "Unknown")


def normalize_status(value: Any) -> str:
    text = clean_text(value)
    if not text:
        return "Unknown"
    return STATUS_MAP.get(re.sub(r"[^a-zA-Z]", "", text).lower(), text.title())


def parse_date_series(series: pd.Series) -> pd.Series:
    parsed_dates = pd.to_datetime(series.replace("", pd.NA), errors="coerce")
    return parsed_dates.dt.strftime("%Y-%m-%d").where(parsed_dates.notna(), None)


def parse_salary_value(value: Any) -> float | None:
    text = clean_text(value)
    if not text:
        return None
    cleaned_value = (
        text.upper()
        .replace("USD", "")
        .replace("$", "")
        .replace(",", "")
        .replace(" ", "")
    )
    try:
        return float(cleaned_value)
    except ValueError:
        return None


def parse_boolean(value: Any) -> int:
    text = clean_text(value)
    if not text:
        return 0
    return 1 if text.lower() in {"yes", "y", "true", "1"} else 0


def clean_employees(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = standardize_column_names(df)
    cleaned.insert(0, "source_row_id", range(1, len(cleaned) + 1))
    cleaned["employee_id"] = cleaned["employee_id"].apply(normalize_employee_id)
    cleaned["first_name"] = cleaned["first_name"].apply(title_case_text)
    cleaned["last_name"] = cleaned["last_name"].apply(title_case_text)
    cleaned["gender"] = cleaned["gender"].apply(title_case_text)
    cleaned["age_group"] = cleaned["age_group"].apply(clean_text)
    cleaned["department_code"] = cleaned["department_code"].apply(normalize_code)
    cleaned["location_code"] = cleaned["location_code"].apply(normalize_code)
    cleaned["job_code"] = cleaned["job_code"].apply(normalize_code)
    cleaned["employment_type"] = cleaned["employment_type"].apply(normalize_employment_type)
    cleaned["hire_date"] = parse_date_series(cleaned["hire_date"])
    cleaned["termination_date"] = parse_date_series(cleaned.get("termination_date", pd.Series([""] * len(cleaned))))
    cleaned["employment_status"] = cleaned["employment_status"].apply(normalize_status)
    cleaned["source_system"] = cleaned.get("source_system", "Unknown").apply(title_case_text)
    cleaned["synthetic_record"] = cleaned.get("synthetic_record", "Yes").apply(parse_boolean)
    return cleaned


def clean_departments(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = standardize_column_names(df)
    cleaned.insert(0, "source_row_id", range(1, len(cleaned) + 1))
    cleaned["department_code"] = cleaned["department_code"].apply(normalize_code)
    cleaned["department_name"] = cleaned["department_name"].apply(title_case_text)
    cleaned["division"] = cleaned.get("division", "Unknown").apply(title_case_text)
    return cleaned


def clean_locations(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = standardize_column_names(df)
    cleaned.insert(0, "source_row_id", range(1, len(cleaned) + 1))
    cleaned["location_code"] = cleaned["location_code"].apply(normalize_code)
    for column in ["city", "state", "country", "region"]:
        cleaned[column] = cleaned.get(column, "Unknown").apply(title_case_text)
    return cleaned


def clean_job_roles(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = standardize_column_names(df)
    cleaned.insert(0, "source_row_id", range(1, len(cleaned) + 1))
    cleaned["job_code"] = cleaned["job_code"].apply(normalize_code)
    cleaned["job_title"] = cleaned["job_title"].apply(title_case_text)
    cleaned["job_family"] = cleaned.get("job_family", "Unknown").apply(title_case_text)
    cleaned["job_level"] = cleaned["job_level"].apply(normalize_code)
    cleaned["band_min"] = cleaned["band_min"].apply(parse_salary_value)
    cleaned["band_max"] = cleaned["band_max"].apply(parse_salary_value)
    return cleaned


def clean_compensation(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = standardize_column_names(df)
    cleaned.insert(0, "source_row_id", range(1, len(cleaned) + 1))
    cleaned["employee_id"] = cleaned["employee_id"].apply(normalize_employee_id)
    cleaned["annual_salary"] = cleaned["annual_salary"].apply(parse_salary_value)
    cleaned["bonus_target_percent"] = pd.to_numeric(
        cleaned.get("bonus_target_percent", 0), errors="coerce"
    )
    cleaned["effective_date"] = parse_date_series(cleaned["effective_date"])
    cleaned["currency"] = cleaned.get("currency", "USD").apply(normalize_code)
    cleaned["pay_frequency"] = cleaned.get("pay_frequency", "Annual").apply(title_case_text)
    return cleaned


def clean_employment_events(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = standardize_column_names(df)
    cleaned.insert(0, "source_row_id", range(1, len(cleaned) + 1))
    cleaned["employee_id"] = cleaned["employee_id"].apply(normalize_employee_id)
    cleaned["event_type"] = cleaned["event_type"].apply(title_case_text)
    cleaned["event_date"] = parse_date_series(cleaned["event_date"])
    cleaned["department_code"] = cleaned.get("department_code", "").apply(normalize_code)
    cleaned["job_code"] = cleaned.get("job_code", "").apply(normalize_code)
    cleaned["termination_type"] = cleaned.get("termination_type", "").apply(title_case_text)
    cleaned["event_reason"] = cleaned.get("event_reason", "").apply(title_case_text)
    return cleaned


def clean_manager_hierarchy(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = standardize_column_names(df)
    cleaned.insert(0, "source_row_id", range(1, len(cleaned) + 1))
    cleaned["employee_id"] = cleaned["employee_id"].apply(normalize_employee_id)
    cleaned["manager_employee_id"] = cleaned["manager_employee_id"].apply(normalize_employee_id)
    cleaned["effective_date"] = parse_date_series(cleaned["effective_date"])
    cleaned["end_date"] = parse_date_series(cleaned.get("end_date", pd.Series([""] * len(cleaned))))
    return cleaned


def clean_workforce_plan(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = standardize_column_names(df)
    cleaned.insert(0, "source_row_id", range(1, len(cleaned) + 1))
    cleaned["plan_month"] = parse_date_series(cleaned["plan_month"])
    cleaned["department_code"] = cleaned["department_code"].apply(normalize_code)
    cleaned["department_name"] = cleaned.get("department_name", "").apply(title_case_text)
    cleaned["planned_headcount"] = pd.to_numeric(cleaned["planned_headcount"], errors="coerce")
    cleaned["plan_version"] = cleaned.get("plan_version", "Plan").apply(clean_text)
    return cleaned


def clean_sources(sources: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    return {
        "employees": clean_employees(sources["employees"]),
        "compensation": clean_compensation(sources["compensation"]),
        "departments": clean_departments(sources["departments"]),
        "locations": clean_locations(sources["locations"]),
        "job_roles": clean_job_roles(sources["job_roles"]),
        "employment_events": clean_employment_events(sources["employment_events"]),
        "manager_hierarchy": clean_manager_hierarchy(sources["manager_hierarchy"]),
        "workforce_plan": clean_workforce_plan(sources["workforce_plan"]),
    }
