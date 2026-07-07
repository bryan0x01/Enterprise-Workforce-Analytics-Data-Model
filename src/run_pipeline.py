from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.build_database import build_database, save_processed_csvs
from src.clean_data import clean_sources
from src.export_powerbi_tables import export_powerbi_tables
from src.generate_synthetic_data import generate_all_raw_data
from src.ingest_data import find_missing_required_columns, load_source_files
from src.reconcile_data import run_reconciliations
from src.utils import ensure_directories, load_config, project_path, setup_logging
from src.validate_data import validate_all


def main() -> None:
    logger = setup_logging()
    config = load_config()
    ensure_directories(config)

    logger.info("Starting Enterprise Workforce Analytics pipeline")

    logger.info("Generating synthetic raw data")
    generated_counts = generate_all_raw_data(config)
    logger.info("Generated source record counts: %s", generated_counts)

    logger.info("Ingesting raw CSV source files")
    sources = load_source_files(config)
    required_column_issues = find_missing_required_columns(sources)
    logger.info("Loaded %s source files", len(sources))

    logger.info("Cleaning and standardizing source data")
    cleaned_sources = clean_sources(sources)
    cleaned_counts = {source_name: len(df) for source_name, df in cleaned_sources.items()}
    logger.info("Cleaned record counts: %s", cleaned_counts)
    save_processed_csvs(cleaned_sources, config)

    logger.info("Running validation checks")
    data_quality_issues = validate_all(cleaned_sources, config, required_column_issues)
    logger.info("Validation produced %s data-quality issues", len(data_quality_issues))

    logger.info("Running reconciliation checks")
    reconciliation_summary = run_reconciliations(cleaned_sources, config)
    logger.info(
        "Reconciliation status counts: %s",
        reconciliation_summary["status"].value_counts().to_dict(),
    )

    logger.info("Building SQLite warehouse and analytics views")
    table_counts = build_database(
        cleaned_sources,
        data_quality_issues,
        reconciliation_summary,
        config,
    )
    logger.info("Database table counts: %s", table_counts)

    logger.info("Exporting Power BI-ready CSV files")
    export_counts = export_powerbi_tables(config)
    logger.info("Exported %s Power BI files", len(export_counts))

    database_path = project_path(config["paths"]["database_path"])
    output_dir = project_path(config["paths"]["output_dir"])

    print("\nEnterprise Workforce Analytics Pipeline Summary")
    print("=" * 54)
    print(f"Raw files generated: {len(generated_counts)}")
    print(f"Cleaned source tables: {len(cleaned_counts)}")
    print(f"Data-quality issues logged: {len(data_quality_issues)}")
    print(f"Reconciliation checks: {len(reconciliation_summary)}")
    print(f"Database path: {database_path}")
    print(f"Power BI export directory: {output_dir}")
    print("\nMain table counts")
    for table_name, row_count in table_counts.items():
        print(f"- {table_name}: {row_count:,}")
    print("\nMain export counts")
    for object_name, row_count in export_counts.items():
        print(f"- {object_name}.csv: {row_count:,}")
    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()
