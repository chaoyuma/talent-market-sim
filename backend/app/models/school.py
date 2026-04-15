from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    school_code = Column(String(64), unique=True, nullable=False, index=True)
    school_name = Column(String(128), nullable=False)

    school_type = Column(String(64), nullable=False, index=True)
    region = Column(String(64), nullable=True)
    tier = Column(String(64), nullable=True)

    training_quality = Column(Float, nullable=False, default=0.7)
    reputation = Column(Float, nullable=False, default=0.7)
    resource_support = Column(Float, nullable=False, default=0.03)
    capacity_base = Column(Integer, nullable=False, default=500)
    city_tier = Column(Float, nullable=False, default=0.5)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)