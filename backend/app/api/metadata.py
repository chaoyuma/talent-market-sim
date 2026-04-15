from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.system_metadata_service import (
    build_metadata_index_payload,
    build_table_metadata_payload,
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def list_metadata_tables(db: Session = Depends(get_db)):
    """
    查询所有已登记元数据的表名。
    """
    return build_metadata_index_payload(db)


@router.get("/{table_name}")
def get_table_metadata(table_name: str, db: Session = Depends(get_db)):
    """
    按表名查询元数据。
    """
    payload = build_table_metadata_payload(db, table_name)

    if payload["table_info"] is None and len(payload["fields"]) == 0:
        raise HTTPException(status_code=404, detail=f"metadata for table '{table_name}' not found")

    return payload