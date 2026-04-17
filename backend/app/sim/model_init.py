# backend/app/sim/model_init.py
# 初始化与cohort生成器
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
from app.sim.market_signals import perceive_market_heat, get_social_major_score
# 省份到宏观区域的映射
# 说明：
# - 当前企业岗位 region 多为“东部 / 中部 / 西部”这类宏观区域
# - 而学生 region 多为“江苏 / 安徽 / 广东”这类省份
# - 若不做统一映射，则同区域就业率会被永久压成 0
PROVINCE_TO_MACRO_REGION = {
    # 东部
    "北京": "东部",
    "天津": "东部",
    "河北": "东部",
    "上海": "东部",
    "江苏": "东部",
    "浙江": "东部",
    "福建": "东部",
    "山东": "东部",
    "广东": "东部",
    "海南": "东部",

    # 中部
    "山西": "中部",
    "安徽": "中部",
    "江西": "中部",
    "河南": "中部",
    "湖北": "中部",
    "湖南": "中部",

    # 西部
    "内蒙古": "西部",
    "广西": "西部",
    "重庆": "西部",
    "四川": "西部",
    "贵州": "西部",
    "云南": "西部",
    "西藏": "西部",
    "陕西": "西部",
    "甘肃": "西部",
    "青海": "西部",
    "宁夏": "西部",
    "新疆": "西部",

    # 东北
    "辽宁": "东北",
    "吉林": "东北",
    "黑龙江": "东北",
}

# 已经是宏观区的值，直接保留
MACRO_REGION_SET = {"东部", "中部", "西部", "东北"}


def _safe_float(value, default=0.0):
    """
    安全转换为 float。

    作用：
    - 避免数据库字段为空或类型异常时导致仿真中断
    """
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value, low=0.0, high=1.0):
    """
    对数值做上下界裁剪。
    """
    return max(low, min(high, float(value)))


def _normalize_region(value):
    """
    统一地区字段格式。

    作用：
    - 避免因为空格、None、空字符串导致地区匹配异常
    """
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    return text


def _normalize_region_to_macro(value):
    """
    将地区字段统一到“宏观区域”口径。

    作用：
    - 学生侧可能是省份，如“江苏”“安徽”
    - 企业侧可能已经是“东部”“中部”“西部”
    - 该函数将两者统一成同一层级，便于地区匹配和统计
    """
    region = _normalize_region(value)
    if region is None:
        return None

    # 若本身就是宏观区，则直接返回
    if region in MACRO_REGION_SET:
        return region

    # 若是省份，则映射为宏观区
    return PROVINCE_TO_MACRO_REGION.get(region, region)


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


def _build_student_profile_from_db(model, student_row, student_type):
    """
    从数据库学生记录构建学生画像。

    作用：
    - 融合学生类型画像 + 数据库字段
    - 统一补齐求职决策所需属性
    """
    type_profile = STUDENT_TYPE_PROFILES.get(student_type, {})
    profile = dict(type_profile)

    original_region = getattr(student_row, "region", None)
    macro_region = _normalize_region_to_macro(original_region)

    profile.update({
        "gender": getattr(student_row, "gender", None),

        # 保留原始地区字段，便于后续诊断
        "region_raw": _normalize_region(original_region),

        # region 统一存放宏观区域，供匹配和统计使用
        "region": macro_region,

        "city_preference_name": getattr(student_row, "city_preference", None),
        "city_preference": _safe_float(
            getattr(student_row, "city_tier_preference", None),
            _safe_float(profile.get("city_preference"), 0.6),
        ),
        "city_tier_preference": _safe_float(
            getattr(student_row, "city_tier_preference", None),
            _safe_float(profile.get("city_preference"), 0.6),
        ),
        "risk_preference": _safe_float(
            getattr(student_row, "risk_preference", None),
            _safe_float(profile.get("risk_preference"), 0.5),
        ),
        "information_level": _safe_float(
            getattr(student_row, "information_level", None),
            _safe_float(profile.get("information_transparency"), 0.8),
        ),
        "career_growth_preference": _safe_float(
            getattr(student_row, "career_growth_preference", None),
            _safe_float(profile.get("career_growth_preference"), 0.6),
        ),
        "learning_effort": _safe_float(
            getattr(student_row, "learning_effort", None),
            _safe_float(profile.get("learning_effort"), 0.7),
        ),
    })

    # 若画像中未配置保留效用阈值，则继承全局配置
    if "reservation_utility" not in profile:
        profile["reservation_utility"] = model.student_config.get("reservation_utility", 0.0)

    return profile


def _build_school_profile_from_db(model, school_row, school_type):
    """
    从数据库学校记录构建学校画像。
    """
    type_profile = SCHOOL_TYPE_PROFILES.get(school_type, {})
    profile = dict(type_profile)

    raw_quality = _safe_float(
        getattr(school_row, "training_quality", None),
        _safe_float(profile.get("training_quality"), 0.7),
    )
    quality_scale = _safe_float(model.school_config.get("training_quality"), 0.7) / 0.7

    original_region = getattr(school_row, "region", None)

    profile.update({
        "region_raw": _normalize_region(original_region),
        "region": _normalize_region_to_macro(original_region),
        "tier": getattr(school_row, "tier", None),
        "training_quality": _clamp(raw_quality * quality_scale, 0.4, 1.0),
        "reputation": _safe_float(getattr(school_row, "reputation", None), 0.7),
        "resource_support": _safe_float(
            getattr(school_row, "resource_support", None),
            _safe_float(model.school_config.get("resource_support"), 0.03),
        ),
        "capacity_base": int(getattr(school_row, "capacity_base", 0) or 0),
        "city_tier": _safe_float(getattr(school_row, "city_tier", None), 0.5),
    })

    return profile


def _build_employer_profile_from_db(model, employer_row, employer_type):
    """
    从数据库企业记录构建企业画像。
    """
    type_profile = EMPLOYER_TYPE_PROFILES.get(employer_type, {})
    profile = dict(type_profile)

    original_region = getattr(employer_row, "region", None)

    profile.update({
        "employer_name": getattr(employer_row, "employer_name", None),
        "city": getattr(employer_row, "city", None),

        # 同时保留原始地区和统一后的宏观区
        "region_raw": _normalize_region(original_region),
        "region": _normalize_region_to_macro(original_region),

        "city_tier": _safe_float(getattr(employer_row, "city_tier", None), 0.5),
        "growth_factor": _safe_float(getattr(employer_row, "growth_factor", None), 1.0),
        "stability": _safe_float(
            getattr(employer_row, "stability", None),
            _safe_float(profile.get("stability"), 0.6),
        ),

        # 企业基准岗位数：
        # 若数据库未提供，则给出更现实的默认范围，避免岗位总量长期偏低
        "base_job_count": int(
            getattr(employer_row, "base_job_count", 0)
            or profile.get("base_job_count", random.randint(6, 12))
        ),

        "threshold_relax_speed": _safe_float(
            getattr(employer_row, "threshold_relax_speed", None),
            _safe_float(model.employer_config.get("threshold_relax_speed"), 0.03),
        ),
        "tolerance_increase_speed": _safe_float(
            getattr(employer_row, "tolerance_increase_speed", None),
            _safe_float(model.employer_config.get("tolerance_increase_speed"), 0.03),
        ),
    })

    # 用全局仿真配置覆盖企业参数，确保实验可控
    for key in [
        "major_preference_strength",
        "skill_preference_strength",
        "salary_elasticity",
        "hire_threshold",
        "cross_major_tolerance",
        "threshold_relax_speed",
        "tolerance_increase_speed",
        "threshold_tighten_speed",
        "tolerance_decrease_speed",
    ]:
        if key in model.employer_config:
            profile[key] = model.employer_config[key]

    return profile


def _build_major_capacity(model, school_profile):
    """
    构建学校专业容量。
    """
    if not model.majors:
        return {}

    base_capacity = int(school_profile.get("capacity_base", 0) or 0)
    per_major = max(5, round(base_capacity / len(model.majors))) if base_capacity > 0 else 50

    return {major: per_major for major in model.majors}


def _choose_school_for_student(model, major, rng):
    """
    为学生分配学校。

    作用：
    - 当前最小实现中，按学校专业容量和声誉加权分配
    """
    if not model.schools:
        return None

    weights = {}
    for school in model.schools:
        capacity = getattr(school, "major_capacity", {}) or {}
        reputation = _safe_float(school.profile.get("reputation"), 0.7)
        weights[school] = max(1.0, _safe_float(capacity.get(major), 0.0)) * (0.5 + reputation)

    return weighted_choice(weights, rng)


def assign_major_for_new_student(model, student_interest, student_ability, rng, student_profile=None):
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
    student_profile = student_profile or {}

    market_signal_weight = float(
        student_profile.get("market_signal_weight", model.student_config.get("market_signal_weight", 0.1))
    )
    interest_weight = float(
        student_profile.get("interest_weight", model.student_config.get("interest_weight", 0.3))
    )
    salary_weight = float(
        student_profile.get("salary_weight", model.student_config.get("salary_weight", 0.2))
    )
    herd_strength = float(model.type_config.get("herd_strength", 0.0))
    information_level = student_profile.get("information_level")

    scores = {}

    for major in majors:
        # 1. 兴趣匹配
        interest_score = 1.0 if major == student_interest else 0.4

        # 2. 学生感知到的市场热度
        perceived_market_heat = perceive_market_heat(
            model=model,
            major=major,
            rng=rng,
            information_level=information_level,
            transparency=student_profile.get(
                "information_transparency",
                model.student_config.get("information_transparency", 0.8),
            ),
        )

        # 3. 学校供给能力
        capacity_score = float(capacity_weights.get(major, 0.0))

        # 4. 能力适配
        ability_score = 0.6 + 0.4 * float(student_ability)

        # 5. 政策支持和薪资信号
        policy_weight = float(getattr(model, "major_policy_support_weight", {}).get(major, 0.5))
        policy_bonus = 0.1 * policy_support * policy_weight
        salary_score = float(model.major_salary_expectation.get(major, 0.6))

        # 6. 社会影响
        social_score = get_social_major_score(model, major)

        total_score = (
            interest_weight * interest_score
            + market_signal_weight * perceived_market_heat
            + salary_weight * salary_score
            + 0.35 * capacity_score
            + 0.15 * ability_score
            + policy_bonus
            + herd_strength * social_score
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

        model.major_mobility = {
            m.major_name: float(getattr(m, "mobility", 0.5) or 0.5)
            for m in db_majors
        }

        model.major_policy_support_weight = {
            m.major_name: float(getattr(m, "policy_support_weight", 0.5) or 0.5)
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
        model.major_mobility = {}
        model.major_policy_support_weight = {}

    model.major_industry_match = {}
    for row in model.db_data.get("major_industry_mappings", []) or []:
        model.major_industry_match[(row.major_name, row.industry)] = float(row.match_score)

    # -------------------------
    # 2. 学校主体（跨轮保留）
    # -------------------------
    db_schools = model.db_data["schools"]

    for s in db_schools:
        school_type = s.school_type

        school_profile = _build_school_profile_from_db(model, s, school_type)

        school = SchoolAgent(
            unique_id=f"school_{s.id}",
            model=model,
            name=s.school_name,
            major_capacity=_build_major_capacity(model, school_profile),
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

        employer_profile = _build_employer_profile_from_db(model, e, employer_type)

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

    # print("DEBUG majors =", model.majors)
    # print("DEBUG schools loaded =", len(model.schools))
    # print("DEBUG employers loaded =", len(model.employers))


def refresh_students_for_new_cohort(model, step_idx: int):
    """
    每轮生成一届新的学生 cohort。

    设计意图：
    - 每个 step 表示 1 个年度 / 1 届毕业生
    - 学生默认按届更新
    - 若开启未就业滞留，则允许上一轮未就业学生继续进入本轮市场

    当前最小实现：
    - 基于数据库学生样本重抽样
    - 每轮重新构建学生主体
    - unique_id 中加入 step_idx，避免跨轮重复
    """
    carryover_students = []

    # -------------------------
    # 1. 处理上一轮未就业学生的滞留
    # -------------------------
    if model.type_config.get("enable_unemployed_carryover", False):
        max_carryover_steps = int(model.student_config.get("max_carryover_steps", 1))
        carryover_fraction = float(model.student_config.get("carryover_fraction", 1.0))

        previous_unemployed = [
            s for s in model.students
            if (
                not s.employed
                and not getattr(s, "exit_market", False)
                and getattr(s, "destination", "job_searching") == "job_searching"
                and getattr(s, "carryover_rounds", 0) < max_carryover_steps
            )
        ]

        if previous_unemployed and carryover_fraction > 0:
            rng = random.Random(model.base_config["random_seed"] + 10000 + step_idx)
            keep_count = min(
                len(previous_unemployed),
                max(0, round(len(previous_unemployed) * carryover_fraction)),
            )

            # 使用随机抽样而不是切片，避免总是保留前一部分学生
            carryover_students = rng.sample(previous_unemployed, keep_count)

            for student in carryover_students:
                student.prepare_for_carryover()

    # 先清空学生池，再加入本轮 cohort
    model.students = []
    model.round_carryover_student_count = len(carryover_students)

    db_students = model.db_data.get("students", [])
    if not db_students:
        #print(f"DEBUG no student source data at step {step_idx}")
        return

    # 为了让不同轮次生成不同 cohort，这里给随机数加 step 偏移
    rng = random.Random(model.base_config["random_seed"] + step_idx)

    # 若样本足够，则无放回抽样；若不足，则允许重复抽样
    if len(db_students) >= model.num_students:
        cohort_students = rng.sample(db_students, model.num_students)
    else:
        cohort_students = [rng.choice(db_students) for _ in range(model.num_students)]

    # -------------------------
    # 2. 构建本轮新学生 cohort
    # -------------------------
    for idx, s in enumerate(cohort_students):
        student_type = s.student_type

        student_profile = _build_student_profile_from_db(model, s, student_type)

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
            student_profile=student_profile,
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
        student.cohort_step = step_idx

        # 本届学生在进入就业市场前，已经形成专业结果
        student.major = assigned_major
        student.school = _choose_school_for_student(model, assigned_major, rng)
        student.school_type = getattr(student.school, "school_type", None) if student.school else None

        model.students.append(student)

    # -------------------------
    # 3. 将滞留学生拼接回本轮学生池
    # -------------------------
    model.students.extend(carryover_students)
    model.round_new_cohort_student_count = len(cohort_students)

    print(f"DEBUG cohort students generated at step {step_idx} =", len(model.students))