from app.core.database import SessionLocal
from app.repositories.student_repository import bulk_create_students
from app.repositories.school_repository import bulk_create_schools
from app.repositories.employer_repository import bulk_create_employers
from app.repositories.major_repository import bulk_create_majors
from app.repositories.job_repository import bulk_create_jobs


def seed_majors(db):
    data = [
        {"major_code": "M001", "major_name": "CS", "category": "STEM", "skill_direction": "software", "heat_init": 1.0, "mobility": 0.8},
        {"major_code": "M002", "major_name": "Finance", "category": "Business", "skill_direction": "analysis", "heat_init": 0.9, "mobility": 0.6},
        {"major_code": "M003", "major_name": "Mechanical", "category": "Engineering", "skill_direction": "manufacturing", "heat_init": 0.8, "mobility": 0.5},
        {"major_code": "M004", "major_name": "Education", "category": "Social", "skill_direction": "teaching", "heat_init": 0.7, "mobility": 0.4},
    ]
    bulk_create_majors(db, data)


def seed_schools(db):
    data = [
        {"school_code": "S001", "school_name": "Research University A", "school_type": "research_university", "region": "Beijing", "tier": "high", "training_quality": 0.9, "reputation": 0.95},
        {"school_code": "S002", "school_name": "Applied University B", "school_type": "applied_university", "region": "Shanghai", "tier": "mid", "training_quality": 0.75, "reputation": 0.75},
        {"school_code": "S003", "school_name": "Vocational College C", "school_type": "vocational_college", "region": "Hebei", "tier": "basic", "training_quality": 0.65, "reputation": 0.6},
    ]
    bulk_create_schools(db, data)


def seed_employers(db):
    data = [
        {"employer_code": "E001", "employer_name": "Tech Corp", "employer_type": "tech_strict", "industry": "IT", "city": "Beijing", "base_salary": 18, "growth_factor": 1.2},
        {"employer_code": "E002", "employer_name": "Growth Startup", "employer_type": "growth_firm", "industry": "Internet", "city": "Shanghai", "base_salary": 15, "growth_factor": 1.3},
        {"employer_code": "E003", "employer_name": "Traditional Factory", "employer_type": "traditional_firm", "industry": "Manufacturing", "city": "Tianjin", "base_salary": 12, "growth_factor": 1.0},
        {"employer_code": "E004", "employer_name": "Cost Control Ltd", "employer_type": "cost_sensitive", "industry": "Services", "city": "Shijiazhuang", "base_salary": 10, "growth_factor": 0.9},
    ]
    bulk_create_employers(db, data)


def seed_jobs(db):
    data = [
        {"job_code": "J001", "job_name": "Software Engineer", "industry": "IT", "major_code": "M001", "skill_required": 0.75, "salary_base": 18, "city": "Beijing", "cross_major_allowed": True},
        {"job_code": "J002", "job_name": "Data Analyst", "industry": "Finance", "major_code": "M002", "skill_required": 0.65, "salary_base": 14, "city": "Shanghai", "cross_major_allowed": True},
        {"job_code": "J003", "job_name": "Mechanical Engineer", "industry": "Manufacturing", "major_code": "M003", "skill_required": 0.70, "salary_base": 13, "city": "Tianjin", "cross_major_allowed": False},
        {"job_code": "J004", "job_name": "Teacher", "industry": "Education", "major_code": "M004", "skill_required": 0.60, "salary_base": 11, "city": "Hebei", "cross_major_allowed": False},
    ]
    bulk_create_jobs(db, data)


def seed_students(db):
    data = [
        {"student_code": "ST001", "student_type": "employment_oriented", "gender": "M", "region": "Hebei", "ability": 0.82, "interest_major": "CS", "city_preference": "Beijing", "expected_salary": 15, "risk_preference": 0.6, "information_level": 0.8},
        {"student_code": "ST002", "student_type": "interest_oriented", "gender": "F", "region": "Beijing", "ability": 0.70, "interest_major": "Education", "city_preference": "Beijing", "expected_salary": 10, "risk_preference": 0.4, "information_level": 0.7},
        {"student_code": "ST003", "student_type": "prestige_oriented", "gender": "M", "region": "Shandong", "ability": 0.88, "interest_major": "Finance", "city_preference": "Shanghai", "expected_salary": 14, "risk_preference": 0.5, "information_level": 0.75},
        {"student_code": "ST004", "student_type": "trend_sensitive", "gender": "F", "region": "Henan", "ability": 0.76, "interest_major": "CS", "city_preference": "Shanghai", "expected_salary": 13, "risk_preference": 0.7, "information_level": 0.9},
    ]
    bulk_create_students(db, data)


def run_seed():
    db = SessionLocal()
    try:
        seed_majors(db)
        seed_schools(db)
        seed_employers(db)
        seed_jobs(db)
        seed_students(db)
        print("Seed data inserted successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()