from datetime import datetime


def build_result_payload(req: dict, results: list, experiment_id: str | None = None):
    if experiment_id is None:
        experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    final_result = results[-1] if results else {}

    summary = {
        "final_employment_rate": final_result.get("employment_rate", 0.0),
        "final_matching_rate": final_result.get("matching_rate", 0.0),
        "final_cross_major_rate": final_result.get("cross_major_rate", 0.0),
        "final_vacancy_rate": final_result.get("vacancy_rate", 0.0),
        "final_filled_jobs": final_result.get("filled_jobs", 0),
        "final_avg_salary": final_result.get("avg_salary", 0.0),
    }

    return {
        "experiment_id": experiment_id,
        "params": req,
        "results": results,
        "summary": summary,
    }