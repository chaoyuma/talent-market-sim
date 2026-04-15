from app.core.database import SessionLocal
from app.repositories.experiment_repository import (
    list_experiments,
    get_experiment_by_experiment_id,
)
from app.repositories.experiment_metric_repository import list_experiment_metrics


def get_experiment_list():
    """
    获取实验列表。
    """
    db = SessionLocal()
    try:
        experiments = list_experiments(db)
        return [
            {
                "experiment_id": e.experiment_id,
                "scenario_name": e.scenario_name,
                "status": e.status,
                "created_at": e.created_at,
            }
            for e in experiments
        ]
    finally:
        db.close()


def get_experiment_detail(experiment_id: str):
    """
    获取单次实验详情，包括主记录和逐轮指标。
    """
    db = SessionLocal()
    try:
        experiment = get_experiment_by_experiment_id(db, experiment_id)
        if experiment is None:
            return {
                "experiment_id": experiment_id,
                "status": "not_found",
                "scenario_name": None,
                "config_snapshot_json": None,
                "metrics": [],
            }

        metrics = list_experiment_metrics(db, experiment_id)

        return {
            "experiment_id": experiment.experiment_id,
            "status": experiment.status,
            "scenario_name": experiment.scenario_name,
            "config_snapshot_json": experiment.config_snapshot_json,
            "metrics": [
                {
                    "step": m.step,

                    # 实际参与规模
                    "student_count": m.student_count,
                    "school_count": m.school_count,
                    "employer_count": m.employer_count,

                    # 累计结果指标
                    "employment_rate": m.employment_rate,
                    "matching_rate": m.matching_rate,
                    "cross_major_rate": m.cross_major_rate,
                    "avg_salary": m.avg_salary,
                    "avg_satisfaction": m.avg_satisfaction,

                    # 本轮流量指标
                    "active_job_seekers": m.active_job_seekers,
                    "round_job_count": m.round_job_count,
                    "round_filled_jobs": m.round_filled_jobs,
                    "round_vacancy_rate": m.round_vacancy_rate,
                    "round_new_employment_rate": m.round_new_employment_rate,

                    # 结构与反馈指标
                    "mismatch_index": m.mismatch_index,
                    "herding_index": m.herding_index,
                    "avg_hire_threshold": m.avg_hire_threshold,
                    "avg_cross_major_tolerance": m.avg_cross_major_tolerance,
                    "avg_training_quality": m.avg_training_quality,
                }
                for m in metrics
            ],
        }
    finally:
        db.close()