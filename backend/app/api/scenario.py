from fastapi import APIRouter

router = APIRouter()

# 获取场景列表（占位）
@router.get("/presets")
def list_scenario_presets():
    return {"message": "scenario presets placeholder"}