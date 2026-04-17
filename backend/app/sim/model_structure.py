# backend/app/sim/model_structure.py
# 结构分析模块
from collections import Counter


def _get_student_major_counter(model):
    """
    统计学生专业分布计数。
    """
    return Counter([s.major for s in model.students if s.major is not None])


def _get_job_major_counter(model):
    """
    统计岗位专业分布计数。
    """
    return Counter(
        [j["major"] for e in model.employers for j in e.open_jobs if j.get("major")]
    )


def _get_job_industry_counter(model):
    """
    统计岗位行业分布计数。

    这里采用“企业行业”作为岗位所属行业。
    """
    return Counter(
        [e.industry for e in model.employers for _j in e.open_jobs if e.industry]
    )


def build_major_supply_demand_gap(model):
    """
    构建专业供需偏差表。

    输出字段：
    - major：专业
    - student_count：学生数
    - job_count：岗位数
    - student_share：学生占比
    - job_share：岗位占比
    - gap：供需差值（学生占比 - 岗位占比）
    """
    student_major_counter = _get_student_major_counter(model)
    job_major_counter = _get_job_major_counter(model)

    total_students = sum(student_major_counter.values())
    total_jobs = sum(job_major_counter.values())

    rows = []
    for major in model.majors:
        student_count = student_major_counter.get(major, 0)
        job_count = job_major_counter.get(major, 0)

        student_share = student_count / total_students if total_students else 0.0
        job_share = job_count / total_jobs if total_jobs else 0.0

        rows.append({
            "major": major,
            "student_count": student_count,
            "job_count": job_count,
            "student_share": student_share,
            "job_share": job_share,
            "gap": student_share - job_share,
        })

    return rows


def build_major_school_adjustment_bias(model):
    """
    构建学校对各专业调整偏置的输出。

    多所学校对同一专业的调整幅度取平均：
    - 正值：整体扩招
    - 负值：整体缩招
    """
    rows = []

    for major in model.majors:
        bias_values = model.major_school_adjustment_bias.get(major, [])

        if isinstance(bias_values, list) and bias_values:
            avg_bias = sum(bias_values) / len(bias_values)
        elif isinstance(bias_values, (int, float)):
            avg_bias = float(bias_values)
        else:
            avg_bias = 0.0

        rows.append({
            "major": major,
            "school_adjustment_bias": avg_bias,
        })

    return rows


def build_major_student_distribution(model):
    """
    构建学生专业分布。
    """
    student_major_counter = _get_student_major_counter(model)
    total_students = sum(student_major_counter.values())

    rows = []
    for major in model.majors:
        count = student_major_counter.get(major, 0)
        rows.append({
            "major": major,
            "count": count,
            "share": count / total_students if total_students else 0.0,
        })
    return rows


def build_major_job_distribution(model):
    """
    构建岗位专业分布。
    """
    job_major_counter = _get_job_major_counter(model)
    total_jobs = sum(job_major_counter.values())

    rows = []
    for major in model.majors:
        count = job_major_counter.get(major, 0)
        rows.append({
            "major": major,
            "count": count,
            "share": count / total_jobs if total_jobs else 0.0,
        })
    return rows


def build_industry_job_distribution(model):
    """
    构建岗位行业分布。
    """
    job_industry_counter = _get_job_industry_counter(model)
    total_jobs = sum(job_industry_counter.values())

    rows = []
    for industry, count in sorted(job_industry_counter.items(), key=lambda x: x[1], reverse=True):
        rows.append({
            "industry": industry,
            "count": count,
            "share": count / total_jobs if total_jobs else 0.0,
        })
    return rows


def build_major_market_signals(model):
    """
    构建专业层面的市场信号、薪资和空缺指标。
    """
    rows = []
    signals = getattr(model, "latest_major_market_signals", {}) or {}
    for major in model.majors:
        signal = signals.get(major, {})
        rows.append({
            "major": major,
            "market_heat": float(model.major_market_heat.get(major, 0.0)),
            "job_count": signal.get("job_count", 0),
            "filled_count": signal.get("filled_count", 0),
            "vacancy_rate": signal.get("vacancy_rate", 0.0),
            "avg_salary": signal.get("avg_salary", 0.0),
            "salary_signal": signal.get("salary_signal", 1.0),
        })
    return rows


def build_major_outcomes(model):
    """
    构建专业层面的就业结果。
    """
    rows = []
    for major in model.majors:
        stats = model.last_round_major_stats.get(major, {})
        rows.append({
            "major": major,
            "student_count": stats.get("student_count", 0),
            "employment_rate": stats.get("employment_rate", 0.0),
            "avg_salary": stats.get("avg_salary", 0.0),
            "avg_satisfaction": stats.get("avg_satisfaction", 0.0),
        })
    return rows


def build_student_type_outcomes(model):
    """
    按学生类型输出就业、薪资、满意度。
    """
    groups = {}
    for student in model.students:
        key = student.student_type or "unknown"
        groups.setdefault(key, []).append(student)

    rows = []
    for student_type, students in sorted(groups.items()):
        employed = [s for s in students if s.employed]
        rows.append({
            "student_type": student_type,
            "student_count": len(students),
            "employment_rate": len(employed) / len(students) if students else 0.0,
            "avg_salary": (
                sum(s.current_offer["salary"] for s in employed if s.current_offer) / len(employed)
                if employed else 0.0
            ),
            "avg_satisfaction": (
                sum(getattr(s, "satisfaction", 0.0) for s in employed) / len(employed)
                if employed else 0.0
            ),
        })
    return rows


def build_employer_type_metrics(model):
    """
    按企业类型输出岗位、空缺、门槛和跨专业容忍度。
    """
    groups = {}
    for employer in model.employers:
        key = employer.employer_type or "unknown"
        groups.setdefault(key, []).append(employer)

    rows = []
    for employer_type, employers in sorted(groups.items()):
        jobs = [job for e in employers for job in e.open_jobs]
        filled = [job for job in jobs if job.get("filled")]
        rows.append({
            "employer_type": employer_type,
            "employer_count": len(employers),
            "job_count": len(jobs),
            "vacancy_rate": (len(jobs) - len(filled)) / len(jobs) if jobs else 0.0,
            "avg_hire_threshold": (
                sum(e.profile.get("hire_threshold", 0.55) for e in employers) / len(employers)
                if employers else 0.0
            ),
            "avg_cross_major_tolerance": (
                sum(e.profile.get("cross_major_tolerance", 0.6) for e in employers) / len(employers)
                if employers else 0.0
            ),
        })
    return rows


def build_school_type_metrics(model):
    """
    按学校类型输出培养质量和容量。
    """
    groups = {}
    for school in model.schools:
        key = school.school_type or "unknown"
        groups.setdefault(key, []).append(school)

    rows = []
    for school_type, schools in sorted(groups.items()):
        rows.append({
            "school_type": school_type,
            "school_count": len(schools),
            "avg_training_quality": (
                sum(s.profile.get("training_quality", 0.7) for s in schools) / len(schools)
                if schools else 0.0
            ),
            "total_capacity": sum(sum((s.major_capacity or {}).values()) for s in schools),
        })
    return rows


def build_regional_flow_metrics(model):
    """
    输出区域流动指标。

    说明：
    - region 使用统一后的宏观区域口径
    - 同时保留学生原始地区分布，便于后续检查省份样本结构
    """
    # -------------------------
    # 1. 宏观区域统计
    # -------------------------
    student_region_counter = Counter(
        [s.profile.get("region") or "unknown" for s in model.students]
    )
    job_region_counter = Counter(
        [j.get("region") or "unknown" for e in model.employers for j in e.open_jobs]
    )
    employed_region_counter = Counter(
        [
            (s.current_offer.get("region") or "unknown")
            for s in model.students
            if s.employed and s.current_offer
        ]
    )

    same_region_count = sum(
        1 for s in model.students
        if s.employed
        and s.current_offer
        and s.profile.get("region")
        and s.current_offer.get("region")
        and s.profile.get("region") == s.current_offer.get("region")
    )
    employed_count = sum(1 for s in model.students if s.employed)

    macro_regions = sorted(
        set(student_region_counter) | set(job_region_counter) | set(employed_region_counter)
    )

    macro_rows = []
    for region in macro_regions:
        macro_rows.append({
            "region": region,
            "student_count": student_region_counter.get(region, 0),
            "job_count": job_region_counter.get(region, 0),
            "employed_job_count": employed_region_counter.get(region, 0),
            "student_job_gap": student_region_counter.get(region, 0) - job_region_counter.get(region, 0),
        })

    # -------------------------
    # 2. 学生原始地区分布
    # -------------------------
    student_region_raw_counter = Counter(
        [s.profile.get("region_raw") or "unknown" for s in model.students]
    )

    raw_rows = []
    for region, count in sorted(student_region_raw_counter.items(), key=lambda x: x[1], reverse=True):
        raw_rows.append({
            "region_raw": region,
            "student_count": count,
        })

    return {
        "rows": macro_rows,
        "student_region_raw_distribution": raw_rows,
        "same_region_employment_rate": (
            same_region_count / employed_count if employed_count else 0.0
        ),
    }


def update_structure_analysis(model):
    """
    更新模型当前轮的结构分析缓存。

    该缓存最终会挂到 payload.structure_analysis 中返回给前端。
    """
    model.latest_structure_analysis = {
        "major_supply_demand_gap": build_major_supply_demand_gap(model),
        "major_school_adjustment_bias": build_major_school_adjustment_bias(model),
        "major_student_distribution": build_major_student_distribution(model),
        "major_job_distribution": build_major_job_distribution(model),
        "industry_job_distribution": build_industry_job_distribution(model),
        "major_market_signals": build_major_market_signals(model),
        "major_outcomes": build_major_outcomes(model),
        "student_type_outcomes": build_student_type_outcomes(model),
        "employer_type_metrics": build_employer_type_metrics(model),
        "school_type_metrics": build_school_type_metrics(model),
        "regional_flow_metrics": build_regional_flow_metrics(model),
    }