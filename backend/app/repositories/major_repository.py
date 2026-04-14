from sqlalchemy.orm import Session
from app.models.major import Major


def bulk_create_majors(db: Session, data_list: list[dict]):
    objs = [Major(**item) for item in data_list]
    db.add_all(objs)
    db.commit()
    return objs


def list_majors(db: Session):
    return db.query(Major).all()


def count_majors(db: Session):
    return db.query(Major).count()