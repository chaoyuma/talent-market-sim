from sqlalchemy.orm import Session
from app.models.experiment_metric import ExperimentMetric


def bulk_create_experiment_metrics(
    db: Session,
    experiment_id: str,
    metrics_list: list[dict],
):
    objs = []
    for item in metrics_list:
        obj = ExperimentMetric(
            experiment_id=experiment_id,
            step=item["step"],
            employment_rate=item.get("employment_rate", 0.0),
            matching_rate=item.get("matching_rate", 0.0),
            cross_major_rate=item.get("cross_major_rate", 0.0),
            vacancy_rate=item.get("vacancy_rate", 0.0),
            filled_jobs=item.get("filled_jobs", 0),
            avg_salary=item.get("avg_salary", 0.0),
        )
        objs.append(obj)

    db.add_all(objs)
    db.commit()
    return objs


def list_experiment_metrics(db: Session, experiment_id: str):
    return (
        db.query(ExperimentMetric)
        .filter(ExperimentMetric.experiment_id == experiment_id)
        .order_by(ExperimentMetric.step.asc())
        .all()
    )