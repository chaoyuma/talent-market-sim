from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Major(Base):
    __tablename__ = "majors"

    id = Column(Integer, primary_key=True, index=True)
    major_code = Column(String(64), unique=True, nullable=False, index=True)
    major_name = Column(String(128), nullable=False)

    category = Column(String(64), nullable=True)
    skill_direction = Column(String(128), nullable=True)

    heat_init = Column(Float, nullable=False, default=1.0)
    mobility = Column(Float, nullable=False, default=0.5)
    salary_expectation = Column(Float, nullable=False, default=0.7)
    policy_support_weight = Column(Float, nullable=False, default=0.5)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)