from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils import project_path


SOURCE_FILES = {
    "employees": "employees.csv",
    "compensation": "compensation.csv",
    "departments": "departments.csv",
    "locations": "locations.csv",
    "job_roles": "job_roles.csv",
    "employment_events": "employment_events.csv",
    "manager_hierarchy": "manager_hierarchy.csv",
    "workforce_plan": "workforce_plan.csv",
}

REQUIRED_COLUMNS = {
    "employees": [
        "Employee ID",
        "First Name",
        "Last Name",
        "Department Code",
        "Location Code",
        "Job Code",
        "Employment Type",
        "Hire Date",
        "Employment Status",
    ],
    "compensation": ["Employee ID", "Annual Salary", "Effective Date"],
    "departments": ["Department Code", "Department Name"],
    "locations": ["Location Code", "City", "Country"],
    "job_roles": ["Job Code", "Job Title", "Job Level", "Band Min", "Band Max"],
    "employment_events": ["Employee ID", "Event Type", "Event Date"],
    "manager_hierarchy": ["Employee ID", "Manager Employee ID", "Effective Date"],
    "workforce_plan": ["Plan Month", "Department Code", "Planned Headcount"],
}


def load_source_files(config: dict) -> dict[str, pd.DataFrame]:
    raw_dir = project_path(config["paths"]["raw_data_dir"])
    sources = {}

    for source_name, file_name in SOURCE_FILES.items():
        file_path = raw_dir / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"Required source file is missing: {file_path}")
        sources[source_name] = pd.read_csv(file_path, dtype=str, keep_default_na=False)

    return sources


def find_missing_required_columns(sources: dict[str, pd.DataFrame]) -> list[dict[str, str]]:
    missing_columns = []
    for source_name, required_columns in REQUIRED_COLUMNS.items():
        source_columns = set(sources[source_name].columns)
        for column in required_columns:
            if column not in source_columns:
                missing_columns.append(
                    {
                        "source_file": SOURCE_FILES[source_name],
                        "record_identifier": "FILE",
                        "column_name": column,
                        "rule_name": "required_column_exists",
                        "severity": "Critical",
                        "issue_description": f"Required column '{column}' is missing from {SOURCE_FILES[source_name]}.",
                    }
                )
    return missing_columns


def get_source_path(config: dict, source_name: str) -> Path:
    return project_path(config["paths"]["raw_data_dir"]) / SOURCE_FILES[source_name]
