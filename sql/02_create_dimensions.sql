DROP TABLE IF EXISTS dim_employee;
DROP TABLE IF EXISTS dim_department;
DROP TABLE IF EXISTS dim_location;
DROP TABLE IF EXISTS dim_job;
DROP TABLE IF EXISTS dim_manager;
DROP TABLE IF EXISTS dim_employment_type;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_compensation_band;

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT,
    year INTEGER,
    quarter TEXT,
    month_number INTEGER,
    month_name TEXT,
    month_start_date TEXT,
    month_end_date TEXT
);

CREATE TABLE dim_department (
    department_key INTEGER PRIMARY KEY,
    department_code TEXT UNIQUE,
    department_name TEXT,
    division TEXT
);

CREATE TABLE dim_location (
    location_key INTEGER PRIMARY KEY,
    location_code TEXT UNIQUE,
    city TEXT,
    state TEXT,
    country TEXT,
    region TEXT
);

CREATE TABLE dim_job (
    job_key INTEGER PRIMARY KEY,
    job_code TEXT UNIQUE,
    job_title TEXT,
    job_family TEXT,
    job_level TEXT,
    band_min REAL,
    band_max REAL
);

CREATE TABLE dim_manager (
    manager_key INTEGER PRIMARY KEY,
    manager_employee_id TEXT UNIQUE,
    manager_name TEXT,
    manager_department_code TEXT
);

CREATE TABLE dim_employment_type (
    employment_type_key INTEGER PRIMARY KEY,
    employment_type TEXT UNIQUE
);

CREATE TABLE dim_compensation_band (
    compensation_band_key INTEGER PRIMARY KEY,
    compensation_band TEXT UNIQUE,
    band_min REAL,
    band_max REAL
);

CREATE TABLE dim_employee (
    employee_key INTEGER PRIMARY KEY,
    employee_id TEXT UNIQUE,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    gender TEXT,
    age_group TEXT,
    hire_date TEXT,
    termination_date TEXT,
    employment_status TEXT,
    employment_type_key INTEGER,
    department_key INTEGER,
    location_key INTEGER,
    job_key INTEGER,
    manager_key INTEGER,
    source_system TEXT,
    synthetic_record INTEGER,
    FOREIGN KEY (employment_type_key) REFERENCES dim_employment_type(employment_type_key),
    FOREIGN KEY (department_key) REFERENCES dim_department(department_key),
    FOREIGN KEY (location_key) REFERENCES dim_location(location_key),
    FOREIGN KEY (job_key) REFERENCES dim_job(job_key),
    FOREIGN KEY (manager_key) REFERENCES dim_manager(manager_key)
);
