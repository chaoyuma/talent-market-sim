from sqlalchemy.orm import Session
from app.models.student import Student


def create_student(db: Session, data: dict):
    obj = Student(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def bulk_create_students(db: Session, data_list: list[dict]):
    objs = [Student(**item) for item in data_list]
    db.add_all(objs)
    db.commit()
    return objs


def list_students(db: Session):
    return db.query(Student).all()


def count_students(db: Session):
    return db.query(Student).count()