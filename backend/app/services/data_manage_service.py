from app.core.database import SessionLocal
from app.repositories.student_repository import list_students
from app.repositories.school_repository import list_schools
from app.repositories.employer_repository import list_employers
from app.repositories.major_repository import list_majors
from app.repositories.job_repository import list_jobs


def load_simulation_data():
    db = SessionLocal()
    try:
        students = list_students(db)
        schools = list_schools(db)
        employers = list_employers(db)
        majors = list_majors(db)
        jobs = list_jobs(db)

        return {
            "students": students,
            "schools": schools,
            "employers": employers,
            "majors": majors,
            "jobs": jobs,
        }
    finally:
        db.close()