from fastapi import APIRouter
from app.services.experiment_service import (
    get_experiment_list,
    get_experiment_detail,
)

router = APIRouter()


@router.get("/list")
def experiment_list():
    return get_experiment_list()


@router.get("/{experiment_id}")
def experiment_detail(experiment_id: str):
    return get_experiment_detail(experiment_id)