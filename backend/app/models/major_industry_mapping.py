from sqlalchemy import Column, BigInteger, String, Float, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class MajorIndustryMapping(Base):
    __tablename__ = "major_industry_mapping"

    id = Column(BigInteger, primary_key=True, index=True)
    major_name = Column(String(100), nullable=False, index=True)
    industry = Column(String(100), nullable=False, index=True)
    match_score = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)