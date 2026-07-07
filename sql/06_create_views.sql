DROP VIEW IF EXISTS vw_current_workforce;
DROP VIEW IF EXISTS vw_monthly_headcount;
DROP VIEW IF EXISTS vw_hires_and_terminations;
DROP VIEW IF EXISTS vw_turnover_summary;
DROP VIEW IF EXISTS vw_compensation_summary;
DROP VIEW IF EXISTS vw_tenure_distribution;
DROP VIEW IF EXISTS vw_department_workforce;
DROP VIEW IF EXISTS vw_location_workforce;
DROP VIEW IF EXISTS vw_actual_vs_plan;
DROP VIEW IF EXISTS vw_data_quality_summary;

CREATE VIEW vw_current_workforce AS
WITH current_month AS (
    SELECT MAX(snapshot_month_key) AS snapshot_month_key
    FROM fact_employee_snapshot
),
latest_compensation AS (
    SELECT *
    FROM (
        SELECT
            fc.*,
            ROW_NUMBER() OVER (
                PARTITION BY employee_key
                ORDER BY effective_date_key DESC, compensation_key DESC
            ) AS row_rank
        FROM fact_compensation fc
        WHERE annual_salary IS NOT NULL
          AND annual_salary > 0
    )
    WHERE row_rank = 1
)
SELECT
    dd.month_start_date AS "Snapshot Month",
    de.employee_id AS "Employee ID",
    de.full_name AS "Employee Name",
    de.gender AS "Gender",
    de.age_group AS "Age Group",
    dep.department_name AS "Department",
    dep.division AS "Division",
    loc.city AS "City",
    loc.state AS "State",
    loc.region AS "Region",
    job.job_title AS "Job Title",
    job.job_family AS "Job Family",
    job.job_level AS "Job Level",
    et.employment_type AS "Employment Type",
    mgr.manager_name AS "Manager",
    de.hire_date AS "Hire Date",
    fs.tenure_months / 12.0 AS "Tenure Years",
    lc.annual_salary AS "Annual Salary",
    cb.compensation_band AS "Compensation Band",
    fs.headcount AS "Active Headcount"
FROM fact_employee_snapshot fs
JOIN current_month cm
    ON fs.snapshot_month_key = cm.snapshot_month_key
JOIN dim_date dd
    ON fs.snapshot_month_key = dd.date_key
JOIN dim_employee de
    ON fs.employee_key = de.employee_key
JOIN dim_department dep
    ON fs.department_key = dep.department_key
JOIN dim_location loc
    ON fs.location_key = loc.location_key
JOIN dim_job job
    ON fs.job_key = job.job_key
JOIN dim_employment_type et
    ON fs.employment_type_key = et.employment_type_key
JOIN dim_manager mgr
    ON fs.manager_key = mgr.manager_key
LEFT JOIN latest_compensation lc
    ON fs.employee_key = lc.employee_key
LEFT JOIN dim_compensation_band cb
    ON lc.compensation_band_key = cb.compensation_band_key;

CREATE VIEW vw_monthly_headcount AS
SELECT
    dd.month_start_date AS "Month",
    dd.year AS "Year",
    dd.month_name AS "Month Name",
    dep.department_name AS "Department",
    loc.city AS "Location City",
    job.job_level AS "Job Level",
    et.employment_type AS "Employment Type",
    SUM(fs.headcount) AS "Active Headcount"
FROM fact_employee_snapshot fs
JOIN dim_date dd
    ON fs.snapshot_month_key = dd.date_key
JOIN dim_department dep
    ON fs.department_key = dep.department_key
JOIN dim_location loc
    ON fs.location_key = loc.location_key
JOIN dim_job job
    ON fs.job_key = job.job_key
JOIN dim_employment_type et
    ON fs.employment_type_key = et.employment_type_key
GROUP BY
    dd.month_start_date,
    dd.year,
    dd.month_name,
    dep.department_name,
    loc.city,
    job.job_level,
    et.employment_type;

CREATE VIEW vw_hires_and_terminations AS
SELECT
    dd.month_start_date AS "Month",
    dep.department_name AS "Department",
    job.job_level AS "Job Level",
    SUM(CASE WHEN LOWER(f.event_type) = 'hire' THEN f.event_count ELSE 0 END) AS "Hires",
    SUM(CASE WHEN LOWER(f.event_type) = 'termination' THEN f.event_count ELSE 0 END) AS "Terminations",
    SUM(CASE WHEN LOWER(f.event_type) = 'termination' AND LOWER(f.termination_type) = 'voluntary' THEN f.event_count ELSE 0 END) AS "Voluntary Terminations",
    SUM(CASE WHEN LOWER(f.event_type) = 'termination' AND LOWER(f.termination_type) = 'involuntary' THEN f.event_count ELSE 0 END) AS "Involuntary Terminations"
FROM fact_employment_event f
JOIN dim_date dd
    ON f.event_date_key = dd.date_key
JOIN dim_department dep
    ON f.department_key = dep.department_key
JOIN dim_job job
    ON f.job_key = job.job_key
WHERE dd.date_key <> 0
GROUP BY dd.month_start_date, dep.department_name, job.job_level;

CREATE VIEW vw_turnover_summary AS
WITH monthly_headcount AS (
    SELECT
        dd.month_start_date AS month_start_date,
        SUM(fs.headcount) AS ending_headcount
    FROM fact_employee_snapshot fs
    JOIN dim_date dd
        ON fs.snapshot_month_key = dd.date_key
    GROUP BY dd.month_start_date
),
monthly_terms AS (
    SELECT
        dd.month_start_date AS month_start_date,
        SUM(f.event_count) AS terminations
    FROM fact_employment_event f
    JOIN dim_date dd
        ON f.event_date_key = dd.date_key
    WHERE LOWER(f.event_type) = 'termination'
    GROUP BY dd.month_start_date
),
combined AS (
    SELECT
        mh.month_start_date,
        LAG(mh.ending_headcount) OVER (ORDER BY mh.month_start_date) AS beginning_headcount,
        mh.ending_headcount,
        COALESCE(mt.terminations, 0) AS terminations
    FROM monthly_headcount mh
    LEFT JOIN monthly_terms mt
        ON mh.month_start_date = mt.month_start_date
)
SELECT
    month_start_date AS "Month",
    COALESCE(beginning_headcount, ending_headcount) AS "Beginning Headcount",
    ending_headcount AS "Ending Headcount",
    (COALESCE(beginning_headcount, ending_headcount) + ending_headcount) / 2.0 AS "Average Headcount",
    terminations AS "Terminations",
    CASE
        WHEN (COALESCE(beginning_headcount, ending_headcount) + ending_headcount) / 2.0 = 0 THEN 0
        ELSE terminations / ((COALESCE(beginning_headcount, ending_headcount) + ending_headcount) / 2.0)
    END AS "Turnover Rate"
FROM combined;

CREATE VIEW vw_compensation_summary AS
WITH latest_compensation AS (
    SELECT *
    FROM (
        SELECT
            fc.*,
            ROW_NUMBER() OVER (
                PARTITION BY employee_key
                ORDER BY effective_date_key DESC, compensation_key DESC
            ) AS row_rank
        FROM fact_compensation fc
        WHERE employee_key <> 0
          AND annual_salary IS NOT NULL
          AND annual_salary > 0
    )
    WHERE row_rank = 1
)
SELECT
    dep.department_name AS "Department",
    job.job_family AS "Job Family",
    job.job_level AS "Job Level",
    cb.compensation_band AS "Compensation Band",
    COUNT(*) AS "Employees With Compensation",
    ROUND(AVG(lc.annual_salary), 2) AS "Average Salary",
    ROUND(SUM(lc.annual_salary), 2) AS "Total Annual Compensation",
    SUM(CASE WHEN lc.annual_salary < job.band_min THEN 1 ELSE 0 END) AS "Employees Below Job Band",
    SUM(CASE WHEN lc.annual_salary > job.band_max THEN 1 ELSE 0 END) AS "Employees Above Job Band"
FROM latest_compensation lc
JOIN dim_employee de
    ON lc.employee_key = de.employee_key
JOIN dim_department dep
    ON de.department_key = dep.department_key
JOIN dim_job job
    ON de.job_key = job.job_key
JOIN dim_compensation_band cb
    ON lc.compensation_band_key = cb.compensation_band_key
GROUP BY dep.department_name, job.job_family, job.job_level, cb.compensation_band;

CREATE VIEW vw_tenure_distribution AS
WITH current_month AS (
    SELECT MAX(snapshot_month_key) AS snapshot_month_key
    FROM fact_employee_snapshot
)
SELECT
    CASE
        WHEN fs.tenure_months < 12 THEN 'Less than 1 year'
        WHEN fs.tenure_months < 36 THEN '1 to 3 years'
        WHEN fs.tenure_months < 60 THEN '3 to 5 years'
        ELSE '5+ years'
    END AS "Tenure Group",
    dep.department_name AS "Department",
    job.job_level AS "Job Level",
    COUNT(*) AS "Active Headcount",
    ROUND(AVG(fs.tenure_months / 12.0), 2) AS "Average Tenure Years"
FROM fact_employee_snapshot fs
JOIN current_month cm
    ON fs.snapshot_month_key = cm.snapshot_month_key
JOIN dim_department dep
    ON fs.department_key = dep.department_key
JOIN dim_job job
    ON fs.job_key = job.job_key
GROUP BY
    CASE
        WHEN fs.tenure_months < 12 THEN 'Less than 1 year'
        WHEN fs.tenure_months < 36 THEN '1 to 3 years'
        WHEN fs.tenure_months < 60 THEN '3 to 5 years'
        ELSE '5+ years'
    END,
    dep.department_name,
    job.job_level;

CREATE VIEW vw_department_workforce AS
WITH current_month AS (
    SELECT MAX(snapshot_month_key) AS snapshot_month_key
    FROM fact_employee_snapshot
)
SELECT
    dep.department_name AS "Department",
    dep.division AS "Division",
    COUNT(*) AS "Active Headcount",
    ROUND(AVG(fs.tenure_months / 12.0), 2) AS "Average Tenure Years"
FROM fact_employee_snapshot fs
JOIN current_month cm
    ON fs.snapshot_month_key = cm.snapshot_month_key
JOIN dim_department dep
    ON fs.department_key = dep.department_key
GROUP BY dep.department_name, dep.division;

CREATE VIEW vw_location_workforce AS
WITH current_month AS (
    SELECT MAX(snapshot_month_key) AS snapshot_month_key
    FROM fact_employee_snapshot
)
SELECT
    loc.region AS "Region",
    loc.city AS "City",
    loc.state AS "State",
    COUNT(*) AS "Active Headcount"
FROM fact_employee_snapshot fs
JOIN current_month cm
    ON fs.snapshot_month_key = cm.snapshot_month_key
JOIN dim_location loc
    ON fs.location_key = loc.location_key
GROUP BY loc.region, loc.city, loc.state;

CREATE VIEW vw_actual_vs_plan AS
WITH actual_by_month_department AS (
    SELECT
        fs.snapshot_month_key AS month_key,
        fs.department_key,
        SUM(fs.headcount) AS actual_headcount
    FROM fact_employee_snapshot fs
    GROUP BY fs.snapshot_month_key, fs.department_key
),
plan_by_month_department AS (
    SELECT
        plan_month_key AS month_key,
        department_key,
        SUM(planned_headcount) AS planned_headcount
    FROM fact_workforce_plan
    GROUP BY plan_month_key, department_key
),
combined AS (
    SELECT
        p.month_key,
        p.department_key,
        COALESCE(a.actual_headcount, 0) AS actual_headcount,
        p.planned_headcount
    FROM plan_by_month_department p
    LEFT JOIN actual_by_month_department a
        ON p.month_key = a.month_key
       AND p.department_key = a.department_key
    UNION ALL
    SELECT
        a.month_key,
        a.department_key,
        a.actual_headcount,
        0 AS planned_headcount
    FROM actual_by_month_department a
    LEFT JOIN plan_by_month_department p
        ON a.month_key = p.month_key
       AND a.department_key = p.department_key
    WHERE p.department_key IS NULL
)
SELECT
    dd.month_start_date AS "Month",
    dep.department_name AS "Department",
    actual_headcount AS "Actual Headcount",
    planned_headcount AS "Planned Headcount",
    actual_headcount - planned_headcount AS "Headcount Variance"
FROM combined
JOIN dim_date dd
    ON combined.month_key = dd.date_key
JOIN dim_department dep
    ON combined.department_key = dep.department_key;

CREATE VIEW vw_data_quality_summary AS
SELECT
    severity AS "Severity",
    source_file AS "Source File",
    rule_name AS "Validation Rule",
    resolution_status AS "Resolution Status",
    COUNT(*) AS "Issue Count"
FROM fact_data_quality_issue
GROUP BY severity, source_file, rule_name, resolution_status;
