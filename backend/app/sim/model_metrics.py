# backend/app/sim/model_metrics.py
# 指标中枢
from collections import Counter


def calculate_mismatch_index(model) -> float:
    """
    计算结构错配指数。

    含义：
    - 比较学生专业供给结构 与 岗位专业需求结构 的差异
    - 值越大，说明供需结构偏差越明显

    计算方式：
    - 统计各专业学生占比
    - 统计各专业岗位占比
    - 对每个专业做绝对差求和
    """
    student_major_counter = Counter(
        [s.major for s in model.students if s.major is not None]
    )
    job_major_counter = Counter(
        [j["major"] for e in model.employers for j in e.open_jobs if j.get("major")]
    )

    total_students = sum(student_major_counter.values())
    total_jobs = sum(job_major_counter.values())

    if total_students == 0 or total_jobs == 0:
        return 0.0

    mismatch = 0.0
    for major in model.majors:
        supply_share = student_major_counter.get(major, 0) / total_students
        demand_share = job_major_counter.get(major, 0) / total_jobs
        mismatch += abs(supply_share - demand_share)

    return mismatch


def calculate_herding_index(model) -> float:
    """
    计算扎堆指数。

    含义：
    - 衡量学生是否明显集中在少数专业
    - 值越大，说明越存在“扎堆报专业”的现象

    计算方式：
    - 找出人数最多的专业占比
    - 再除以平均专业占比
    """
    student_major_counter = Counter(
        [s.major for s in model.students if s.major is not None]
    )

    if not student_major_counter or not model.students:
        return 0.0

    max_share = max(student_major_counter.values()) / len(model.students)
    avg_share = (
        sum(student_major_counter.values()) / len(student_major_counter)
    ) / len(model.students)

    if avg_share == 0:
        return 0.0

    return max_share / avg_share


def update_major_stats(model):
    """
    更新各专业的基础统计信息。

    当前输出：
    - student_count：该专业学生数
    - employment_rate：该专业学生就业率

    作用：
    - 为学校反馈调整、结构分析提供基础统计支撑
    """
    stats = {}

    for major in model.majors:
        major_students = [s for s in model.students if s.major == major]
        employed_major_students = [
            s for s in major_students if s.current_offer is not None
        ]

        avg_salary = (
            sum(s.current_offer["salary"] for s in employed_major_students if s.current_offer)
            / len(employed_major_students)
            if employed_major_students else 0.0
        )
        avg_satisfaction = (
            sum(getattr(s, "satisfaction", 0.0) for s in employed_major_students)
            / len(employed_major_students)
            if employed_major_students else 0.0
        )

        stats[major] = {
            "student_count": len(major_students),
            "employment_rate": (
                len(employed_major_students) / len(major_students)
                if major_students else 0.0
            ),
            "avg_salary": avg_salary,
            "avg_satisfaction": avg_satisfaction,
        }

    model.last_round_major_stats = stats

    total_students = sum(item["student_count"] for item in stats.values())
    model.previous_major_distribution = {
        major: (
            item["student_count"] / total_students
            if total_students else 0.0
        )
        for major, item in stats.items()
    }


def collect_metrics(model, step_idx: int):
    """
    收集单轮仿真指标。

    指标分为四类：
    1. 跨 step 累计结果指标
    2. 当前届 / 当前轮结果指标
    3. 本轮流量指标
    4. 结构与反馈指标

    说明：
    - 当前模型中，每个 step 更接近“一届学生”
    - 因此单届指标和累计指标要显式区分，避免解释混淆
    """
    total_students = len(model.students)

    # -------------------------
    # 1. 当前轮学生状态
    # -------------------------
    employed_students = [s for s in model.students if s.employed]
    newly_employed_students = [
        s for s in model.students if getattr(s, "just_matched_this_round", False)
    ]
    active_job_seekers = [s for s in model.students if not s.employed]
    # -------------------------
    # 1.1 当前轮去向分流状态
    # -------------------------
    further_study_students = [
        s for s in model.students if getattr(s, "destination", "") == "further_study"
    ]
    public_exam_students = [
        s for s in model.students if getattr(s, "destination", "") == "public_exam"
    ]
    flexible_employment_students = [
        s for s in model.students if getattr(s, "destination", "") == "flexible_employment"
    ]

    further_study_count = len(further_study_students)
    public_exam_count = len(public_exam_students)
    flexible_employment_count = len(flexible_employment_students)

    destination_realization_rate = (
        (
            len(employed_students)
            + further_study_count
            + public_exam_count
            + flexible_employment_count
        ) / total_students
        if total_students else 0.0
    )
    # -------------------------
    # 2. 当前轮岗位状态
    # -------------------------
    all_jobs = [job for e in model.employers for job in e.open_jobs]
    round_job_count = len(all_jobs)
    round_filled_jobs = sum(1 for j in all_jobs if j["filled"])

    round_vacancy_rate = (
        (round_job_count - round_filled_jobs) / round_job_count
        if round_job_count > 0 else 0.0
    )

    round_application_count = getattr(model, "round_application_count", 0)
    round_offer_count = getattr(model, "round_offer_count", 0)
    round_accepted_offer_count = getattr(model, "round_accepted_offer_count", 0)
    round_rejected_offer_count = getattr(model, "round_rejected_offer_count", 0)

    avg_applications_per_job = (
        round_application_count / round_job_count
        if round_job_count else 0.0
    )
    avg_offers_per_student = (
        round_offer_count / total_students
        if total_students else 0.0
    )

    # -------------------------
    # 3. 维护跨 step 累计指标
    # -------------------------
    for student in model.students:
        model.cumulative_seen_student_ids.add(student.unique_id)

    newly_counted_employed_students = [
        s for s in employed_students
        if s.unique_id not in model.cumulative_employed_student_ids
    ]

    for student in newly_counted_employed_students:
        model.cumulative_employed_student_ids.add(student.unique_id)

        if student.matched_job_major:
            model.cumulative_matching_count += 1
        else:
            model.cumulative_cross_major_count += 1

        if getattr(student, "satisfaction", 0.0) < model.satisfaction_threshold:
            model.cumulative_low_satisfaction_count += 1

        # 同区域统计：
        # 注意此处比较的 region 已经是统一后的宏观区域
        if (
            student.current_offer
            and student.profile.get("region")
            and student.current_offer.get("region")
            and student.profile.get("region") == student.current_offer.get("region")
        ):
            model.cumulative_same_region_count += 1

        if student.current_offer:
            model.cumulative_salary_sum += student.current_offer.get("salary", 0.0)

        model.cumulative_satisfaction_sum += getattr(student, "satisfaction", 0.0)

    cumulative_student_count = len(model.cumulative_seen_student_ids)
    cumulative_employed_count = len(model.cumulative_employed_student_ids)

    # 跨 step 累计指标
    employment_rate = (
        cumulative_employed_count / cumulative_student_count
        if cumulative_student_count else 0.0
    )
    matching_rate = (
        model.cumulative_matching_count / cumulative_employed_count
        if cumulative_employed_count else 0.0
    )
    cross_major_rate = (
        model.cumulative_cross_major_count / cumulative_employed_count
        if cumulative_employed_count else 0.0
    )
    avg_salary = (
        model.cumulative_salary_sum / cumulative_employed_count
        if cumulative_employed_count else 0.0
    )
    avg_satisfaction = (
        model.cumulative_satisfaction_sum / cumulative_employed_count
        if cumulative_employed_count else 0.0
    )
    low_satisfaction_employment_rate = (
        model.cumulative_low_satisfaction_count / cumulative_employed_count
        if cumulative_employed_count else 0.0
    )
    same_region_employment_rate = (
        model.cumulative_same_region_count / cumulative_employed_count
        if cumulative_employed_count else 0.0
    )

    # -------------------------
    # 4. 当前届 / 当前轮真实结果指标
    # -------------------------
    current_step_employment_rate = (
        len(employed_students) / total_students
        if total_students else 0.0
    )
    current_step_matching_rate = (
        sum(1 for s in employed_students if s.matched_job_major) / len(employed_students)
        if employed_students else 0.0
    )
    current_step_cross_major_rate = (
        sum(1 for s in employed_students if not s.matched_job_major) / len(employed_students)
        if employed_students else 0.0
    )
    current_step_same_region_employment_rate = (
        sum(
            1 for s in employed_students
            if s.current_offer
            and s.profile.get("region")
            and s.current_offer.get("region")
            and s.profile.get("region") == s.current_offer.get("region")
        ) / len(employed_students)
        if employed_students else 0.0
    )

    # -------------------------
    # 5. 新 cohort 与 carryover 指标
    # -------------------------
    carryover_student_count = int(getattr(model, "round_carryover_student_count", 0))
    new_cohort_student_count = int(
        getattr(model, "round_new_cohort_student_count", total_students)
    )

    new_cohort_students = [
        s for s in model.students if not getattr(s, "is_carryover", False)
    ]
    carryover_students = [
        s for s in model.students if getattr(s, "is_carryover", False)
    ]

    employed_new_cohort_students = [s for s in new_cohort_students if s.employed]
    employed_carryover_students = [s for s in carryover_students if s.employed]

    new_cohort_employment_rate = (
        len(employed_new_cohort_students) / len(new_cohort_students)
        if new_cohort_students else 0.0
    )
    carryover_employment_rate = (
        len(employed_carryover_students) / len(carryover_students)
        if carryover_students else 0.0
    )
    carryover_pool_share = (
        len(carryover_students) / total_students if total_students else 0.0
    )
    avg_carryover_rounds = (
        sum(getattr(s, "carryover_rounds", 0) for s in model.students) / total_students
        if total_students else 0.0
    )

    # 本轮新增就业率
    round_new_employment_rate = (
        len(newly_employed_students) / total_students
        if total_students else 0.0
    )

    # -------------------------
    # 6. 结构与反馈指标
    # -------------------------
    mismatch_index = calculate_mismatch_index(model)
    herding_index = calculate_herding_index(model)

    avg_hire_threshold = (
        sum(e.profile.get("hire_threshold", 0.55) for e in model.employers) / len(model.employers)
        if model.employers else 0.0
    )

    avg_cross_major_tolerance = (
        sum(e.profile.get("cross_major_tolerance", 0.6) for e in model.employers) / len(model.employers)
        if model.employers else 0.0
    )

    avg_training_quality = (
        sum(
            school.profile.get(
                "training_quality",
                model.school_config.get("training_quality", 0.7),
            )
            for school in model.schools
        ) / len(model.schools)
        if model.schools else 0.0
    )

    return {
        "step": step_idx,

        # -------------------------
        # 实际参与规模
        # -------------------------
        "student_count": len(model.students),
        "school_count": len(model.schools),
        "employer_count": len(model.employers),

        # -------------------------
        # 跨 step 累计结果指标
        # -------------------------
        "employment_rate": employment_rate,
        "matching_rate": matching_rate,
        "cross_major_rate": cross_major_rate,
        "avg_salary": avg_salary,
        "avg_satisfaction": avg_satisfaction,
        "low_satisfaction_employment_rate": low_satisfaction_employment_rate,
        "same_region_employment_rate": same_region_employment_rate,

        # -------------------------
        # 当前届 / 当前轮结果指标
        # -------------------------
        "current_step_employment_rate": current_step_employment_rate,
        "current_step_matching_rate": current_step_matching_rate,
        "current_step_cross_major_rate": current_step_cross_major_rate,
        "current_step_same_region_employment_rate": current_step_same_region_employment_rate,

        # -------------------------
        # cohort / carryover 指标
        # -------------------------
        "carryover_student_count": carryover_student_count,
        "new_cohort_student_count": new_cohort_student_count,
        "new_cohort_employment_rate": new_cohort_employment_rate,
        "carryover_employment_rate": carryover_employment_rate,
        "carryover_pool_share": carryover_pool_share,
        "avg_carryover_rounds": avg_carryover_rounds,

        # -------------------------
        # 本轮流量指标
        # -------------------------
        "active_job_seekers": len(active_job_seekers),
        "round_job_count": round_job_count,
        "round_filled_jobs": round_filled_jobs,
        "round_vacancy_rate": round_vacancy_rate,
        "round_new_employment_rate": round_new_employment_rate,
        "round_application_count": round_application_count,
        "round_offer_count": round_offer_count,
        "round_accepted_offer_count": round_accepted_offer_count,
        "round_rejected_offer_count": round_rejected_offer_count,
        "avg_applications_per_job": avg_applications_per_job,
        "avg_offers_per_student": avg_offers_per_student,

        # -------------------------
        # 结构与反馈指标
        # -------------------------
        "mismatch_index": mismatch_index,
        "herding_index": herding_index,
        "avg_hire_threshold": avg_hire_threshold,
        "avg_cross_major_tolerance": avg_cross_major_tolerance,
        "avg_training_quality": avg_training_quality,
        # -------------------------
        # 去向分流指标
        # -------------------------
        "further_study_count": further_study_count,
        "public_exam_count": public_exam_count,
        "flexible_employment_count": flexible_employment_count,
        "destination_realization_rate": destination_realization_rate,
    }