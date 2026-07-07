INSERT INTO fact_compensation (
    effective_date_key,
    employee_key,
    compensation_band_key,
    annual_salary,
    bonus_target_percent,
    total_target_compensation,
    currency,
    pay_frequency
)
SELECT
    COALESCE(d.date_key, 0) AS effective_date_key,
    COALESCE(e.employee_key, 0) AS employee_key,
    COALESCE(cb.compensation_band_key, 0) AS compensation_band_key,
    c.annual_salary,
    c.bonus_target_percent,
    CASE
        WHEN c.annual_salary IS NULL THEN NULL
        ELSE c.annual_salary * (1 + COALESCE(c.bonus_target_percent, 0) / 100.0)
    END AS total_target_compensation,
    COALESCE(c.currency, 'USD') AS currency,
    COALESCE(c.pay_frequency, 'Annual') AS pay_frequency
FROM stg_compensation c
LEFT JOIN dim_employee e
    ON c.employee_id = e.employee_id
LEFT JOIN dim_date d
    ON c.effective_date = d.full_date
LEFT JOIN dim_compensation_band cb
    ON c.annual_salary >= cb.band_min
   AND (c.annual_salary <= cb.band_max OR cb.band_max IS NULL)
   AND cb.compensation_band_key <> 0;

INSERT INTO fact_employment_event (
    event_date_key,
    employee_key,
    department_key,
    job_key,
    event_type,
    termination_type,
    event_reason,
    event_count
)
SELECT
    COALESCE(d.date_key, 0) AS event_date_key,
    COALESCE(e.employee_key, 0) AS employee_key,
    COALESCE(dep.department_key, 0) AS department_key,
    COALESCE(j.job_key, 0) AS job_key,
    COALESCE(ev.event_type, 'Unknown') AS event_type,
    COALESCE(ev.termination_type, 'Not Applicable') AS termination_type,
    COALESCE(ev.event_reason, 'Not Provided') AS event_reason,
    1 AS event_count
FROM stg_employment_events ev
LEFT JOIN dim_employee e
    ON ev.employee_id = e.employee_id
LEFT JOIN dim_date d
    ON ev.event_date = d.full_date
LEFT JOIN dim_department dep
    ON ev.department_code = dep.department_code
LEFT JOIN dim_job j
    ON ev.job_code = j.job_code;

INSERT INTO fact_workforce_plan (
    plan_month_key,
    department_key,
    planned_headcount,
    plan_version
)
SELECT
    COALESCE(d.date_key, 0) AS plan_month_key,
    COALESCE(dep.department_key, 0) AS department_key,
    wp.planned_headcount,
    COALESCE(wp.plan_version, 'Plan') AS plan_version
FROM stg_workforce_plan wp
LEFT JOIN dim_date d
    ON wp.plan_month = d.full_date
LEFT JOIN dim_department dep
    ON wp.department_code = dep.department_code;

INSERT INTO fact_data_quality_issue (
    issue_id,
    source_file,
    record_identifier,
    column_name,
    rule_name,
    severity,
    issue_description,
    detected_timestamp,
    resolution_status
)
SELECT
    issue_id,
    source_file,
    record_identifier,
    column_name,
    rule_name,
    severity,
    issue_description,
    detected_timestamp,
    resolution_status
FROM stg_data_quality_issue;

WITH RECURSIVE snapshot_months(month_start) AS (
    VALUES(date('{{start_date}}', 'start of month'))
    UNION ALL
    SELECT date(month_start, '+1 month')
    FROM snapshot_months
    WHERE month_start < date('{{end_date}}', 'start of month')
)
INSERT INTO fact_employee_snapshot (
    snapshot_month_key,
    employee_key,
    department_key,
    location_key,
    job_key,
    manager_key,
    employment_type_key,
    headcount,
    tenure_months
)
SELECT
    d.date_key AS snapshot_month_key,
    e.employee_key,
    COALESCE(e.department_key, 0),
    COALESCE(e.location_key, 0),
    COALESCE(e.job_key, 0),
    COALESCE(e.manager_key, 0),
    COALESCE(e.employment_type_key, 0),
    1 AS headcount,
    (
        (CAST(strftime('%Y', date(m.month_start, 'start of month', '+1 month', '-1 day')) AS INTEGER)
            - CAST(strftime('%Y', e.hire_date) AS INTEGER)) * 12
        + (CAST(strftime('%m', date(m.month_start, 'start of month', '+1 month', '-1 day')) AS INTEGER)
            - CAST(strftime('%m', e.hire_date) AS INTEGER))
    ) AS tenure_months
FROM snapshot_months m
JOIN dim_date d
    ON m.month_start = d.full_date
JOIN dim_employee e
    ON e.employee_key <> 0
   AND e.hire_date IS NOT NULL
   AND date(e.hire_date) <= date(m.month_start, 'start of month', '+1 month', '-1 day')
   AND (
       e.termination_date IS NULL
       OR date(e.termination_date) > date(m.month_start, 'start of month', '+1 month', '-1 day')
   );
