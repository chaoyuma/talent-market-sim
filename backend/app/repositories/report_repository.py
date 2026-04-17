from sqlalchemy.orm import Session

from app.models.simulation_report import SimulationReport


def create_report(
    db: Session,
    report_id: str,
    title: str,
    report_type: str,
    status: str,
    experiment_ids_json,
    report_markdown: str,
    file_name: str,
    file_path: str,
    used_llm: bool,
    fallback_reason: str | None = None,
    error_message: str | None = None,
):
    row = SimulationReport(
        report_id=report_id,
        title=title,
        report_type=report_type,
        status=status,
        experiment_ids_json=experiment_ids_json,
        report_markdown=report_markdown,
        file_name=file_name,
        file_path=file_path,
        used_llm=used_llm,
        fallback_reason=fallback_reason,
        error_message=error_message,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_reports(db: Session):
    return (
        db.query(SimulationReport)
        .order_by(SimulationReport.created_at.desc())
        .all()
    )


def get_report_by_report_id(db: Session, report_id: str):
    return (
        db.query(SimulationReport)
        .filter(SimulationReport.report_id == report_id)
        .first()
    )


def list_reports_by_experiment(db: Session, experiment_id: str):
    """
    查询与某个实验相关的报告列表。
    """
    rows = (
        db.query(SimulationReport)
        .order_by(SimulationReport.created_at.desc())
        .all()
    )

    result = []
    for row in rows:
        experiment_ids = row.experiment_ids_json or []
        if isinstance(experiment_ids, list) and experiment_id in experiment_ids:
            result.append(row)

    return result


def delete_report_by_report_id(db: Session, report_id: str):
    row = get_report_by_report_id(db, report_id)
    if not row:
        return None
    db.delete(row)
    db.commit()
    return row