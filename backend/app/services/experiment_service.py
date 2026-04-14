from app.core.database import SessionLocal
from app.repositories.experiment_repository import list_experiments, get_experiment_by_experiment_id
from app.repositories.experiment_metric_repository import list_experiment_metrics


def get_experiment_list():
    db = SessionLocal()
    try:
        experiments = list_experiments(db)
        return [
            {
                "experiment_id": e.experiment_id,
                "scenario_name": e.scenario_name,
                "status": e.status,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "started_at": e.started_at.isoformat() if e.started_at else None,
                "finished_at": e.finished_at.isoformat() if e.finished_at else None,
            }
            for e in experiments
        ]
    finally:
        db.close()


def get_experiment_detail(experiment_id: str):
    db = SessionLocal()
    try:
        exp = get_experiment_by_experiment_id(db, experiment_id)
        if not exp:
            return {"error": "experiment not found"}

        metrics = list_experiment_metrics(db, experiment_id)

        return {
            "experiment_id": exp.experiment_id,
            "scenario_name": exp.scenario_name,
            "status": exp.status,
            "config_snapshot_json": exp.config_snapshot_json,
            "created_at": exp.created_at.isoformat() if exp.created_at else None,
            "started_at": exp.started_at.isoformat() if exp.started_at else None,
            "finished_at": exp.finished_at.isoformat() if exp.finished_at else None,
            "metrics": [
                {
                    "step": m.step,
                    "employment_rate": m.employment_rate,
                    "matching_rate": m.matching_rate,
                    "cross_major_rate": m.cross_major_rate,
                    "vacancy_rate": m.vacancy_rate,
                    "filled_jobs": m.filled_jobs,
                    "avg_salary": m.avg_salary,
                }
                for m in metrics
            ],
        }
    finally:
        db.close()