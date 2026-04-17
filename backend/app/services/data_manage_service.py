# backend/app/services/data_manage_service.py

import random

from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.repositories.student_repository import list_students
from app.repositories.school_repository import list_schools
from app.repositories.employer_repository import list_employers
from app.repositories.major_repository import list_majors
from app.repositories.job_repository import list_jobs
from app.repositories.major_industry_mapping_repository import (
    list_major_industry_mappings,
)


def _sample_entities(items, target_count, random_seed=42):
    """
    对数据库读取到的主体做抽样。
    """
    if not items:
        return []

    if target_count is None or target_count <= 0:
        return items

    if len(items) <= target_count:
        return items

    rng = random.Random(random_seed)
    return rng.sample(items, target_count)


def load_simulation_data(
    num_students: int | None = None,
    num_schools: int | None = None,
    num_employers: int | None = None,
    random_seed: int = 42,
):
    """
    加载仿真所需基础数据。
    当前逻辑：
    - 学生、学校、企业从数据库读取后按规模参数抽样
    - 专业、岗位模板全量读取
    """
    db = SessionLocal()
    try:
        students = list_students(db)
        schools = list_schools(db)
        employers = list_employers(db)
        majors = list_majors(db)
        jobs = list_jobs(db)
        try:
            major_industry_mappings = list_major_industry_mappings(db)
        except SQLAlchemyError:
            db.rollback()
            major_industry_mappings = []

        students = _sample_entities(students, num_students, random_seed)
        schools = _sample_entities(schools, num_schools, random_seed)
        employers = _sample_entities(employers, num_employers, random_seed)

        return {
            "students": students,
            "schools": schools,
            "employers": employers,
            "majors": majors,
            "jobs": jobs,
            "major_industry_mappings": major_industry_mappings,
        }
    finally:
        db.close()
