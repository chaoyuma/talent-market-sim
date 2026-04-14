from sqlalchemy.orm import Session
from app.models.report import Report


def create_report(
    db: Session,
    experiment_id: str,
    report_type: str = "summary",
    summary_text: str | None = None,
    full_report_text: str | None = None,
):
    obj = Report(
        experiment_id=experiment_id,
        report_type=report_type,
        summary_text=summary_text,
        full_report_text=full_report_text,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_reports(db: Session, experiment_id: str):
    return db.query(Report).filter(Report.experiment_id == experiment_id).all()