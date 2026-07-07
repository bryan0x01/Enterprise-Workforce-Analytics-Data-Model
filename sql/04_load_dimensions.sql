INSERT INTO dim_date (
    date_key, full_date, year, quarter, month_number, month_name, month_start_date, month_end_date
)
VALUES (0, NULL, NULL, 'Unknown', NULL, 'Unknown', NULL, NULL);

WITH RECURSIVE dates(full_date) AS (
    VALUES('{{start_date}}')
    UNION ALL
    SELECT date(full_date, '+1 day')
    FROM dates
    WHERE full_date < '{{end_date}}'
)
INSERT INTO dim_date (
    date_key, full_date, year, quarter, month_number, month_name, month_start_date, month_end_date
)
SELECT
    CAST(strftime('%Y%m%d', full_date) AS INTEGER) AS date_key,
    full_date,
    CAST(strftime('%Y', full_date) AS INTEGER) AS year,
    'Q' || CAST(((CAST(strftime('%m', full_date) AS INTEGER) - 1) / 3) + 1 AS INTEGER) AS quarter,
    CAST(strftime('%m', full_date) AS INTEGER) AS month_number,
    CASE strftime('%m', full_date)
        WHEN '01' THEN 'January'
        WHEN '02' THEN 'February'
        WHEN '03' THEN 'March'
        WHEN '04' THEN 'April'
        WHEN '05' THEN 'May'
        WHEN '06' THEN 'June'
        WHEN '07' THEN 'July'
        WHEN '08' THEN 'August'
        WHEN '09' THEN 'September'
        WHEN '10' THEN 'October'
        WHEN '11' THEN 'November'
        WHEN '12' THEN 'December'
    END AS month_name,
    date(full_date, 'start of month') AS month_start_date,
    date(full_date, 'start of month', '+1 month', '-1 day') AS month_end_date
FROM dates;

INSERT INTO dim_department (department_key, department_code, department_name, division)
VALUES (0, 'UNKNOWN', 'Unknown Department', 'Unknown');

INSERT INTO dim_department (department_code, department_name, division)
SELECT department_code, MIN(department_name), MIN(division)
FROM stg_departments
WHERE department_code IS NOT NULL
GROUP BY department_code;

INSERT INTO dim_location (location_key, location_code, city, state, country, region)
VALUES (0, 'UNKNOWN', 'Unknown City', 'Unknown State', 'Unknown Country', 'Unknown Region');

INSERT INTO dim_location (location_code, city, state, country, region)
SELECT location_code, MIN(city), MIN(state), MIN(country), MIN(region)
FROM stg_locations
WHERE location_code IS NOT NULL
GROUP BY location_code;

INSERT INTO dim_job (job_key, job_code, job_title, job_family, job_level, band_min, band_max)
VALUES (0, 'UNKNOWN', 'Unknown Job', 'Unknown', 'Unknown', NULL, NULL);

INSERT INTO dim_job (job_code, job_title, job_family, job_level, band_min, band_max)
SELECT job_code, MIN(job_title), MIN(job_family), MIN(job_level), MIN(band_min), MAX(band_max)
FROM stg_job_roles
WHERE job_code IS NOT NULL
GROUP BY job_code;

INSERT INTO dim_employment_type (employment_type_key, employment_type)
VALUES (0, 'Unknown');

INSERT INTO dim_employment_type (employment_type)
SELECT DISTINCT employment_type
FROM stg_employees
WHERE employment_type IS NOT NULL
  AND employment_type <> 'Unknown';

INSERT INTO dim_compensation_band (compensation_band_key, compensation_band, band_min, band_max)
VALUES
    (0, 'Unknown', NULL, NULL),
    (1, 'Entry Band', 30000, 59999),
    (2, 'Mid Band', 60000, 89999),
    (3, 'Senior Band', 90000, 124999),
    (4, 'Lead Band', 125000, 169999),
    (5, 'Executive Band', 170000, 250000),
    (6, 'Above Standard Band', 250001, NULL);

INSERT INTO dim_manager (manager_key, manager_employee_id, manager_name, manager_department_code)
VALUES (0, 'UNKNOWN', 'Unknown Manager', 'UNKNOWN');

WITH manager_ids AS (
    SELECT DISTINCT manager_employee_id
    FROM stg_manager_hierarchy
    WHERE manager_employee_id IS NOT NULL
),
ranked_employees AS (
    SELECT
        employee_id,
        first_name,
        last_name,
        department_code,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY source_row_id) AS row_rank
    FROM stg_employees
    WHERE employee_id IS NOT NULL
)
INSERT INTO dim_manager (manager_employee_id, manager_name, manager_department_code)
SELECT
    manager_ids.manager_employee_id,
    COALESCE(TRIM(COALESCE(e.first_name, '') || ' ' || COALESCE(e.last_name, '')), 'Unknown Manager'),
    COALESCE(e.department_code, 'UNKNOWN')
FROM manager_ids
LEFT JOIN ranked_employees e
    ON manager_ids.manager_employee_id = e.employee_id
   AND e.row_rank = 1;

INSERT INTO dim_employee (
    employee_key,
    employee_id,
    first_name,
    last_name,
    full_name,
    gender,
    age_group,
    hire_date,
    termination_date,
    employment_status,
    employment_type_key,
    department_key,
    location_key,
    job_key,
    manager_key,
    source_system,
    synthetic_record
)
VALUES (
    0, 'UNKNOWN', 'Unknown', 'Employee', 'Unknown Employee', 'Unknown', 'Unknown',
    NULL, NULL, 'Unknown', 0, 0, 0, 0, 0, 'Unknown', 1
);

WITH ranked_employees AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY source_row_id) AS row_rank
    FROM stg_employees
    WHERE employee_id IS NOT NULL
),
current_manager AS (
    SELECT employee_id, manager_employee_id
    FROM (
        SELECT
            employee_id,
            manager_employee_id,
            ROW_NUMBER() OVER (PARTITION BY employee_id ORDER BY source_row_id) AS row_rank
        FROM stg_manager_hierarchy
        WHERE employee_id IS NOT NULL
    )
    WHERE row_rank = 1
)
INSERT INTO dim_employee (
    employee_id,
    first_name,
    last_name,
    full_name,
    gender,
    age_group,
    hire_date,
    termination_date,
    employment_status,
    employment_type_key,
    department_key,
    location_key,
    job_key,
    manager_key,
    source_system,
    synthetic_record
)
SELECT
    e.employee_id,
    e.first_name,
    e.last_name,
    TRIM(COALESCE(e.first_name, '') || ' ' || COALESCE(e.last_name, '')) AS full_name,
    COALESCE(e.gender, 'Unknown') AS gender,
    COALESCE(e.age_group, 'Unknown') AS age_group,
    e.hire_date,
    e.termination_date,
    COALESCE(e.employment_status, 'Unknown') AS employment_status,
    COALESCE(et.employment_type_key, 0) AS employment_type_key,
    COALESCE(d.department_key, 0) AS department_key,
    COALESCE(l.location_key, 0) AS location_key,
    COALESCE(j.job_key, 0) AS job_key,
    COALESCE(m.manager_key, 0) AS manager_key,
    COALESCE(e.source_system, 'Unknown') AS source_system,
    COALESCE(e.synthetic_record, 1) AS synthetic_record
FROM ranked_employees e
LEFT JOIN dim_employment_type et
    ON e.employment_type = et.employment_type
LEFT JOIN dim_department d
    ON e.department_code = d.department_code
LEFT JOIN dim_location l
    ON e.location_code = l.location_code
LEFT JOIN dim_job j
    ON e.job_code = j.job_code
LEFT JOIN current_manager cm
    ON e.employee_id = cm.employee_id
LEFT JOIN dim_manager m
    ON cm.manager_employee_id = m.manager_employee_id
WHERE e.row_rank = 1;
