from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from src.utils import project_path


FIRST_NAMES = [
    "Aaliyah",
    "Alex",
    "Amara",
    "Andre",
    "Brianna",
    "Camila",
    "Carlos",
    "Daniel",
    "Elena",
    "Fatima",
    "Grace",
    "Hannah",
    "Isaac",
    "Jada",
    "Jordan",
    "Kai",
    "Leah",
    "Luis",
    "Maya",
    "Nina",
    "Omar",
    "Priya",
    "Rafael",
    "Sam",
    "Sofia",
    "Taylor",
    "Victor",
    "Yara",
]

LAST_NAMES = [
    "Adams",
    "Baker",
    "Chen",
    "Diaz",
    "Evans",
    "Flores",
    "Garcia",
    "Hall",
    "Johnson",
    "Kim",
    "Lopez",
    "Martinez",
    "Nguyen",
    "Patel",
    "Rivera",
    "Robinson",
    "Singh",
    "Smith",
    "Thomas",
    "Williams",
]

DEPARTMENTS = [
    ("ENG", "Engineering", "Technology"),
    ("PRD", "Product", "Technology"),
    ("IT", "Information Technology", "Technology"),
    ("SAL", "Sales", "Revenue"),
    ("MKT", "Marketing", "Revenue"),
    ("CS", "Customer Success", "Revenue"),
    ("FIN", "Finance", "Corporate"),
    ("HR", "Human Resources", "Corporate"),
    ("OPS", "Operations", "Corporate"),
    ("LEG", "Legal", "Corporate"),
]

LOCATIONS = [
    ("NYC", "New York", "NY", "United States", "Northeast"),
    ("AUS", "Austin", "TX", "United States", "South"),
    ("SFO", "San Francisco", "CA", "United States", "West"),
    ("CHI", "Chicago", "IL", "United States", "Midwest"),
    ("ATL", "Atlanta", "GA", "United States", "South"),
    ("SEA", "Seattle", "WA", "United States", "West"),
    ("DEN", "Denver", "CO", "United States", "Mountain"),
    ("REM", "Remote", "", "United States", "Remote"),
]

JOB_ROLES = [
    ("ENG1", "Software Engineer I", "Engineering", "L1", 70000, 95000),
    ("ENG2", "Software Engineer II", "Engineering", "L2", 90000, 125000),
    ("ENG3", "Senior Software Engineer", "Engineering", "L3", 120000, 165000),
    ("DATA1", "Data Analyst", "Analytics", "L1", 65000, 90000),
    ("DATA2", "Analytics Engineer", "Analytics", "L2", 85000, 120000),
    ("DATA3", "Senior Data Engineer", "Analytics", "L3", 115000, 155000),
    ("PM1", "Product Manager", "Product", "L2", 95000, 135000),
    ("PM2", "Senior Product Manager", "Product", "L3", 125000, 170000),
    ("SALE1", "Account Executive", "Sales", "L2", 70000, 115000),
    ("SALE2", "Sales Manager", "Sales", "M1", 110000, 160000),
    ("MKT1", "Marketing Specialist", "Marketing", "L1", 55000, 80000),
    ("CS1", "Customer Success Manager", "Customer Success", "L2", 70000, 105000),
    ("FIN1", "Financial Analyst", "Finance", "L1", 65000, 90000),
    ("HR1", "People Operations Specialist", "Human Resources", "L1", 58000, 85000),
    ("OPS1", "Operations Manager", "Operations", "M1", 90000, 135000),
    ("DIR1", "Director", "Leadership", "M2", 145000, 210000),
]

EMPLOYMENT_TYPE_VARIANTS = {
    "Full-Time": ["Full Time", "full-time", "FT", " Full-Time "],
    "Part-Time": ["Part Time", "part-time", "PT"],
    "Contractor": ["Contractor", "contract", "CONT"],
    "Intern": ["Intern", "internship", "INTERN"],
    "Temporary": ["Temp", "Temporary", "temporary"],
}


def random_date(random_generator: random.Random, start_date: date, end_date: date) -> date:
    days = (end_date - start_date).days
    return start_date + timedelta(days=random_generator.randint(0, days))


def choose_weighted(random_generator: random.Random, values: list[str], weights: list[float]) -> str:
    return random_generator.choices(values, weights=weights, k=1)[0]


def generate_reference_files(raw_dir: Path) -> None:
    department_rows = [
        {"Department Code": code, "Department Name": name, "Division": division}
        for code, name, division in DEPARTMENTS
    ]
    department_rows.append(
        {"Department Code": "MKT", "Department Name": "Marketing Team", "Division": "Revenue"}
    )

    location_rows = [
        {
            "Location Code": code,
            "City": city,
            "State": state,
            "Country": country,
            "Region": region,
        }
        for code, city, state, country, region in LOCATIONS
    ]

    job_rows = [
        {
            "Job Code": code,
            "Job Title": title,
            "Job Family": family,
            "Job Level": level,
            "Band Min": band_min,
            "Band Max": band_max,
        }
        for code, title, family, level, band_min, band_max in JOB_ROLES
    ]

    pd.DataFrame(department_rows).to_csv(raw_dir / "departments.csv", index=False)
    pd.DataFrame(location_rows).to_csv(raw_dir / "locations.csv", index=False)
    pd.DataFrame(job_rows).to_csv(raw_dir / "job_roles.csv", index=False)


def generate_employee_rows(config: dict) -> pd.DataFrame:
    random_generator = random.Random(config["random_seed"])
    employee_count = config["synthetic_data"]["employee_count"]
    start_date = date.fromisoformat(config["synthetic_data"]["start_date"])
    end_date = date.fromisoformat(config["synthetic_data"]["end_date"])

    department_codes = [item[0] for item in DEPARTMENTS]
    location_codes = [item[0] for item in LOCATIONS]
    job_codes = [item[0] for item in JOB_ROLES]
    employment_type_labels = list(EMPLOYMENT_TYPE_VARIANTS.keys())
    employment_type_weights = [0.77, 0.08, 0.08, 0.04, 0.03]

    employee_rows = []
    for index in range(1, employee_count + 1):
        employee_id = f"E{index:06d}"
        hire_date = random_date(random_generator, start_date, end_date - timedelta(days=60))

        is_terminated = random_generator.random() < 0.23
        termination_date = ""
        employment_status = "Active"
        if is_terminated:
            max_term_date = end_date
            min_term_date = hire_date + timedelta(days=30)
            if min_term_date <= max_term_date:
                termination_date = random_date(random_generator, min_term_date, max_term_date)
                employment_status = "Terminated"

        employment_type = choose_weighted(
            random_generator, employment_type_labels, employment_type_weights
        )
        employment_type = random_generator.choice(EMPLOYMENT_TYPE_VARIANTS[employment_type])

        employee_rows.append(
            {
                "Employee ID": employee_id,
                "First Name": random_generator.choice(FIRST_NAMES),
                "Last Name": random_generator.choice(LAST_NAMES),
                "Gender": random_generator.choice(["Female", "Male", "Non-Binary", "Not Disclosed"]),
                "Age Group": random_generator.choice(["18-24", "25-34", "35-44", "45-54", "55+"]),
                "Department Code": random_generator.choice(department_codes),
                "Location Code": random_generator.choice(location_codes),
                "Job Code": random_generator.choice(job_codes),
                "Employment Type": employment_type,
                "Hire Date": hire_date.isoformat(),
                "Termination Date": termination_date if termination_date == "" else termination_date.isoformat(),
                "Employment Status": employment_status,
                "Source System": random_generator.choice(["HRIS", "Core HR", "PeopleOps"]),
                "Synthetic Record": "Yes",
            }
        )

    df = pd.DataFrame(employee_rows)
    return inject_employee_inconsistencies(df, random_generator, end_date)


def inject_employee_inconsistencies(
    employees: pd.DataFrame, random_generator: random.Random, end_date: date
) -> pd.DataFrame:
    for row_index in random_generator.sample(list(employees.index), 35):
        employees.loc[row_index, "Department Code"] = random_generator.choice(["BAD", "UNKNOWN", ""])

    for row_index in random_generator.sample(list(employees.index), 30):
        employees.loc[row_index, "Location Code"] = random_generator.choice(["ZZZ", "N/A", ""])

    for row_index in random_generator.sample(list(employees.index), 25):
        employees.loc[row_index, "Job Code"] = random_generator.choice(["NOJOB", "", "TEMP99"])

    for row_index in random_generator.sample(list(employees.index), 18):
        employees.loc[row_index, "Employee ID"] = " "

    for row_index in random_generator.sample(list(employees.index), 20):
        employees.loc[row_index, "First Name"] = f"  {employees.loc[row_index, 'First Name'].upper()} "

    for row_index in random_generator.sample(list(employees.index), 14):
        hire_date = date.fromisoformat(employees.loc[row_index, "Hire Date"])
        employees.loc[row_index, "Termination Date"] = (hire_date - timedelta(days=20)).isoformat()
        employees.loc[row_index, "Employment Status"] = "Terminated"

    for row_index in random_generator.sample(list(employees.index), 18):
        employees.loc[row_index, "Employment Status"] = "Active"
        employees.loc[row_index, "Termination Date"] = random_date(
            random_generator, date(end_date.year, 1, 1), end_date
        ).isoformat()

    duplicate_rows = employees.sample(n=20, random_state=11).copy()
    duplicate_rows["Department Code"] = duplicate_rows["Department Code"].replace({"ENG": " eng "})
    return pd.concat([employees, duplicate_rows], ignore_index=True)


def generate_compensation(employees: pd.DataFrame, config: dict) -> pd.DataFrame:
    random_generator = random.Random(config["random_seed"] + 1)
    start_date = date.fromisoformat(config["synthetic_data"]["start_date"])
    end_date = date.fromisoformat(config["synthetic_data"]["end_date"])
    job_band_lookup = {code: (band_min, band_max) for code, _, _, _, band_min, band_max in JOB_ROLES}

    valid_employee_rows = employees[employees["Employee ID"].str.strip().str.startswith("E", na=False)]
    sampled_rows = valid_employee_rows.sample(frac=0.96, random_state=17)

    compensation_rows = []
    for _, employee in sampled_rows.iterrows():
        band_min, band_max = job_band_lookup.get(str(employee["Job Code"]).strip().upper(), (55000, 130000))
        salary = random_generator.randint(band_min, band_max)
        salary_text = random_generator.choice(
            [
                str(salary),
                f"${salary:,.0f}",
                f"USD {salary:,.0f}",
                f" {salary} ",
            ]
        )
        compensation_rows.append(
            {
                "Employee ID": employee["Employee ID"],
                "Annual Salary": salary_text,
                "Bonus Target Percent": random_generator.choice([0, 5, 8, 10, 12, 15, 20]),
                "Effective Date": random_date(random_generator, start_date, end_date).isoformat(),
                "Currency": "USD",
                "Pay Frequency": "Annual",
            }
        )

    for index in range(1, 26):
        compensation_rows.append(
            {
                "Employee ID": f"X{index:05d}",
                "Annual Salary": random_generator.choice(["$75,000", "85000", "N/A"]),
                "Bonus Target Percent": 5,
                "Effective Date": random_date(random_generator, start_date, end_date).isoformat(),
                "Currency": "USD",
                "Pay Frequency": "Annual",
            }
        )

    compensation_df = pd.DataFrame(compensation_rows)
    for row_index in random_generator.sample(list(compensation_df.index), 15):
        compensation_df.loc[row_index, "Annual Salary"] = random_generator.choice(["N/A", "-5000", "999999"])

    return compensation_df


def generate_events(employees: pd.DataFrame, config: dict) -> pd.DataFrame:
    random_generator = random.Random(config["random_seed"] + 2)
    event_rows = []

    for _, employee in employees.drop_duplicates("Employee ID").iterrows():
        employee_id = str(employee["Employee ID"]).strip()
        if not employee_id:
            continue

        event_rows.append(
            {
                "Employee ID": employee_id,
                "Event Type": "Hire",
                "Event Date": employee["Hire Date"],
                "Department Code": employee["Department Code"],
                "Job Code": employee["Job Code"],
                "Termination Type": "",
                "Event Reason": "New Hire",
            }
        )

        if str(employee["Termination Date"]).strip():
            event_rows.append(
                {
                    "Employee ID": employee_id,
                    "Event Type": "Termination",
                    "Event Date": employee["Termination Date"],
                    "Department Code": employee["Department Code"],
                    "Job Code": employee["Job Code"],
                    "Termination Type": random_generator.choice(["Voluntary", "Involuntary"]),
                    "Event Reason": random_generator.choice(["Resignation", "Performance", "Layoff", "Career Change"]),
                }
            )

        if random_generator.random() < 0.12:
            event_rows.append(
                {
                    "Employee ID": employee_id,
                    "Event Type": random_generator.choice(["Promotion", "Transfer"]),
                    "Event Date": employee["Hire Date"],
                    "Department Code": random_generator.choice([item[0] for item in DEPARTMENTS]),
                    "Job Code": random_generator.choice([item[0] for item in JOB_ROLES]),
                    "Termination Type": "",
                    "Event Reason": "Internal Movement",
                }
            )

    event_rows.append(
        {
            "Employee ID": "E999999",
            "Event Type": "Transfer",
            "Event Date": config["synthetic_data"]["end_date"],
            "Department Code": "ENG",
            "Job Code": "ENG2",
            "Termination Type": "",
            "Event Reason": "Invalid employee test row",
        }
    )

    return pd.DataFrame(event_rows)


def generate_manager_hierarchy(employees: pd.DataFrame, config: dict) -> pd.DataFrame:
    random_generator = random.Random(config["random_seed"] + 3)
    active_employees = employees[
        employees["Employee ID"].str.strip().str.startswith("E", na=False)
    ].drop_duplicates("Employee ID")
    manager_candidates = active_employees.sample(n=min(280, len(active_employees)), random_state=23)[
        "Employee ID"
    ].tolist()

    rows = []
    for _, employee in active_employees.iterrows():
        employee_id = str(employee["Employee ID"]).strip()
        manager_id = random_generator.choice(manager_candidates)
        if manager_id == employee_id:
            manager_id = ""

        rows.append(
            {
                "Employee ID": employee_id,
                "Manager Employee ID": manager_id,
                "Effective Date": employee["Hire Date"],
                "End Date": "",
            }
        )

    for row_index in random_generator.sample(range(len(rows)), 18):
        rows[row_index]["Manager Employee ID"] = random_generator.choice(["E999998", "", "BADMANAGER"])

    conflict_rows = random_generator.sample(rows, 15)
    for row in conflict_rows:
        rows.append({**row, "Manager Employee ID": random_generator.choice(manager_candidates)})

    return pd.DataFrame(rows)


def generate_workforce_plan(config: dict) -> pd.DataFrame:
    random_generator = random.Random(config["random_seed"] + 4)
    start_month = pd.Timestamp(config["synthetic_data"]["start_date"]).to_period("M").to_timestamp()
    end_month = pd.Timestamp(config["synthetic_data"]["end_date"]).to_period("M").to_timestamp()
    months = pd.date_range(start_month, end_month, freq="MS")

    rows = []
    for month_start in months:
        for department_code, department_name, _ in DEPARTMENTS:
            base_plan = random_generator.randint(120, 420)
            month_adjustment = int((month_start.year - start_month.year) * random_generator.uniform(2, 8))
            planned_headcount = base_plan + month_adjustment + random_generator.randint(-20, 25)
            if random_generator.random() < 0.005:
                planned_headcount = -3

            rows.append(
                {
                    "Plan Month": month_start.date().isoformat(),
                    "Department Code": department_code,
                    "Department Name": random_generator.choice(
                        [department_name, department_name.upper(), f" {department_name} "]
                    ),
                    "Planned Headcount": planned_headcount,
                    "Plan Version": "2025 Operating Plan",
                }
            )

    return pd.DataFrame(rows)


def generate_all_raw_data(config: dict) -> dict[str, int]:
    raw_dir = project_path(config["paths"]["raw_data_dir"])
    raw_dir.mkdir(parents=True, exist_ok=True)

    generate_reference_files(raw_dir)
    employees = generate_employee_rows(config)
    compensation = generate_compensation(employees, config)
    events = generate_events(employees, config)
    manager_hierarchy = generate_manager_hierarchy(employees, config)
    workforce_plan = generate_workforce_plan(config)

    employees.to_csv(raw_dir / "employees.csv", index=False)
    compensation.to_csv(raw_dir / "compensation.csv", index=False)
    events.to_csv(raw_dir / "employment_events.csv", index=False)
    manager_hierarchy.to_csv(raw_dir / "manager_hierarchy.csv", index=False)
    workforce_plan.to_csv(raw_dir / "workforce_plan.csv", index=False)

    return {
        "employees": len(employees),
        "compensation": len(compensation),
        "employment_events": len(events),
        "manager_hierarchy": len(manager_hierarchy),
        "workforce_plan": len(workforce_plan),
        "departments": len(pd.read_csv(raw_dir / "departments.csv")),
        "locations": len(pd.read_csv(raw_dir / "locations.csv")),
        "job_roles": len(pd.read_csv(raw_dir / "job_roles.csv")),
    }
