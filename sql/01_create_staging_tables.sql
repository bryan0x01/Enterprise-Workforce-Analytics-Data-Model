DROP TABLE IF EXISTS stg_employees;
DROP TABLE IF EXISTS stg_compensation;
DROP TABLE IF EXISTS stg_departments;
DROP TABLE IF EXISTS stg_locations;
DROP TABLE IF EXISTS stg_job_roles;
DROP TABLE IF EXISTS stg_employment_events;
DROP TABLE IF EXISTS stg_manager_hierarchy;
DROP TABLE IF EXISTS stg_workforce_plan;
DROP TABLE IF EXISTS stg_data_quality_issue;

CREATE TABLE stg_employees (
    source_row_id INTEGER,
    employee_id TEXT,
    first_name TEXT,
    last_name TEXT,
    gender TEXT,
    age_group TEXT,
    department_code TEXT,
    location_code TEXT,
    job_code TEXT,
    employment_type TEXT,
    hire_date TEXT,
    termination_date TEXT,
    employment_status TEXT,
    source_system TEXT,
    synthetic_record INTEGER
);

CREATE TABLE stg_compensation (
    source_row_id INTEGER,
    employee_id TEXT,
    annual_salary REAL,
    bonus_target_percent REAL,
    effective_date TEXT,
    currency TEXT,
    pay_frequency TEXT
);

CREATE TABLE stg_departments (
    source_row_id INTEGER,
    department_code TEXT,
    department_name TEXT,
    division TEXT
);

CREATE TABLE stg_locations (
    source_row_id INTEGER,
    location_code TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    region TEXT
);

CREATE TABLE stg_job_roles (
    source_row_id INTEGER,
    job_code TEXT,
    job_title TEXT,
    job_family TEXT,
    job_level TEXT,
    band_min REAL,
    band_max REAL
);

CREATE TABLE stg_employment_events (
    source_row_id INTEGER,
    employee_id TEXT,
    event_type TEXT,
    event_date TEXT,
    department_code TEXT,
    job_code TEXT,
    termination_type TEXT,
    event_reason TEXT
);

CREATE TABLE stg_manager_hierarchy (
    source_row_id INTEGER,
    employee_id TEXT,
    manager_employee_id TEXT,
    effective_date TEXT,
    end_date TEXT
);

CREATE TABLE stg_workforce_plan (
    source_row_id INTEGER,
    plan_month TEXT,
    department_code TEXT,
    department_name TEXT,
    planned_headcount REAL,
    plan_version TEXT
);

CREATE TABLE stg_data_quality_issue (
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
