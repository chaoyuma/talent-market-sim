# backend/app/sim/model_init.py

import random

from app.services.data_manage_service import load_simulation_data
from app.sim.agents.student_agent import StudentAgent
from app.sim.agents.school_agent import SchoolAgent
from app.sim.agents.employer_agent import EmployerAgent
from app.sim.profiles import (
    STUDENT_TYPE_PROFILES,
    SCHOOL_TYPE_PROFILES,
    EMPLOYER_TYPE_PROFILES,
)


def sample_entities(items, target_count, random_seed=42):
    """
    对数据库读取到的主体数据进行抽样。

    作用：
    - 在 database 模式下，让 base_config 里的数量参数真正生效
    - 如果数据库记录数大于目标数量，则随机抽样
    - 如果数据库记录数小于等于目标数量，则直接全部使用
    """
    if not items:
        return []

    if target_count is None or target_count <= 0:
        return items

    if len(items) <= target_count:
        return items

    rng = random.Random(random_seed)
    return rng.sample(items, target_count)


def calculate_school_training_quality_avg(model):
    """
    计算学校平均培养质量。

    作用：
    - 为学生学习阶段能力增长提供统一质量基准
    """
    if not model.schools:
        return model.school_config.get("training_quality", 0.7)

    qualities = []
    for school in model.schools:
        q = school.profile.get(
            "training_quality",
            model.school_config.get("training_quality", 0.7),
        )
        qualities.append(float(q))

    return sum(qualities) / len(qualities) if qualities else 0.7

def build_major_capacity_weights(model):
    """
    根据当前学校专业容量，构建各专业的供给权重。

    返回：
    {
        "CS": 0.25,
        "Finance": 0.18,
        ...
    }
    """
    if not model.majors:
        return {}

    major_capacity_sum = {major: 0.0 for major in model.majors}

    for school in model.schools:
        major_capacity = getattr(school, "major_capacity", {}) or {}
        for major in model.majors:
            major_capacity_sum[major] += float(major_capacity.get(major, 0.0))

    total_capacity = sum(major_capacity_sum.values())
    if total_capacity <= 0:
        # 若学校容量未配置，则均匀分布
        return {major: 1.0 / len(model.majors) for major in model.majors}

    return {
        major: major_capacity_sum[major] / total_capacity
        for major in model.majors
    }


def weighted_choice(weight_dict, rng):
    """
    按权重随机选择一个 key。
    """
    items = list(weight_dict.items())
    total = sum(max(v, 0.0) for _, v in items)

    if total <= 0:
        return rng.choice([k for k, _ in items])

    r = rng.random() * total
    cum = 0.0
    for key, value in items:
        cum += max(value, 0.0)
        if r <= cum:
            return key

    return items[-1][0]


def assign_major_for_new_student(model, student_interest, student_ability, rng):
    """
    为新一届学生分配专业。

    影响因素：
    1. 学生兴趣
    2. 市场热度
    3. 学校容量（供给侧）
    4. 政策支持
    """
    majors = model.majors
    if not majors:
        return "CS"

    capacity_weights = build_major_capacity_weights(model)
    policy_support = float(model.scenario_config.get("policy_support", 0.5))
    info_transparency = float(model.student_config.get("information_transparency", 0.8))
    market_signal_weight = float(model.student_config.get("market_signal_weight", 0.1))
    interest_weight = float(model.student_config.get("interest_weight", 0.3))

    scores = {}

    for major in majors:
        # 兴趣匹配
        interest_score = 1.0 if major == student_interest else 0.4

        # 市场热度
        true_market_heat = float(model.major_market_heat.get(major, 1.0))
        noisy_signal = true_market_heat * rng.uniform(0.7, 1.3)
        perceived_market_heat = (
            info_transparency * true_market_heat
            + (1 - info_transparency) * noisy_signal
        )

        # 学校供给能力
        capacity_score = float(capacity_weights.get(major, 0.0))

        # 能力适配：这里先做一个弱化处理，避免过强绑定
        ability_score = 0.6 + 0.4 * float(student_ability)

        # 政策支持：当前先做统一小加成，后面可扩展成专业定向支持
        policy_bonus = 0.1 * policy_support

        total_score = (
            interest_weight * interest_score
            + market_signal_weight * perceived_market_heat
            + 0.35 * capacity_score
            + 0.15 * ability_score
            + policy_bonus
        )

        scores[major] = max(total_score, 0.0001)

    return weighted_choice(scores, rng)


def create_static_agents(model):
    """
    创建跨轮保留的静态主体。

    当前保留的静态主体包括：
    1. 专业基础信息
    2. 学校主体
    3. 企业主体

    注意：
    - 学生主体不在此处创建
    - 学生改为在每个 step 开始时，按“新一届 cohort”动态生成
    """
    # 读取数据库数据，并按当前仿真规模抽样
    model.db_data = load_simulation_data(
        num_students=model.num_students,
        num_schools=model.num_schools,
        num_employers=model.num_employers,
        random_seed=model.base_config["random_seed"],
    )

    # -------------------------
    # 1. 专业数据
    # -------------------------
    db_majors = model.db_data["majors"]
    if db_majors:
        model.majors = [m.major_name for m in db_majors]

        model.major_market_heat = {
            m.major_name: float(getattr(m, "heat_init", 1.0) or 1.0)
            for m in db_majors
        }

        model.major_salary_expectation = {
            m.major_name: float(getattr(m, "salary_expectation", 0.7) or 0.7)
            for m in db_majors
        }

        model.major_code_to_name = {
            m.major_code: m.major_name for m in db_majors
        }
        model.major_name_to_code = {
            m.major_name: m.major_code for m in db_majors
        }
    else:
        model.major_code_to_name = {}
        model.major_name_to_code = {}

    # -------------------------
    # 2. 学校主体（跨轮保留）
    # -------------------------
    db_schools = model.db_data["schools"]

    for s in db_schools:
        school_type = s.school_type

        school_profile = SCHOOL_TYPE_PROFILES.get(
            school_type,
            random.choice(list(SCHOOL_TYPE_PROFILES.values()))
        )

        # 将当前 school_config 注入学校画像
        school_profile = {
            **school_profile,
            "training_quality": model.school_config.get(
                "training_quality",
                school_profile.get("training_quality", 0.7),
            ),
        }

        school = SchoolAgent(
            unique_id=f"school_{s.id}",
            model=model,
            name=s.school_name,
            major_capacity={m: 50 for m in model.majors},
            school_type=school_type,
            profile=school_profile,
        )
        model.schools.append(school)

    # -------------------------
    # 3. 企业主体（跨轮保留）
    # -------------------------
    db_employers = model.db_data["employers"]

    for e in db_employers:
        employer_type = e.employer_type

        employer_profile = EMPLOYER_TYPE_PROFILES.get(
            employer_type,
            random.choice(list(EMPLOYER_TYPE_PROFILES.values()))
        )

        # 将 employer_config 注入企业画像
        employer_profile = {
            **employer_profile,
            "major_preference_strength": model.employer_config.get(
                "major_preference_strength",
                employer_profile.get("major_preference_strength", 0.8),
            ),
            "skill_preference_strength": model.employer_config.get(
                "skill_preference_strength",
                employer_profile.get("skill_preference_strength", 0.9),
            ),
            "salary_elasticity": model.employer_config.get(
                "salary_elasticity",
                employer_profile.get("salary_elasticity", 0.05),
            ),
            "hire_threshold": model.employer_config.get(
                "hire_threshold",
                employer_profile.get("hire_threshold", 0.55),
            ),
            "cross_major_tolerance": model.employer_config.get(
                "cross_major_tolerance",
                employer_profile.get("cross_major_tolerance", 0.6),
            ),
        }

        employer = EmployerAgent(
            unique_id=f"employer_{e.id}",
            model=model,
            industry=e.industry,
            base_salary=float(e.base_salary),
            employer_type=employer_type,
            profile=employer_profile,
        )
        model.employers.append(employer)

    # -------------------------
    # 4. 岗位模板数据
    # -------------------------
    model.job_templates = model.db_data["jobs"]

    print("DEBUG majors =", model.majors)
    print("DEBUG schools loaded =", len(model.schools))
    print("DEBUG employers loaded =", len(model.employers))


def refresh_students_for_new_cohort(model, step_idx: int):
    """
    每轮生成一届新的学生 cohort。

    设计意图：
    - 每个 step 表示 1 个年度 / 1 届毕业生
    - 学生不跨轮保留
    - 避免同一批学生在多轮中不断求职，导致就业率机械收敛到 100%

    当前最小实现：
    - 基于数据库学生样本重抽样
    - 每轮重新构建学生主体
    - unique_id 中加入 step_idx，避免跨轮重复
    """
    # 清空上一轮学生
    model.students = []

    db_students = model.db_data.get("students", [])
    if not db_students:
        print(f"DEBUG no student source data at step {step_idx}")
        return

    # 为了让不同轮次生成不同 cohort，这里给随机数加 step 偏移
    rng = random.Random(model.base_config["random_seed"] + step_idx)

    # 若样本足够，则无放回抽样；若不足，则允许重复抽样
    if len(db_students) >= model.num_students:
        cohort_students = rng.sample(db_students, model.num_students)
    else:
        cohort_students = [rng.choice(db_students) for _ in range(model.num_students)]

    for idx, s in enumerate(cohort_students):
        student_type = s.student_type

        student_profile = STUDENT_TYPE_PROFILES.get(
            student_type,
            random.choice(list(STUDENT_TYPE_PROFILES.values()))
        )

        student_interest = s.interest_major
        if not model.majors:
            student_interest = "CS"
        elif student_interest not in model.majors:
            student_interest = rng.choice(model.majors)

        assigned_major = assign_major_for_new_student(
            model=model,
            student_interest=student_interest,
            student_ability=float(s.ability),
            rng=rng,
        )

        student = StudentAgent(
            unique_id=f"student_{step_idx}_{idx}_{getattr(s, 'id', idx)}",
            model=model,
            ability=float(s.ability),
            interest=student_interest,
            expected_salary=float(s.expected_salary),
            student_type=student_type,
            profile=student_profile,
        )

        # 关键：本届学生在进入就业市场前，已经形成专业结果
        student.major = assigned_major

        model.students.append(student)

    print(f"DEBUG cohort students generated at step {step_idx} =", len(model.students))