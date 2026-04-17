import json
from pathlib import Path

from app.core.config import settings
from app.core.database import SessionLocal
from app.repositories.experiment_repository import (
    list_experiments,
    get_experiment_by_experiment_id,
)
from app.repositories.experiment_metric_repository import list_experiment_metrics
from app.repositories.report_repository import list_reports_by_experiment
from app.services.result_service import build_result_payload


def get_experiment_list():
    """
    获取实验列表
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


def load_output_payload(experiment_id: str):
    """
    从 outputs 目录读取某次实验的结果 JSON
    """
    project_root = Path(__file__).resolve().parents[2]
    output_file = project_root / settings.OUTPUT_DIR / f"{experiment_id}.json"

    if not output_file.exists():
        return None

    with open(output_file, "r", encoding="utf-8") as file:
        payload = json.load(file)

    payload.setdefault("message", "simulation completed")
    return payload


def _metric_to_dict(metric):
    """
    将 experiment_metrics 表中的 ORM 对象转换为字典
    """
    return {
        "step": metric.step,
        "student_count": metric.student_count,
        "school_count": metric.school_count,
        "employer_count": metric.employer_count,
        "employment_rate": metric.employment_rate,
        "matching_rate": metric.matching_rate,
        "cross_major_rate": metric.cross_major_rate,
        "avg_salary": metric.avg_salary,
        "avg_satisfaction": metric.avg_satisfaction,
        "low_satisfaction_employment_rate": getattr(metric, "low_satisfaction_employment_rate", 0.0),
        "same_region_employment_rate": getattr(metric, "same_region_employment_rate", 0.0),
        "carryover_student_count": getattr(metric, "carryover_student_count", 0),
        "new_cohort_student_count": getattr(metric, "new_cohort_student_count", 0),
        "new_cohort_employment_rate": getattr(metric, "new_cohort_employment_rate", 0.0),
        "carryover_employment_rate": getattr(metric, "carryover_employment_rate", 0.0),
        "carryover_pool_share": getattr(metric, "carryover_pool_share", 0.0),
        "avg_carryover_rounds": getattr(metric, "avg_carryover_rounds", 0.0),
        "active_job_seekers": metric.active_job_seekers,
        "round_job_count": metric.round_job_count,
        "round_filled_jobs": metric.round_filled_jobs,
        "round_vacancy_rate": metric.round_vacancy_rate,
        "round_new_employment_rate": metric.round_new_employment_rate,
        "round_application_count": getattr(metric, "round_application_count", 0),
        "round_offer_count": getattr(metric, "round_offer_count", 0),
        "round_accepted_offer_count": getattr(metric, "round_accepted_offer_count", 0),
        "round_rejected_offer_count": getattr(metric, "round_rejected_offer_count", 0),
        "avg_applications_per_job": getattr(metric, "avg_applications_per_job", 0.0),
        "avg_offers_per_student": getattr(metric, "avg_offers_per_student", 0.0),
        "mismatch_index": metric.mismatch_index,
        "herding_index": metric.herding_index,
        "avg_hire_threshold": metric.avg_hire_threshold,
        "avg_cross_major_tolerance": metric.avg_cross_major_tolerance,
        "avg_training_quality": metric.avg_training_quality,
    }


def get_experiment_detail(experiment_id: str):
    """
    获取单个实验详情

    优先级：
    1. 先查 experiments 主表
    2. 再尝试读取 outputs 目录下的结果文件
    3. 若结果文件不存在，则从 experiment_metrics 表重建结果
    4. 同时返回与该实验关联的历史报告
    """
    db = SessionLocal()
    try:
        experiment = get_experiment_by_experiment_id(db, experiment_id)
        if experiment is None:
            return {
                "experiment_id": experiment_id,
                "status": "not_found",
                "result_payload": None,
                "latest_explanation": None,
                "saved_reports": [],
            }

        reports = list_reports_by_experiment(db, experiment_id)

        latest_explanation = next(
            (
                report.report_markdown
                for report in reports
                if report.report_type == "llm_explanation" and report.report_markdown
            ),
            None,
        )

        payload = load_output_payload(experiment_id)

        # 如果本地输出文件不存在，则从数据库指标表重建结果
        if payload is None:
            metrics = list_experiment_metrics(db, experiment_id)
            payload = build_result_payload(
                req=experiment.config_snapshot_json or {},
                results=[_metric_to_dict(metric) for metric in metrics],
                experiment_id=experiment.experiment_id,
                structure_analysis={},
            )
            payload["message"] = "simulation completed"

        return {
            "experiment_id": experiment.experiment_id,
            "status": experiment.status,
            "scenario_name": experiment.scenario_name,
            "created_at": experiment.created_at,
            "result_payload": payload,
            "latest_explanation": latest_explanation,
            "saved_reports": [
                {
                    "report_id": report.report_id,
                    "title": report.title,
                    "report_type": report.report_type,
                    "status": report.status,
                    "used_llm": bool(report.used_llm),
                    "fallback_reason": report.fallback_reason,
                    "file_name": report.file_name,
                    "created_at": report.created_at,
                    "report_markdown": report.report_markdown,
                }
                for report in reports
            ],
        }
    finally:
        db.close()