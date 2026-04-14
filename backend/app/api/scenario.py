from fastapi import APIRouter

router = APIRouter()


@router.get("/presets")
def list_scenario_presets():
    return {"message": "scenario presets placeholder"}