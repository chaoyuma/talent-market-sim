from sqlalchemy.orm import Session
from app.models.employer import Employer


def bulk_create_employers(db: Session, data_list: list[dict]):
    objs = [Employer(**item) for item in data_list]
    db.add_all(objs)
    db.commit()
    return objs


def list_employers(db: Session):
    return db.query(Employer).all()


def count_employers(db: Session):
    return db.query(Employer).count()