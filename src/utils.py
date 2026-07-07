from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def project_path(relative_path: str | Path) -> Path:
    return PROJECT_ROOT / Path(relative_path)


def load_config(config_path: str | Path = "config/config.yaml") -> dict[str, Any]:
    path = project_path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def ensure_directories(config: dict[str, Any]) -> None:
    for path_key in ["raw_data_dir", "processed_data_dir", "output_dir"]:
        project_path(config["paths"][path_key]).mkdir(parents=True, exist_ok=True)

    project_path(config["paths"]["database_path"]).parent.mkdir(parents=True, exist_ok=True)


def setup_logging() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("workforce_pipeline")


def get_database_connection(config: dict[str, Any]) -> sqlite3.Connection:
    database_path = project_path(config["paths"]["database_path"])
    return sqlite3.connect(database_path)


def read_sql_file(file_name: str) -> str:
    sql_path = project_path("sql") / file_name
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")
    return sql_path.read_text(encoding="utf-8")


def render_sql_template(sql_text: str, config: dict[str, Any]) -> str:
    synthetic_config = config["synthetic_data"]
    replacements = {
        "start_date": synthetic_config["start_date"],
        "end_date": synthetic_config["end_date"],
    }

    rendered_sql = sql_text
    for key, value in replacements.items():
        rendered_sql = rendered_sql.replace(f"{{{{{key}}}}}", str(value))
    return rendered_sql


def date_key(date_value: Any) -> int:
    if date_value is None or str(date_value).strip() == "":
        return 0
    return int(str(date_value).replace("-", "")[:8])
