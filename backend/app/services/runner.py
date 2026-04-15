import json
from pathlib import Path
from datetime import datetime

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


def run_simulation(req):
    """
    执行一次完整仿真流程。

    流程包括：
    1. 创建实验主记录
    2. 构建模型并运行
    3. 写入每轮指标
    4. 更新实验状态
    5. 组织最终返回结果
    6. 备份 JSON 输出
    """
    experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    db = SessionLocal()

    # 将请求对象统一转成 dict，后续用于入库与结果返回
    req_dict = req.model_dump()

    try:
        # 1. 创建实验主记录
        create_experiment(
            db=db,
            experiment_id=experiment_id,
            config_snapshot_json=req_dict,
            scenario_name=req.scenario_name or "baseline",
            status="running",
        )

        # 2. 构建模型并运行
        model = TalentMarketModel(
            base_config=req.base_config.model_dump(),
            student_config=req.student_config.model_dump(),
            employer_config=req.employer_config.model_dump(),
            school_config=req.school_config.model_dump(),
            scenario_config=req.scenario_config.model_dump(),
            type_config=req.type_config.model_dump(),
            data_config=req.data_config.model_dump(),
            llm_config=req.llm_config.model_dump(),
        )

        steps = req.base_config.steps
        results = model.run_model(steps=steps)

        # 3. 写入每轮指标
        bulk_create_experiment_metrics(
            db=db,
            experiment_id=experiment_id,
            metrics_list=results,
        )

        # 4. 更新实验状态
        update_experiment_status(
            db=db,
            experiment_id=experiment_id,
            status="finished",
        )

        # 5. 组织返回 payload
        payload = build_result_payload(
            req=req_dict,
            results=results,
            experiment_id=experiment_id,
            structure_analysis=model.latest_structure_analysis,
        )

        # 6. 补充实际运行规模信息
        payload["actual_runtime"] = model.get_runtime_info()

        # 7. 保留 JSON 备份
        project_root = Path(__file__).resolve().parents[2]
        output_dir = project_root / settings.OUTPUT_DIR
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{experiment_id}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return payload

    except Exception:
        # 先回滚当前失败事务，否则 Session 会处于 pending rollback 状态
        db.rollback()

        update_experiment_status(
            db=db,
            experiment_id=experiment_id,
            status="failed",
        )
        raise
    finally:
        db.close()