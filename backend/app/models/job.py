from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_code = Column(String(64), unique=True, nullable=False, index=True)
    job_name = Column(String(128), nullable=False)

    industry = Column(String(64), nullable=True)
    major_code = Column(String(64), nullable=True)
    skill_required = Column(Float, nullable=False, default=0.5)
    salary_base = Column(Float, nullable=False, default=10.0)
    city = Column(String(64), nullable=True)
    cross_major_allowed = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)