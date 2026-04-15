from sqlalchemy.orm import Session

from app.models.system_metadata import SystemMetadata


def list_all_table_names(db: Session):
    """
    查询所有已登记元数据的表名。
    """
    rows = (
        db.query(SystemMetadata.table_name)
        .distinct()
        .order_by(SystemMetadata.table_name.asc())
        .all()
    )
    return [row[0] for row in rows]


def get_metadata_by_table_name(db: Session, table_name: str):
    """
    按表名查询元数据，包含表级记录和字段级记录。
    """
    return (
        db.query(SystemMetadata)
        .filter(SystemMetadata.table_name == table_name)
        .order_by(SystemMetadata.sort_order.asc(), SystemMetadata.id.asc())
        .all()
    )


def get_table_level_metadata(db: Session, table_name: str):
    """
    查询表级说明（field_name 为空）。
    """
    return (
        db.query(SystemMetadata)
        .filter(
            SystemMetadata.table_name == table_name,
            SystemMetadata.field_name.is_(None),
        )
        .order_by(SystemMetadata.sort_order.asc(), SystemMetadata.id.asc())
        .first()
    )


def get_field_level_metadata(db: Session, table_name: str):
    """
    查询字段级说明（field_name 不为空）。
    """
    return (
        db.query(SystemMetadata)
        .filter(
            SystemMetadata.table_name == table_name,
            SystemMetadata.field_name.is_not(None),
        )
        .order_by(SystemMetadata.sort_order.asc(), SystemMetadata.id.asc())
        .all()
    )