from sqlalchemy import Column, BigInteger, String, JSON, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class ConfigTemplate(Base):
    __tablename__ = "config_templates"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    template_name = Column(String(128), nullable=False, unique=True, index=True)
    template_desc = Column(String(255), nullable=True)
    config_json = Column(JSON, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )