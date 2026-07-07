from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils import get_database_connection, project_path, read_sql_file, render_sql_template


STAGING_TABLES = {
    "employees": "stg_employees",
    "compensation": "stg_compensation",
    "departments": "stg_departments",
    "locations": "stg_locations",
    "job_roles": "stg_job_roles",
    "employment_events": "stg_employment_events",
    "manager_hierarchy": "stg_manager_hierarchy",
    "workforce_plan": "stg_workforce_plan",
}


def execute_sql_script(connection, config: dict, file_name: str) -> None:
    sql_text = render_sql_template(read_sql_file(file_name), config)
    connection.executescript(sql_text)


def load_dataframe(connection, table_name: str, df: pd.DataFrame) -> None:
    safe_df = df.where(pd.notna(df), None)
    safe_df.to_sql(table_name, connection, if_exists="append", index=False)


def save_processed_csvs(cleaned_sources: dict[str, pd.DataFrame], config: dict) -> None:
    processed_dir = project_path(config["paths"]["processed_data_dir"])
    processed_dir.mkdir(parents=True, exist_ok=True)

    for source_name, df in cleaned_sources.items():
        df.to_csv(processed_dir / f"{source_name}_cleaned.csv", index=False)


def build_database(
    cleaned_sources: dict[str, pd.DataFrame],
    data_quality_issues: pd.DataFrame,
    reconciliation_summary: pd.DataFrame,
    config: dict,
) -> dict[str, int]:
    database_path = project_path(config["paths"]["database_path"])
    if database_path.exists():
        database_path.unlink()

    with get_database_connection(config) as connection:
        connection.execute("PRAGMA foreign_keys = OFF;")

        execute_sql_script(connection, config, "01_create_staging_tables.sql")
        execute_sql_script(connection, config, "02_create_dimensions.sql")
        execute_sql_script(connection, config, "03_create_fact_tables.sql")

        for source_name, table_name in STAGING_TABLES.items():
            load_dataframe(connection, table_name, cleaned_sources[source_name])

        load_dataframe(connection, "stg_data_quality_issue", data_quality_issues)

        execute_sql_script(connection, config, "04_load_dimensions.sql")
        execute_sql_script(connection, config, "05_load_facts.sql")

        load_dataframe(connection, "reconciliation_summary", reconciliation_summary)

        execute_sql_script(connection, config, "06_create_views.sql")

        table_counts = {}
        tables_to_check = [
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
        ]
        for table_name in tables_to_check:
            table_counts[table_name] = int(
                connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            )

    return table_counts
