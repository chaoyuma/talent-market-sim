# backend/app/sim/model_metrics.py

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

        stats[major] = {
            "student_count": len(major_students),
            "employment_rate": (
                len(employed_major_students) / len(major_students)
                if major_students else 0.0
            ),
        }

    model.last_round_major_stats = stats


def collect_metrics(model, step_idx: int):
    """
    收集单轮仿真指标。

    指标分为三类：
    1. 累计结果指标
    2. 本轮流量指标
    3. 结构与反馈指标
    """
    total_students = len(model.students)

    # 已就业学生（累计）
    employed_students = [s for s in model.students if s.employed]

    # 本轮新就业学生（流量）
    newly_employed_students = [
        s for s in model.students if getattr(s, "just_matched_this_round", False)
    ]

    # 当前仍在求职的学生
    active_job_seekers = [s for s in model.students if not s.employed]

    # 当前轮企业发布的全部岗位
    all_jobs = [job for e in model.employers for job in e.open_jobs]
    round_job_count = len(all_jobs)
    round_filled_jobs = sum(1 for j in all_jobs if j["filled"])

    # 本轮岗位空缺率
    round_vacancy_rate = (
        (round_job_count - round_filled_jobs) / round_job_count
        if round_job_count > 0 else 0.0
    )

    # 累计就业率
    employment_rate = len(employed_students) / total_students if total_students else 0.0

    # 累计对口率
    matching_count = sum(1 for s in employed_students if s.matched_job_major)
    matching_rate = matching_count / len(employed_students) if employed_students else 0.0

    # 累计跨专业率
    cross_major_rate = (
        sum(1 for s in employed_students if not s.matched_job_major) / len(employed_students)
        if employed_students else 0.0
    )

    # 累计平均薪资
    avg_salary = (
        sum(s.current_offer["salary"] for s in employed_students if s.current_offer) / len(employed_students)
        if employed_students else 0.0
    )

    # 累计平均满意度
    avg_satisfaction = (
        sum(getattr(s, "satisfaction", 0.0) for s in employed_students) / len(employed_students)
        if employed_students else 0.0
    )

    # 低满意就业率
    low_satisfaction_employment_rate = (
        sum(
            1 for s in employed_students
            if getattr(s, "satisfaction", 0.0) < model.satisfaction_threshold
        ) / len(employed_students)
        if employed_students else 0.0
    )

    # 本轮新增就业率
    round_new_employment_rate = (
        len(newly_employed_students) / total_students
        if total_students else 0.0
    )

    # 结构性指标
    mismatch_index = calculate_mismatch_index(model)
    herding_index = calculate_herding_index(model)

    # 企业反馈参数均值
    avg_hire_threshold = (
        sum(e.profile.get("hire_threshold", 0.55) for e in model.employers) / len(model.employers)
        if model.employers else 0.0
    )

    avg_cross_major_tolerance = (
        sum(e.profile.get("cross_major_tolerance", 0.6) for e in model.employers) / len(model.employers)
        if model.employers else 0.0
    )

    # 学校培养质量均值
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

        # 实际参与规模
        "student_count": len(model.students),
        "school_count": len(model.schools),
        "employer_count": len(model.employers),

        # 累计结果指标
        "employment_rate": employment_rate,
        "matching_rate": matching_rate,
        "cross_major_rate": cross_major_rate,
        "avg_salary": avg_salary,
        "avg_satisfaction": avg_satisfaction,
        "low_satisfaction_employment_rate": low_satisfaction_employment_rate,

        # 本轮流量指标
        "active_job_seekers": len(active_job_seekers),
        "round_job_count": round_job_count,
        "round_filled_jobs": round_filled_jobs,
        "round_vacancy_rate": round_vacancy_rate,
        "round_new_employment_rate": round_new_employment_rate,

        # 结构与反馈指标
        "mismatch_index": mismatch_index,
        "herding_index": herding_index,
        "avg_hire_threshold": avg_hire_threshold,
        "avg_cross_major_tolerance": avg_cross_major_tolerance,
        "avg_training_quality": avg_training_quality,
    }