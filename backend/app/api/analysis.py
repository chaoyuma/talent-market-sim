from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import uuid

from app.core.database import SessionLocal
from app.services.analysis_service import explain_simulation_result
from app.repositories.report_repository import create_report
from app.services.parameter_tuning_service import call_llm_for_parameter_suggestions

router = APIRouter()


class ParameterSuggestionRequest(BaseModel):
    payload: dict


@router.post("/generate-parameter-suggestions")
def generate_parameter_suggestions(req: ParameterSuggestionRequest):
    """
    基于实验结果生成参数调优建议。
    """
    return call_llm_for_parameter_suggestions(req.payload)


class ExplainResultRequest(BaseModel):
    experiment_id: str
    params: Dict[str, Any]
    actual_runtime: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    latest_result: Optional[Dict[str, Any]] = None
    structure_analysis: Optional[Dict[str, Any]] = None
    results: List[Dict[str, Any]] = Field(default_factory=list)


@router.post("/explain-result")
def explain_result(req: ExplainResultRequest):
    req_data = req.model_dump()
    explanation = explain_simulation_result(req_data)

    db = SessionLocal()
    try:
        create_report(
            db=db,
            report_id=str(uuid.uuid4()),
            title=f"实验 {req.experiment_id} 结果解释报告",
            report_type="llm_explanation",
            status="completed",
            experiment_ids_json=[req.experiment_id],
            report_markdown=explanation,
            file_name="",
            file_path="",
            used_llm=True,
            fallback_reason=None,
            error_message=None,
        )
    finally:
        db.close()

    return {
        "experiment_id": req.experiment_id,
        "explanation": explanation,
    }