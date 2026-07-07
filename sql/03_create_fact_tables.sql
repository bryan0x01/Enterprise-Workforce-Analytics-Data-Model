DROP TABLE IF EXISTS fact_employee_snapshot;
DROP TABLE IF EXISTS fact_employment_event;
DROP TABLE IF EXISTS fact_compensation;
DROP TABLE IF EXISTS fact_workforce_plan;
DROP TABLE IF EXISTS fact_data_quality_issue;
DROP TABLE IF EXISTS reconciliation_summary;

CREATE TABLE fact_employee_snapshot (
    snapshot_key INTEGER PRIMARY KEY,
    snapshot_month_key INTEGER,
    employee_key INTEGER,
    department_key INTEGER,
    location_key INTEGER,
    job_key INTEGER,
    manager_key INTEGER,
    employment_type_key INTEGER,
    headcount INTEGER,
    tenure_months INTEGER
);

CREATE TABLE fact_employment_event (
    event_key INTEGER PRIMARY KEY,
    event_date_key INTEGER,
    employee_key INTEGER,
    department_key INTEGER,
    job_key INTEGER,
    event_type TEXT,
    termination_type TEXT,
    event_reason TEXT,
    event_count INTEGER
);

CREATE TABLE fact_compensation (
    compensation_key INTEGER PRIMARY KEY,
    effective_date_key INTEGER,
    employee_key INTEGER,
    compensation_band_key INTEGER,
    annual_salary REAL,
    bonus_target_percent REAL,
    total_target_compensation REAL,
    currency TEXT,
    pay_frequency TEXT
);

CREATE TABLE fact_workforce_plan (
    plan_key INTEGER PRIMARY KEY,
    plan_month_key INTEGER,
    department_key INTEGER,
    planned_headcount REAL,
    plan_version TEXT
);

CREATE TABLE fact_data_quality_issue (
    issue_key INTEGER PRIMARY KEY,
    issue_id TEXT,
    source_file TEXT,
    record_identifier TEXT,
    column_name TEXT,
    rule_name TEXT,
    severity TEXT,
    issue_description TEXT,
    detected_timestamp TEXT,
    resolution_status TEXT
);

CREATE TABLE reconciliation_summary (
    reconciliation_id INTEGER PRIMARY KEY,
    reconciliation_name TEXT,
    source_value REAL,
    target_value REAL,
    difference REAL,
    status TEXT,
    notes TEXT
);
