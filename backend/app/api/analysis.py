from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from app.services.analysis_service import explain_simulation_result

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

    return {
        "experiment_id": req.experiment_id,
        "explanation": explanation,
    }