from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String(64), nullable=False, index=True)
    report_type = Column(String(64), nullable=False, default="summary")

    summary_text = Column(Text, nullable=True)
    full_report_text = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)