# backend/app/sim/model_structure.py

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

    这里将多所学校在同一专业上的调整幅度做平均：
    - 正值：整体扩招
    - 负值：整体缩招
    - 0：基本不调整
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
    }