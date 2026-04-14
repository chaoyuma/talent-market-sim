from sqlalchemy.orm import Session
from app.models.job import Job


def bulk_create_jobs(db: Session, data_list: list[dict]):
    objs = [Job(**item) for item in data_list]
    db.add_all(objs)
    db.commit()
    return objs


def list_jobs(db: Session):
    return db.query(Job).all()


def count_jobs(db: Session):
    return db.query(Job).count()