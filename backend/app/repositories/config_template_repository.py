from sqlalchemy.orm import Session

from app.models.config_template import ConfigTemplate


def list_config_templates(db: Session):
    return (
        db.query(ConfigTemplate)
        .order_by(ConfigTemplate.created_at.desc())
        .all()
    )


def get_config_template_by_id(db: Session, template_id: int):
    return (
        db.query(ConfigTemplate)
        .filter(ConfigTemplate.id == template_id)
        .first()
    )


def get_config_template_by_name(db: Session, template_name: str):
    return (
        db.query(ConfigTemplate)
        .filter(ConfigTemplate.template_name == template_name)
        .first()
    )


def create_config_template(
    db: Session,
    template_name: str,
    template_desc: str | None,
    config_json: dict,
):
    obj = ConfigTemplate(
        template_name=template_name,
        template_desc=template_desc,
        config_json=config_json,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_config_template(
    db: Session,
    obj: ConfigTemplate,
    template_desc: str | None,
    config_json: dict,
):
    obj.template_desc = template_desc
    obj.config_json = config_json
    db.commit()
    db.refresh(obj)
    return obj