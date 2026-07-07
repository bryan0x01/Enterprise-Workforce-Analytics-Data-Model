-- Quick warehouse checks after running python src/run_pipeline.py

SELECT 'dim_employee' AS table_name, COUNT(*) AS row_count FROM dim_employee
UNION ALL
SELECT 'dim_department', COUNT(*) FROM dim_department
UNION ALL
SELECT 'dim_location', COUNT(*) FROM dim_location
UNION ALL
SELECT 'dim_job', COUNT(*) FROM dim_job
UNION ALL
SELECT 'dim_manager', COUNT(*) FROM dim_manager
UNION ALL
SELECT 'dim_employment_type', COUNT(*) FROM dim_employment_type
UNION ALL
SELECT 'dim_date', COUNT(*) FROM dim_date
UNION ALL
SELECT 'dim_compensation_band', COUNT(*) FROM dim_compensation_band
UNION ALL
SELECT 'fact_employee_snapshot', COUNT(*) FROM fact_employee_snapshot
UNION ALL
SELECT 'fact_employment_event', COUNT(*) FROM fact_employment_event
UNION ALL
SELECT 'fact_compensation', COUNT(*) FROM fact_compensation
UNION ALL
SELECT 'fact_workforce_plan', COUNT(*) FROM fact_workforce_plan
UNION ALL
SELECT 'fact_data_quality_issue', COUNT(*) FROM fact_data_quality_issue;

SELECT
    dd.month_start_date,
    SUM(fs.headcount) AS snapshot_headcount
FROM fact_employee_snapshot fs
JOIN dim_date dd
    ON fs.snapshot_month_key = dd.date_key
GROUP BY dd.month_start_date
ORDER BY dd.month_start_date;

SELECT
    severity,
    COUNT(*) AS issue_count
FROM fact_data_quality_issue
GROUP BY severity
ORDER BY issue_count DESC;
