from sqlalchemy import Column, BigInteger, String, DateTime, Text, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class SimulationReport(Base):
    __tablename__ = "simulation_report"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_id = Column(String(64), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    report_type = Column(String(64), nullable=False, default="comparison")
    status = Column(String(32), nullable=False, default="finished")
    experiment_ids_json = Column(JSON, nullable=True)
    report_markdown = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    used_llm = Column(BigInteger, nullable=False, default=0)
    fallback_reason = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())