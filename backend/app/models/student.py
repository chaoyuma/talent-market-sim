from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_code = Column(String(64), unique=True, nullable=False, index=True)
    student_type = Column(String(64), nullable=False, index=True)

    gender = Column(String(16), nullable=True)
    region = Column(String(64), nullable=True)

    ability = Column(Float, nullable=False, default=0.5)
    interest_major = Column(String(64), nullable=True)
    city_preference = Column(String(64), nullable=True)  # 保留旧字段
    city_tier_preference = Column(Float, nullable=False, default=0.5)

    expected_salary = Column(Float, nullable=False, default=10.0)
    risk_preference = Column(Float, nullable=False, default=0.5)
    information_level = Column(Float, nullable=False, default=0.8)
    career_growth_preference = Column(Float, nullable=False, default=0.5)
    learning_effort = Column(Float, nullable=False, default=0.7)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)