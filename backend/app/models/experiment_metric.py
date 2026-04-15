from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class ExperimentMetric(Base):
    __tablename__ = "experiment_metrics"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String(64), nullable=False, index=True)

    step = Column(Integer, nullable=False)

    student_count = Column(Integer, nullable=False, default=0)
    school_count = Column(Integer, nullable=False, default=0)
    employer_count = Column(Integer, nullable=False, default=0)

    employment_rate = Column(Float, nullable=False, default=0.0)
    matching_rate = Column(Float, nullable=False, default=0.0)
    cross_major_rate = Column(Float, nullable=False, default=0.0)
    avg_salary = Column(Float, nullable=False, default=0.0)
    avg_satisfaction = Column(Float, nullable=False, default=0.0)

    active_job_seekers = Column(Integer, nullable=False, default=0)
    round_job_count = Column(Integer, nullable=False, default=0)
    round_filled_jobs = Column(Integer, nullable=False, default=0)
    round_vacancy_rate = Column(Float, nullable=False, default=0.0)
    round_new_employment_rate = Column(Float, nullable=False, default=0.0)

    mismatch_index = Column(Float, nullable=False, default=0.0)
    herding_index = Column(Float, nullable=False, default=0.0)
    avg_hire_threshold = Column(Float, nullable=False, default=0.0)
    avg_cross_major_tolerance = Column(Float, nullable=False, default=0.0)
    avg_training_quality = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)