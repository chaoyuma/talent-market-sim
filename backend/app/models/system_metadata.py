from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class SystemMetadata(Base):
    __tablename__ = "system_metadata"

    id = Column(BigInteger, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False, index=True)
    field_name = Column(String(100), nullable=True, index=True)
    field_type = Column(String(100), nullable=True)
    is_nullable = Column(Integer, nullable=True)
    default_value = Column(String(255), nullable=True)
    field_meaning = Column(String(1000), nullable=False)
    example_value = Column(String(255), nullable=True)
    data_source = Column(String(255), nullable=True)
    notes = Column(String(1000), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )