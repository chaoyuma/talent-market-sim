import json
import math
from pathlib import Path
from datetime import datetime
from statistics import mean, pstdev

from app.sim.model import TalentMarketModel
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.result_service import build_result_payload
from app.repositories.experiment_repository import (
    create_experiment,
    update_experiment_status,
)
from app.repositories.experiment_metric_repository import (
    bulk_create_experiment_metrics,
)


def _build_model(config: dict) -> TalentMarketModel:
    return TalentMarketModel(
        base_config=config["base_config"],
        student_config=config["student_config"],
        employer_config=config["employer_config"],
        school_config=config["school_config"],
        scenario_config=config["scenario_config"],
        type_config=config["type_config"],
        data_config=config["data_config"],
        llm_config=config["llm_config"],
    )


def _run_single_seed(config: dict, seed: int) -> dict:
    run_config = {
        **config,
        "base_config": {
            **config["base_config"],
            "random_seed": seed,
            "seed_runs": 1,
        },
    }
    model = _build_model(run_config)
    results = model.run_model(steps=run_config["base_config"]["steps"])
    return {
        "seed": seed,
        "results": results,
        "final_result": results[-1] if results else {},
        "runtime": model.get_runtime_info(),
        "structure_analysis": model.latest_structure_analysis,
    }


def _numeric_values(rows: list[dict], key: str) -> list[float]:
    return [
        row[key]
        for row in rows
        if isinstance(row.get(key), (int, float))
        and not isinstance(row.get(key), bool)
        and math.isfinite(row[key])
    ]


def _aggregate_metric_runs(seed_runs: list[dict]) -> list[dict]:
    if not seed_runs:
        return []

    max_steps = max(len(item["results"]) for item in seed_runs)
    aggregated = []

    for step_idx in range(max_steps):
        step_rows = [
            item["results"][step_idx]
            for item in seed_runs
            if step_idx < len(item["results"])
        ]
        numeric_keys = sorted({
            key
            for row in step_rows
            for key, value in row.items()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        })
        merged = {
            key: mean(values)
            for key in numeric_keys
            if (values := _numeric_values(step_rows, key))
        }
        merged["step"] = step_idx
        aggregated.append(merged)

    return aggregated


def _build_multi_seed_summary(seed_runs: list[dict]) -> dict:
    final_rows = [item["final_result"] for item in seed_runs if item["final_result"]]
    metric_keys = [
        "employment_rate",
        "new_cohort_employment_rate",
        "carryover_employment_rate",
        "matching_rate",
        "cross_major_rate",
        "avg_salary",
        "avg_satisfaction",
        "round_vacancy_rate",
        "mismatch_index",
        "herding_index",
    ]

    summary = {}
    for key in metric_keys:
        values = _numeric_values(final_rows, key)
        if not values:
            continue
        summary[key] = {
            "mean": mean(values),
            "std": pstdev(values) if len(values) > 1 else 0.0,
            "min": min(values),
            "max": max(values),
        }

    return summary


def run_simulation(req):
    """
    Run one experiment. When base_config.seed_runs > 1, the same scenario is
    repeated with consecutive random seeds and numeric step metrics are stored
    as cross-seed means.
    """
    experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    db = SessionLocal()
    req_dict = req.model_dump()

    try:
        create_experiment(
            db=db,
            experiment_id=experiment_id,
            config_snapshot_json=req_dict,
            scenario_name=req.scenario_name or "baseline",
            status="running",
        )

        seed_count = max(1, int(req_dict["base_config"].get("seed_runs", 1)))
        base_seed = int(req_dict["base_config"].get("random_seed", 42))

        if seed_count == 1:
            single_run = _run_single_seed(req_dict, base_seed)
            results = single_run["results"]
            structure_analysis = single_run["structure_analysis"]
            actual_runtime = single_run["runtime"]
            multi_seed_payload = {
                "enabled": False,
                "seed_runs": 1,
                "seeds": [base_seed],
            }
            seed_results = []
        else:
            seed_results = [
                _run_single_seed(req_dict, base_seed + idx)
                for idx in range(seed_count)
            ]
            results = _aggregate_metric_runs(seed_results)
            structure_analysis = seed_results[-1]["structure_analysis"]
            actual_runtime = dict(seed_results[-1]["runtime"])
            actual_runtime["seed_runs"] = seed_count
            actual_runtime["aggregation"] = "mean_by_step"
            multi_seed_payload = {
                "enabled": True,
                "seed_runs": seed_count,
                "seeds": [item["seed"] for item in seed_results],
                "summary": _build_multi_seed_summary(seed_results),
            }

        bulk_create_experiment_metrics(
            db=db,
            experiment_id=experiment_id,
            metrics_list=results,
        )

        update_experiment_status(
            db=db,
            experiment_id=experiment_id,
            status="finished",
        )

        payload = build_result_payload(
            req=req_dict,
            results=results,
            experiment_id=experiment_id,
            structure_analysis=structure_analysis,
        )
        payload["actual_runtime"] = actual_runtime
        payload["multi_seed"] = multi_seed_payload
        if seed_results:
            payload["seed_results"] = [
                {
                    "seed": item["seed"],
                    "results": item["results"],
                    "final_result": item["final_result"],
                }
                for item in seed_results
            ]

        project_root = Path(__file__).resolve().parents[2]
        output_dir = project_root / settings.OUTPUT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{experiment_id}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return payload

    except Exception:
        db.rollback()
        update_experiment_status(
            db=db,
            experiment_id=experiment_id,
            status="failed",
        )
        raise
    finally:
        db.close()
