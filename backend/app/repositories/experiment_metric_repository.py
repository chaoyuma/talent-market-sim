from sqlalchemy import inspect, text

from app.models.experiment_metric import ExperimentMetric


EXTRA_METRIC_COLUMNS = {
    "low_satisfaction_employment_rate": "FLOAT NOT NULL DEFAULT 0",
    "same_region_employment_rate": "FLOAT NOT NULL DEFAULT 0",
    "carryover_student_count": "INTEGER NOT NULL DEFAULT 0",
    "new_cohort_student_count": "INTEGER NOT NULL DEFAULT 0",
    "new_cohort_employment_rate": "FLOAT NOT NULL DEFAULT 0",
    "carryover_employment_rate": "FLOAT NOT NULL DEFAULT 0",
    "carryover_pool_share": "FLOAT NOT NULL DEFAULT 0",
    "avg_carryover_rounds": "FLOAT NOT NULL DEFAULT 0",
    "round_application_count": "INTEGER NOT NULL DEFAULT 0",
    "round_offer_count": "INTEGER NOT NULL DEFAULT 0",
    "round_accepted_offer_count": "INTEGER NOT NULL DEFAULT 0",
    "round_rejected_offer_count": "INTEGER NOT NULL DEFAULT 0",
    "avg_applications_per_job": "FLOAT NOT NULL DEFAULT 0",
    "avg_offers_per_student": "FLOAT NOT NULL DEFAULT 0",
}


def ensure_experiment_metric_columns(db):
    """
    Keep existing deployments compatible with newly added metric columns.
    """
    inspector = inspect(db.bind)
    if "experiment_metrics" not in inspector.get_table_names():
        return

    existing = {col["name"] for col in inspector.get_columns("experiment_metrics")}
    for column_name, ddl in EXTRA_METRIC_COLUMNS.items():
        if column_name not in existing:
            db.execute(text(f"ALTER TABLE experiment_metrics ADD COLUMN {column_name} {ddl}"))
    db.commit()


def bulk_create_experiment_metrics(db, experiment_id: str, metrics_list: list):
    """
    批量写入实验逐轮指标。
    适配当前新版 experiment_metrics 字段。
    """
    ensure_experiment_metric_columns(db)
    objs = []

    for m in metrics_list:
        obj = ExperimentMetric(
            experiment_id=experiment_id,
            step=m.get("step", 0),

            # 实际参与规模
            student_count=m.get("student_count", 0),
            school_count=m.get("school_count", 0),
            employer_count=m.get("employer_count", 0),

            # 累计结果指标
            employment_rate=m.get("employment_rate", 0.0),
            matching_rate=m.get("matching_rate", 0.0),
            cross_major_rate=m.get("cross_major_rate", 0.0),
            avg_salary=m.get("avg_salary", 0.0),
            avg_satisfaction=m.get("avg_satisfaction", 0.0),
            low_satisfaction_employment_rate=m.get("low_satisfaction_employment_rate", 0.0),
            same_region_employment_rate=m.get("same_region_employment_rate", 0.0),
            carryover_student_count=m.get("carryover_student_count", 0),
            new_cohort_student_count=m.get("new_cohort_student_count", 0),
            new_cohort_employment_rate=m.get("new_cohort_employment_rate", 0.0),
            carryover_employment_rate=m.get("carryover_employment_rate", 0.0),
            carryover_pool_share=m.get("carryover_pool_share", 0.0),
            avg_carryover_rounds=m.get("avg_carryover_rounds", 0.0),

            # 本轮流量指标
            active_job_seekers=m.get("active_job_seekers", 0),
            round_job_count=m.get("round_job_count", 0),
            round_filled_jobs=m.get("round_filled_jobs", 0),
            round_vacancy_rate=m.get("round_vacancy_rate", 0.0),
            round_new_employment_rate=m.get("round_new_employment_rate", 0.0),
            round_application_count=m.get("round_application_count", 0),
            round_offer_count=m.get("round_offer_count", 0),
            round_accepted_offer_count=m.get("round_accepted_offer_count", 0),
            round_rejected_offer_count=m.get("round_rejected_offer_count", 0),
            avg_applications_per_job=m.get("avg_applications_per_job", 0.0),
            avg_offers_per_student=m.get("avg_offers_per_student", 0.0),

            # 结构与反馈指标
            mismatch_index=m.get("mismatch_index", 0.0),
            herding_index=m.get("herding_index", 0.0),
            avg_hire_threshold=m.get("avg_hire_threshold", 0.0),
            avg_cross_major_tolerance=m.get("avg_cross_major_tolerance", 0.0),
            avg_training_quality=m.get("avg_training_quality", 0.0),
        )
        objs.append(obj)

    if objs:
        db.add_all(objs)
        db.commit()


def list_experiment_metrics(db, experiment_id: str):
    """
    查询某次实验的所有逐轮指标，按 step 升序返回。
    """
    return (
        db.query(ExperimentMetric)
        .filter(ExperimentMetric.experiment_id == experiment_id)
        .order_by(ExperimentMetric.step.asc())
        .all()
    )
