from datetime import datetime
from sqlalchemy.orm import Session
from app.models.experiment import Experiment


def create_experiment(
    db: Session,
    experiment_id: str,
    config_snapshot_json: dict,
    scenario_name: str | None = None,
    status: str = "running",
):
    obj = Experiment(
        experiment_id=experiment_id,
        scenario_name=scenario_name,
        config_snapshot_json=config_snapshot_json,
        status=status,
        started_at=datetime.now(),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_experiment_status(
    db: Session,
    experiment_id: str,
    status: str,
):
    obj = db.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    if not obj:
        return None

    obj.status = status
    if status in ["finished", "failed"]:
        obj.finished_at = datetime.now()

    db.commit()
    db.refresh(obj)
    return obj



def list_experiments(db):
    return (
        db.query(Experiment)
        .order_by(Experiment.created_at.desc())
        .all()
    )


def get_experiment_by_experiment_id(db, experiment_id: str):
    return (
        db.query(Experiment)
        .filter(Experiment.experiment_id == experiment_id)
        .first()
    )