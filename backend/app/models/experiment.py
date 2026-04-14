from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String(64), unique=True, nullable=False, index=True)
    scenario_name = Column(String(128), nullable=True)
    config_snapshot_json = Column(JSON, nullable=False)
    status = Column(String(32), nullable=False, default="created")

    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)