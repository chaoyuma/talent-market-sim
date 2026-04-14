from sqlalchemy.orm import Session
from app.models.school import School


def bulk_create_schools(db: Session, data_list: list[dict]):
    objs = [School(**item) for item in data_list]
    db.add_all(objs)
    db.commit()
    return objs


def list_schools(db: Session):
    return db.query(School).all()


def count_schools(db: Session):
    return db.query(School).count()