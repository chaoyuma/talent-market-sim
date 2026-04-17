from fastapi import APIRouter
from app.schemas.simulation import SimulationRequest
from app.services.runner import run_simulation

router = APIRouter()

# 执行仿真接口
@router.post("/run")
def run_simulation_api(req: SimulationRequest):
    result = run_simulation(req)
    return {
        "message": "simulation completed",
        **result
    }