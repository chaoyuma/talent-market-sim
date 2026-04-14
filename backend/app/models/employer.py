from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Employer(Base):
    __tablename__ = "employers"

    id = Column(Integer, primary_key=True, index=True)
    employer_code = Column(String(64), unique=True, nullable=False, index=True)
    employer_name = Column(String(128), nullable=False)

    employer_type = Column(String(64), nullable=False, index=True)
    industry = Column(String(64), nullable=True)
    city = Column(String(64), nullable=True)

    base_salary = Column(Float, nullable=False, default=10.0)
    growth_factor = Column(Float, nullable=False, default=1.0)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)