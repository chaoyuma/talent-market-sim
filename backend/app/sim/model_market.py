# backend/app/sim/model_market.py

from collections import Counter, defaultdict


def update_major_market_heat(model):
    """
    根据本轮岗位需求结构与招聘压力，更新专业市场热度。

    作用：
    1. 把需求侧变化转成可感知的市场信号
    2. 供下一轮学生专业选择使用
    3. 供学校反馈调整时参考

    当前最小实现使用 3 类信号：
    - 岗位占比 job_share
    - 招聘缺口 vacancy_pressure
    - 薪资信号 salary_signal

    最终采用平滑更新，避免热度剧烈跳动。
    """
    major_job_counter = Counter()
    major_salary_sum = defaultdict(float)
    major_salary_count = Counter()
    major_filled_counter = Counter()

    # 统计当前轮岗位结构
    for employer in model.employers:
        for job in employer.open_jobs:
            major = job.get("major")
            if not major:
                continue

            major_job_counter[major] += 1

            salary = job.get("salary")
            if salary is not None:
                major_salary_sum[major] += float(salary)
                major_salary_count[major] += 1

            # 如果岗位对象里有 filled 状态，可用于更精确统计
            if job.get("filled", False):
                major_filled_counter[major] += 1

    total_jobs = sum(major_job_counter.values())
    if total_jobs <= 0:
        return

    # 当前轮全市场平均薪资
    all_salary_sum = sum(major_salary_sum.values())
    all_salary_count = sum(major_salary_count.values())
    market_avg_salary = all_salary_sum / all_salary_count if all_salary_count > 0 else 1.0

    new_market_heat = {}

    for major in model.majors:
        old_heat = float(model.major_market_heat.get(major, 1.0))

        # 1. 岗位需求占比
        job_count = major_job_counter.get(major, 0)
        job_share = job_count / total_jobs if total_jobs else 0.0

        # 2. 招聘缺口压力
        # 若 filled 信息不可用，则退化为岗位占比信号
        filled_count = major_filled_counter.get(major, 0)
        if job_count > 0 and filled_count > 0:
            vacancy_pressure = max(0.0, (job_count - filled_count) / job_count)
        else:
            vacancy_pressure = job_share

        # 3. 薪资信号
        if major_salary_count.get(major, 0) > 0 and market_avg_salary > 0:
            avg_major_salary = major_salary_sum[major] / major_salary_count[major]
            salary_signal = avg_major_salary / market_avg_salary
        else:
            salary_signal = 1.0

        # 归一到较稳范围
        salary_signal = max(0.5, min(1.5, salary_signal))

        # 平滑更新
        # old_heat 保留惯性，避免热度剧烈波动
        new_heat = (
            0.50 * old_heat
            + 0.25 * job_share * 3.0
            + 0.15 * vacancy_pressure * 2.0
            + 0.10 * salary_signal
        )

        new_market_heat[major] = max(0.3, min(1.5, new_heat))

    model.major_market_heat = new_market_heat