from __future__ import annotations

import pandas as pd

from src.utils import get_database_connection, project_path


EXPORT_OBJECTS = [
    "dim_employee",
    "dim_department",
    "dim_location",
    "dim_job",
    "dim_manager",
    "dim_employment_type",
    "dim_date",
    "dim_compensation_band",
    "fact_employee_snapshot",
    "fact_employment_event",
    "fact_compensation",
    "fact_workforce_plan",
    "fact_data_quality_issue",
    "reconciliation_summary",
    "vw_current_workforce",
    "vw_monthly_headcount",
    "vw_hires_and_terminations",
    "vw_turnover_summary",
    "vw_compensation_summary",
    "vw_tenure_distribution",
    "vw_department_workforce",
    "vw_location_workforce",
    "vw_actual_vs_plan",
    "vw_data_quality_summary",
]


def export_powerbi_tables(config: dict) -> dict[str, int]:
    output_dir = project_path(config["paths"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    export_counts = {}

    with get_database_connection(config) as connection:
        for object_name in EXPORT_OBJECTS:
            df = pd.read_sql_query(f"SELECT * FROM {object_name}", connection)
            df.to_csv(output_dir / f"{object_name}.csv", index=False)
            export_counts[object_name] = len(df)

    return export_counts
