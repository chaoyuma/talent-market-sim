from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class ExperimentMetric(Base):
    __tablename__ = "experiment_metrics"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String(64), nullable=False, index=True)

    step = Column(Integer, nullable=False)

    student_count = Column(Integer, nullable=False, default=0)
    school_count = Column(Integer, nullable=False, default=0)
    employer_count = Column(Integer, nullable=False, default=0)

    employment_rate = Column(Float, nullable=False, default=0.0)
    matching_rate = Column(Float, nullable=False, default=0.0)
    cross_major_rate = Column(Float, nullable=False, default=0.0)
    avg_salary = Column(Float, nullable=False, default=0.0)
    avg_satisfaction = Column(Float, nullable=False, default=0.0)
    low_satisfaction_employment_rate = Column(Float, nullable=False, default=0.0)
    same_region_employment_rate = Column(Float, nullable=False, default=0.0)
    carryover_student_count = Column(Integer, nullable=False, default=0)
    new_cohort_student_count = Column(Integer, nullable=False, default=0)
    new_cohort_employment_rate = Column(Float, nullable=False, default=0.0)
    carryover_employment_rate = Column(Float, nullable=False, default=0.0)
    carryover_pool_share = Column(Float, nullable=False, default=0.0)
    avg_carryover_rounds = Column(Float, nullable=False, default=0.0)

    active_job_seekers = Column(Integer, nullable=False, default=0)
    round_job_count = Column(Integer, nullable=False, default=0)
    round_filled_jobs = Column(Integer, nullable=False, default=0)
    round_vacancy_rate = Column(Float, nullable=False, default=0.0)
    round_new_employment_rate = Column(Float, nullable=False, default=0.0)
    round_application_count = Column(Integer, nullable=False, default=0)
    round_offer_count = Column(Integer, nullable=False, default=0)
    round_accepted_offer_count = Column(Integer, nullable=False, default=0)
    round_rejected_offer_count = Column(Integer, nullable=False, default=0)
    avg_applications_per_job = Column(Float, nullable=False, default=0.0)
    avg_offers_per_student = Column(Float, nullable=False, default=0.0)

    mismatch_index = Column(Float, nullable=False, default=0.0)
    herding_index = Column(Float, nullable=False, default=0.0)
    avg_hire_threshold = Column(Float, nullable=False, default=0.0)
    avg_cross_major_tolerance = Column(Float, nullable=False, default=0.0)
    avg_training_quality = Column(Float, nullable=False, default=0.0)
    
    current_step_employment_rate = Column(Float, nullable=False, default=0.0)
    current_step_matching_rate = Column(Float, nullable=False, default=0.0)
    current_step_cross_major_rate = Column(Float, nullable=False, default=0.0)
    current_step_same_region_employment_rate = Column(Float, nullable=False, default=0.0)

    further_study_count = Column(Integer, nullable=False, default=0)
    public_exam_count = Column(Integer, nullable=False, default=0)
    flexible_employment_count = Column(Integer, nullable=False, default=0)
    destination_realization_rate = Column(Float, nullable=False, default=0.0)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
