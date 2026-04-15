from fastapi import APIRouter, Body

from app.services.config_template_service import (
    get_template_list,
    get_template_detail,
    save_template,
)

router = APIRouter()


@router.get("/list")
def config_template_list():
    return get_template_list()


@router.post("/save")
def config_template_save(payload: dict = Body(...)):
    return save_template(payload)


@router.get("/{template_id}")
def config_template_detail(template_id: int):
    return get_template_detail(template_id)