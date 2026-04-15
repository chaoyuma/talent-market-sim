from datetime import datetime


def build_result_payload(
    req: dict,
    results: list,
    experiment_id: str | None = None,
    structure_analysis: dict | None = None,
):
    """
    组织仿真结果返回结构。
    summary 基于最后一轮结果生成，适配当前新版指标口径。
    """
    if experiment_id is None:
        experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    final_result = results[-1] if results else {}

    summary = {
        # 累计结果指标
        "final_employment_rate": final_result.get("employment_rate", 0.0),
        "final_matching_rate": final_result.get("matching_rate", 0.0),
        "final_cross_major_rate": final_result.get("cross_major_rate", 0.0),
        "final_avg_salary": final_result.get("avg_salary", 0.0),
        "final_avg_satisfaction": final_result.get("avg_satisfaction", 0.0),
        "final_low_satisfaction_employment_rate": final_result.get("low_satisfaction_employment_rate", 0.0),

        # 本轮流量指标（取最后一轮）
        "final_active_job_seekers": final_result.get("active_job_seekers", 0),
        "final_round_job_count": final_result.get("round_job_count", 0),
        "final_round_filled_jobs": final_result.get("round_filled_jobs", 0),
        "final_round_vacancy_rate": final_result.get("round_vacancy_rate", 0.0),
        "final_round_new_employment_rate": final_result.get("round_new_employment_rate", 0.0),

        # 结构与反馈指标
        "final_mismatch_index": final_result.get("mismatch_index", 0.0),
        "final_herding_index": final_result.get("herding_index", 0.0),
        "final_avg_hire_threshold": final_result.get("avg_hire_threshold", 0.0),
        "final_avg_cross_major_tolerance": final_result.get("avg_cross_major_tolerance", 0.0),
        "final_avg_training_quality": final_result.get("avg_training_quality", 0.0),
    }

    return {
        "experiment_id": experiment_id,
        "scenario_name": req.get("scenario_name", "baseline"),
        "params": req,
        "results": results,
        "summary": summary,
        "structure_analysis": structure_analysis or {
            "major_supply_demand_gap": [],
            "major_school_adjustment_bias": [],
            "major_student_distribution": [],
            "major_job_distribution": [],
            "industry_job_distribution": [],
        },
    }