from app.models.report import Report


def create_report(
    db,
    experiment_id: str,
    report_type: str = "llm_explanation",
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