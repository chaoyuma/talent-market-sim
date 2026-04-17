# backend/app/services/report_task_service.py

from datetime import datetime
from pathlib import Path
import uuid
import threading


# 简单内存任务表
# 单机开发环境够用；后续可改成数据库表
REPORT_TASKS: dict[str, dict] = {}

# 报告输出目录
REPORT_OUTPUT_DIR = Path("outputs/reports")
REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_report_task(experiment_ids: list[str]) -> dict:
    """
    创建报告生成任务。
    """
    task_id = uuid.uuid4().hex
    now = datetime.now().isoformat()

    task = {
        "task_id": task_id,
        "status": "pending",   # pending / running / finished / failed
        "experiment_ids": experiment_ids,
        "title": "",
        "report_markdown": "",
        "download_filename": "",
        "download_path": "",
        "used_llm": False,
        "fallback_reason": "",
        "error": "",
        "created_at": now,
        "updated_at": now,
    }
    REPORT_TASKS[task_id] = task
    return task


def get_report_task(task_id: str) -> dict | None:
    """
    查询任务状态。
    """
    return REPORT_TASKS.get(task_id)


def update_report_task(task_id: str, **kwargs):
    """
    更新任务状态。
    """
    task = REPORT_TASKS.get(task_id)
    if not task:
        return

    task.update(kwargs)
    task["updated_at"] = datetime.now().isoformat()


def run_report_task_in_thread(task_id: str, target_func, *args, **kwargs):
    """
    后台线程执行任务。
    """
    thread = threading.Thread(
        target=target_func,
        args=(task_id, *args),
        kwargs=kwargs,
        daemon=True,
    )
    thread.start()
    return thread