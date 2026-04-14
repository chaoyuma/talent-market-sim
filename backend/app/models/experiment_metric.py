from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class ExperimentMetric(Base):
    __tablename__ = "experiment_metrics"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String(64), nullable=False, index=True)

    step = Column(Integer, nullable=False)
    employment_rate = Column(Float, nullable=False, default=0.0)
    matching_rate = Column(Float, nullable=False, default=0.0)
    cross_major_rate = Column(Float, nullable=False, default=0.0)
    vacancy_rate = Column(Float, nullable=False, default=0.0)
    filled_jobs = Column(Integer, nullable=False, default=0)
    avg_salary = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)