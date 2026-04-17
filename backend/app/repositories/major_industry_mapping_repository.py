from sqlalchemy.orm import Session

from app.models.major_industry_mapping import MajorIndustryMapping


def list_major_industry_mappings(db: Session):
    return db.query(MajorIndustryMapping).all()

