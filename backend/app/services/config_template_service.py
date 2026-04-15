from app.core.database import SessionLocal
from app.repositories.config_template_repository import (
    list_config_templates,
    get_config_template_by_id,
    get_config_template_by_name,
    create_config_template,
    update_config_template,
)


def get_template_list():
    db = SessionLocal()
    try:
        rows = list_config_templates(db)
        return [
            {
                "id": row.id,
                "template_name": row.template_name,
                "template_desc": row.template_desc,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            }
            for row in rows
        ]
    finally:
        db.close()


def get_template_detail(template_id: int):
    db = SessionLocal()
    try:
        row = get_config_template_by_id(db, template_id)
        if not row:
            return {
                "message": "template not found",
                "data": None,
            }

        return {
            "message": "success",
            "data": {
                "id": row.id,
                "template_name": row.template_name,
                "template_desc": row.template_desc,
                "config_json": row.config_json,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            },
        }
    finally:
        db.close()


def save_template(payload: dict):
    db = SessionLocal()
    try:
        template_name = (payload.get("template_name") or "").strip()
        template_desc = (payload.get("template_desc") or "").strip()
        config_json = payload.get("config_json")

        if not template_name:
            return {"message": "template_name is required"}

        if not isinstance(config_json, dict):
            return {"message": "config_json must be an object"}

        existed = get_config_template_by_name(db, template_name)
        if existed:
            row = update_config_template(
                db=db,
                obj=existed,
                template_desc=template_desc,
                config_json=config_json,
            )
            return {
                "message": "template updated",
                "data": {
                    "id": row.id,
                    "template_name": row.template_name,
                    "template_desc": row.template_desc,
                },
            }

        row = create_config_template(
            db=db,
            template_name=template_name,
            template_desc=template_desc,
            config_json=config_json,
        )
        return {
            "message": "template created",
            "data": {
                "id": row.id,
                "template_name": row.template_name,
                "template_desc": row.template_desc,
            },
        }
    finally:
        db.close()