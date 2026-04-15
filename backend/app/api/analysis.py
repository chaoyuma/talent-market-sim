from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from app.core.database import SessionLocal
from app.services.analysis_service import explain_simulation_result
from app.repositories.report_repository import create_report

router = APIRouter()


class ExplainResultRequest(BaseModel):
    experiment_id: str
    params: Dict[str, Any]
    actual_runtime: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    latest_result: Optional[Dict[str, Any]] = None
    results: List[Dict[str, Any]] = []


@router.post("/explain-result")
def explain_result(req: ExplainResultRequest):
    req_data = req.model_dump()
    explanation = explain_simulation_result(req_data)

    db = SessionLocal()
    try:
        create_report(
            db=db,
            experiment_id=req.experiment_id,
            report_type="llm_explanation",
            summary_text=explanation[:500],
            full_report_text=explanation,
        )
    finally:
        db.close()

    return {
        "experiment_id": req.experiment_id,
        "explanation": explanation,
    }