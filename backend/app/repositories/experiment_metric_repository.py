from app.models.experiment_metric import ExperimentMetric


def bulk_create_experiment_metrics(db, experiment_id: str, metrics_list: list):
    """
    批量写入实验逐轮指标。
    适配当前新版 experiment_metrics 字段。
    """
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

            # 本轮流量指标
            active_job_seekers=m.get("active_job_seekers", 0),
            round_job_count=m.get("round_job_count", 0),
            round_filled_jobs=m.get("round_filled_jobs", 0),
            round_vacancy_rate=m.get("round_vacancy_rate", 0.0),
            round_new_employment_rate=m.get("round_new_employment_rate", 0.0),

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