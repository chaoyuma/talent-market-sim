import random
from pathlib import Path

import pandas as pd


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "generated_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def truncated_normal(mean=0.6, std=0.15, low=0.0, high=1.0):
    while True:
        x = random.gauss(mean, std)
        if low <= x <= high:
            return round(x, 4)


def generate_majors():
    rows = [
        {
            "major_code": "M001",
            "major_name": "CS",
            "category": "STEM",
            "skill_direction": "Software,AI,Data",
            "heat_init": 1.20,
            "mobility": 0.80,
            "salary_expectation": 0.95,
            "policy_support_weight": 0.80,
        },
        {
            "major_code": "M002",
            "major_name": "Finance",
            "category": "Economics",
            "skill_direction": "Accounting,Investment,Risk",
            "heat_init": 1.00,
            "mobility": 0.65,
            "salary_expectation": 0.85,
            "policy_support_weight": 0.50,
        },
        {
            "major_code": "M003",
            "major_name": "Mechanical",
            "category": "Engineering",
            "skill_direction": "Design,Manufacturing,Equipment",
            "heat_init": 0.90,
            "mobility": 0.55,
            "salary_expectation": 0.75,
            "policy_support_weight": 0.60,
        },
        {
            "major_code": "M004",
            "major_name": "Education",
            "category": "Social",
            "skill_direction": "Teaching,Training,PublicService",
            "heat_init": 0.70,
            "mobility": 0.40,
            "salary_expectation": 0.65,
            "policy_support_weight": 0.70,
        },
        {
            "major_code": "M005",
            "major_name": "Medicine",
            "category": "Health",
            "skill_direction": "Clinical,Health,PublicHealth",
            "heat_init": 1.10,
            "mobility": 0.60,
            "salary_expectation": 0.90,
            "policy_support_weight": 0.85,
        },
        {
            "major_code": "M006",
            "major_name": "Civil",
            "category": "Engineering",
            "skill_direction": "Construction,Infrastructure,Survey",
            "heat_init": 0.85,
            "mobility": 0.50,
            "salary_expectation": 0.72,
            "policy_support_weight": 0.65,
        },
    ]
    return pd.DataFrame(rows)


def generate_schools(n=18):
    school_types = (
        ["research_university"] * 4
        + ["applied_university"] * 8
        + ["vocational_college"] * 6
    )
    regions = ["East", "North", "South", "Central", "West"]
    tiers = ["A", "B", "C"]

    rows = []
    for i in range(n):
        school_type = school_types[i % len(school_types)]

        if school_type == "research_university":
            training_quality = round(random.uniform(0.80, 0.95), 4)
            reputation = round(random.uniform(0.80, 0.95), 4)
            resource_support = round(random.uniform(0.04, 0.08), 4)
            capacity_base = random.randint(800, 2000)
            city_tier = round(random.uniform(0.75, 0.95), 4)
            tier = "A"
        elif school_type == "applied_university":
            training_quality = round(random.uniform(0.65, 0.80), 4)
            reputation = round(random.uniform(0.60, 0.80), 4)
            resource_support = round(random.uniform(0.02, 0.05), 4)
            capacity_base = random.randint(500, 1200)
            city_tier = round(random.uniform(0.55, 0.85), 4)
            tier = "B"
        else:
            training_quality = round(random.uniform(0.55, 0.75), 4)
            reputation = round(random.uniform(0.45, 0.65), 4)
            resource_support = round(random.uniform(0.01, 0.04), 4)
            capacity_base = random.randint(300, 800)
            city_tier = round(random.uniform(0.40, 0.70), 4)
            tier = "C"

        rows.append({
            "school_code": f"S{i+1:03d}",
            "school_name": f"School_{i+1}",
            "school_type": school_type,
            "region": random.choice(regions),
            "tier": tier,
            "training_quality": training_quality,
            "reputation": reputation,
            "resource_support": resource_support,
            "capacity_base": capacity_base,
            "city_tier": city_tier,
        })

    return pd.DataFrame(rows)


def generate_employers(n=60):
    employer_types = ["tech_strict", "growth_firm", "traditional_firm", "cost_sensitive"]
    industries = ["Internet", "Finance", "Manufacturing", "Education", "Healthcare", "Construction"]
    regions = ["East", "North", "South", "Central", "West"]

    rows = []
    for i in range(n):
        t = random.choice(employer_types)

        if t == "tech_strict":
            base_salary = round(random.uniform(14, 28), 2)
            growth_factor = round(random.uniform(1.05, 1.30), 4)
            major_preference_strength = round(random.uniform(0.80, 0.95), 4)
            skill_preference_strength = round(random.uniform(0.85, 0.98), 4)
            hire_threshold = round(random.uniform(0.70, 0.85), 4)
            cross_major_tolerance = round(random.uniform(0.20, 0.45), 4)
            salary_elasticity = round(random.uniform(0.03, 0.08), 4)
            threshold_relax_speed = round(random.uniform(0.01, 0.04), 4)
            tolerance_increase_speed = round(random.uniform(0.01, 0.04), 4)
            stability = round(random.uniform(0.45, 0.65), 4)
        elif t == "growth_firm":
            base_salary = round(random.uniform(12, 24), 2)
            growth_factor = round(random.uniform(1.10, 1.50), 4)
            major_preference_strength = round(random.uniform(0.60, 0.80), 4)
            skill_preference_strength = round(random.uniform(0.75, 0.90), 4)
            hire_threshold = round(random.uniform(0.55, 0.75), 4)
            cross_major_tolerance = round(random.uniform(0.40, 0.70), 4)
            salary_elasticity = round(random.uniform(0.06, 0.12), 4)
            threshold_relax_speed = round(random.uniform(0.02, 0.06), 4)
            tolerance_increase_speed = round(random.uniform(0.02, 0.06), 4)
            stability = round(random.uniform(0.35, 0.60), 4)
        elif t == "traditional_firm":
            base_salary = round(random.uniform(10, 18), 2)
            growth_factor = round(random.uniform(0.95, 1.10), 4)
            major_preference_strength = round(random.uniform(0.75, 0.90), 4)
            skill_preference_strength = round(random.uniform(0.65, 0.85), 4)
            hire_threshold = round(random.uniform(0.55, 0.75), 4)
            cross_major_tolerance = round(random.uniform(0.30, 0.55), 4)
            salary_elasticity = round(random.uniform(0.02, 0.06), 4)
            threshold_relax_speed = round(random.uniform(0.01, 0.04), 4)
            tolerance_increase_speed = round(random.uniform(0.01, 0.04), 4)
            stability = round(random.uniform(0.70, 0.90), 4)
        else:
            base_salary = round(random.uniform(8, 15), 2)
            growth_factor = round(random.uniform(0.90, 1.05), 4)
            major_preference_strength = round(random.uniform(0.50, 0.75), 4)
            skill_preference_strength = round(random.uniform(0.60, 0.80), 4)
            hire_threshold = round(random.uniform(0.45, 0.65), 4)
            cross_major_tolerance = round(random.uniform(0.50, 0.85), 4)
            salary_elasticity = round(random.uniform(0.01, 0.05), 4)
            threshold_relax_speed = round(random.uniform(0.02, 0.05), 4)
            tolerance_increase_speed = round(random.uniform(0.02, 0.05), 4)
            stability = round(random.uniform(0.50, 0.75), 4)

        rows.append({
            "employer_code": f"E{i+1:04d}",
            "employer_name": f"Employer_{i+1}",
            "employer_type": t,
            "industry": random.choice(industries),
            "city": f"City_{random.randint(1, 20)}",
            "region": random.choice(regions),
            "city_tier": round(random.uniform(0.4, 0.95), 4),
            "base_salary": base_salary,
            "growth_factor": growth_factor,
            "major_preference_strength": major_preference_strength,
            "skill_preference_strength": skill_preference_strength,
            "hire_threshold": hire_threshold,
            "cross_major_tolerance": cross_major_tolerance,
            "salary_elasticity": salary_elasticity,
            "threshold_relax_speed": threshold_relax_speed,
            "tolerance_increase_speed": tolerance_increase_speed,
            "stability": stability,
        })

    return pd.DataFrame(rows)


def generate_students(n=400):
    majors = ["CS", "Finance", "Mechanical", "Education", "Medicine", "Civil"]
    major_probs = [0.25, 0.18, 0.18, 0.12, 0.15, 0.12]
    student_types = ["employment_oriented", "interest_oriented", "prestige_oriented", "trend_sensitive"]
    student_type_probs = [0.35, 0.25, 0.15, 0.25]
    regions = ["East", "North", "South", "Central", "West"]

    major_salary_map = {
        "CS": (14, 26),
        "Finance": (12, 22),
        "Mechanical": (10, 18),
        "Education": (8, 14),
        "Medicine": (13, 24),
        "Civil": (10, 17),
    }

    rows = []
    for i in range(n):
        interest_major = random.choices(majors, weights=major_probs, k=1)[0]
        student_type = random.choices(student_types, weights=student_type_probs, k=1)[0]
        sal_low, sal_high = major_salary_map[interest_major]

        rows.append({
            "student_code": f"STU{i+1:05d}",
            "student_type": student_type,
            "gender": random.choice(["male", "female"]),
            "region": random.choice(regions),
            "ability": truncated_normal(),
            "interest_major": interest_major,
            "city_preference": f"City_{random.randint(1, 20)}",
            "city_tier_preference": round(random.uniform(0.4, 0.95), 4),
            "expected_salary": round(random.uniform(sal_low, sal_high), 2),
            "risk_preference": round(random.uniform(0.2, 0.9), 4),
            "information_level": round(random.uniform(0.4, 0.95), 4),
            "career_growth_preference": round(random.uniform(0.3, 0.95), 4),
            "learning_effort": round(random.uniform(0.4, 1.0), 4),
        })

    return pd.DataFrame(rows)


def generate_jobs(n=300):
    major_job_rules = {
        "CS": ("Internet", "软件开发工程师", 14, 28, 0.65, 0.95, 1.10, 1.40),
        "Finance": ("Finance", "金融分析专员", 12, 24, 0.55, 0.85, 0.95, 1.20),
        "Mechanical": ("Manufacturing", "机械设计工程师", 10, 18, 0.50, 0.80, 0.85, 1.05),
        "Education": ("Education", "教学与教研专员", 8, 15, 0.45, 0.75, 0.70, 0.90),
        "Medicine": ("Healthcare", "医疗健康专员", 13, 24, 0.60, 0.90, 1.00, 1.25),
        "Civil": ("Construction", "土木工程项目专员", 10, 17, 0.50, 0.80, 0.80, 1.00),
    }

    major_code_map = {
        "CS": "M001",
        "Finance": "M002",
        "Mechanical": "M003",
        "Education": "M004",
        "Medicine": "M005",
        "Civil": "M006",
    }

    rows = []
    majors = list(major_job_rules.keys())
    for i in range(n):
        major = random.choice(majors)
        industry, job_name, sal_low, sal_high, skill_low, skill_high, heat_low, heat_high = major_job_rules[major]

        rows.append({
            "job_code": f"JOB{i+1:05d}",
            "job_name": f"{job_name}_{i+1}",
            "industry": industry,
            "major_code": major_code_map[major],
            "skill_required": round(random.uniform(skill_low, skill_high), 4),
            "salary_base": round(random.uniform(sal_low, sal_high), 2),
            "city": f"City_{random.randint(1, 20)}",
            "cross_major_allowed": random.choice([True, True, True, False]),
            "career_growth": round(random.uniform(0.4, 0.95), 4),
            "city_tier": round(random.uniform(0.4, 0.95), 4),
            "industry_heat": round(random.uniform(heat_low, heat_high), 4),
        })

    return pd.DataFrame(rows)


def generate_major_industry_mapping():
    rows = [
        {"major_name": "CS", "industry": "Internet", "match_score": 1.0},
        {"major_name": "CS", "industry": "Finance", "match_score": 0.6},
        {"major_name": "CS", "industry": "Manufacturing", "match_score": 0.4},

        {"major_name": "Finance", "industry": "Finance", "match_score": 1.0},
        {"major_name": "Finance", "industry": "Internet", "match_score": 0.5},
        {"major_name": "Finance", "industry": "Education", "match_score": 0.3},

        {"major_name": "Mechanical", "industry": "Manufacturing", "match_score": 1.0},
        {"major_name": "Mechanical", "industry": "Construction", "match_score": 0.6},
        {"major_name": "Mechanical", "industry": "Internet", "match_score": 0.2},

        {"major_name": "Education", "industry": "Education", "match_score": 1.0},

        {"major_name": "Medicine", "industry": "Healthcare", "match_score": 1.0},

        {"major_name": "Civil", "industry": "Construction", "match_score": 1.0},
        {"major_name": "Civil", "industry": "Manufacturing", "match_score": 0.4},
    ]
    return pd.DataFrame(rows)


def main():
    majors = generate_majors()
    schools = generate_schools()
    employers = generate_employers()
    students = generate_students()
    jobs = generate_jobs()
    mapping = generate_major_industry_mapping()

    majors.to_csv(OUTPUT_DIR / "majors.csv", index=False, encoding="utf-8-sig")
    schools.to_csv(OUTPUT_DIR / "schools.csv", index=False, encoding="utf-8-sig")
    employers.to_csv(OUTPUT_DIR / "employers.csv", index=False, encoding="utf-8-sig")
    students.to_csv(OUTPUT_DIR / "students.csv", index=False, encoding="utf-8-sig")
    jobs.to_csv(OUTPUT_DIR / "jobs.csv", index=False, encoding="utf-8-sig")
    mapping.to_csv(OUTPUT_DIR / "major_industry_mapping.csv", index=False, encoding="utf-8-sig")

    print("Seed data generated successfully.")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()