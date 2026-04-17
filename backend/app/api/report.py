from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# 对比报告服务
from app.services.comparison_report_service import (
    generate_comparison_report,
    execute_comparison_report_task,
)
# 报告任务
from app.services.report_task_service import (
    create_report_task,
    get_report_task,
    run_report_task_in_thread,
)
from app.core.database import SessionLocal
from app.repositories.report_repository import (
    list_reports,
    get_report_by_report_id,
    delete_report_by_report_id,
)
router = APIRouter()

@router.get("/history")
def list_report_history():
    # 获取历史报告列表
    db = SessionLocal()
    try:
        rows = list_reports(db)
        return [
            {
                "report_id": row.report_id,
                "title": row.title,
                "report_type": row.report_type,
                "status": row.status,
                "used_llm": bool(row.used_llm),
                "fallback_reason": row.fallback_reason,
                "file_name": row.file_name,
                "created_at": row.created_at,
            }
            for row in rows
        ]
    finally:
        db.close()


@router.get("/history/{report_id}")
def get_report_history_detail(report_id: str):
    # 获取指定报告
    db = SessionLocal()
    try:
        row = get_report_by_report_id(db, report_id)
        if not row:
            raise HTTPException(status_code=404, detail="report not found")

        return {
            "report_id": row.report_id,
            "title": row.title,
            "report_type": row.report_type,
            "status": row.status,
            "experiment_ids": row.experiment_ids_json,
            "report_markdown": row.report_markdown,
            "used_llm": bool(row.used_llm),
            "fallback_reason": row.fallback_reason,
            "file_name": row.file_name,
            "created_at": row.created_at,
            "download_url": f"/api/report/history/{report_id}/download",
        }
    finally:
        db.close()


@router.get("/history/{report_id}/download")
def download_saved_report(report_id: str):
    # 下载报告
    db = SessionLocal()
    try:
        row = get_report_by_report_id(db, report_id)
        if not row:
            raise HTTPException(status_code=404, detail="report not found")

        if not row.file_path or not Path(row.file_path).exists():
            raise HTTPException(status_code=404, detail="report file not found")

        return FileResponse(
            path=row.file_path,
            filename=row.file_name or f"{report_id}.md",
            media_type="text/markdown",
        )
    finally:
        db.close()


@router.delete("/history/{report_id}")
def delete_saved_report(report_id: str):
    db = SessionLocal()
    try:
        row = get_report_by_report_id(db, report_id)
        if not row:
            raise HTTPException(status_code=404, detail="report not found")

        # 先删文件
        if row.file_path and Path(row.file_path).exists():
            Path(row.file_path).unlink()

        delete_report_by_report_id(db, report_id)
        return {"message": "report deleted", "report_id": report_id}
    finally:
        db.close()




class ComparisonReportRequest(BaseModel):
    experiment_ids: list[str] = Field(default_factory=list, min_length=1)


@router.get("/ping")
def report_ping():
    return {"message": "report service ready"}


@router.post("/generate-comparison")
def generate_report(req: ComparisonReportRequest):
    """
    同步接口
    """
    return generate_comparison_report(req.experiment_ids)


@router.post("/generate-comparison-async")
def generate_report_async(req: ComparisonReportRequest):
    """
    异步接口：
    """
    task = create_report_task(req.experiment_ids)

    run_report_task_in_thread(
        task["task_id"],
        execute_comparison_report_task,
        req.experiment_ids,
    )

    return {
        "task_id": task["task_id"],
        "status": task["status"],
        "message": "report task created",
    }


@router.get("/tasks/{task_id}")
def get_report_task_status(task_id: str):
    """
    查询报告任务状态。
    """
    task = get_report_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="report task not found")

    return {
        "task_id": task["task_id"],
        "status": task["status"],
        "title": task.get("title", ""),
        "used_llm": task.get("used_llm", False),
        "fallback_reason": task.get("fallback_reason", ""),
        "error": task.get("error", ""),
        "download_filename": task.get("download_filename", ""),
        "download_url": f"/api/report/download/{task_id}" if task["status"] == "finished" else "",
    }


@router.get("/download/{task_id}")
def download_report_file(task_id: str):
    """
    下载已生成的报告文件。
    """
    task = get_report_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="report task not found")

    if task["status"] != "finished":
        raise HTTPException(status_code=400, detail="report is not ready")

    file_path = task.get("download_path", "")
    if not file_path or not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="report file not found")

    return FileResponse(
        path=file_path,
        filename=task.get("download_filename") or f"{task_id}.md",
        media_type="text/markdown",
    )