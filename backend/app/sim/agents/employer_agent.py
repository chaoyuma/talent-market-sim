from mesa import Agent
import random


class EmployerAgent(Agent):
    """
    企业主体：
    1. 发布岗位
    2. 接收学生申请
    3. 对候选人评分并发放 offer
    4. 根据空缺率动态调整招聘策略
    5. 岗位分层机制
       - strict_major：严格专业岗
       - adjacent_major：相近专业岗
       - generalist：通用岗
       - trainable：培训岗
    """

    def __init__(self, unique_id, model, industry, base_salary, employer_type, profile):
        super().__init__(model)
        self.unique_id = unique_id
        self.industry = industry
        self.base_salary = base_salary
        self.employer_type = employer_type
        self.profile = profile or {}

        self.open_jobs = []
        self.applications = []
        self.last_application_count = 0
        self.last_job_count = 0

    def _get_industry_major_preferences(self):
        """
        获取当前行业偏好专业列表
        优先使用模型中预设的 major_industry_match 映射关系。
        """
        mapped = [
            (major, score)
            for (major, industry), score in getattr(self.model, "major_industry_match", {}).items()
            if industry == self.industry and major in self.model.majors
        ]
        if mapped:
            weighted = []
            for major, score in mapped:
                weighted.extend([major] * max(1, int(round(float(score) * 10))))
            return weighted

        industry_map = {
            "Internet": ["计算机与人工智能", "财经与金融"],
            "AI": ["计算机与人工智能", "电子信息与自动化"],
            "Finance": ["财经与金融", "管理与工商", "计算机与人工智能"],
            "Manufacturing": ["智能制造与机械工程", "材料与化工"],
            "Education": ["现代服务与公共管理", "传媒与内容传播"],
            "Healthcare": ["医学与护理", "现代服务与公共管理"],
            "Construction": ["土木与交通工程", "智能制造与机械工程"],
            "先进制造": ["智能制造与机械工程", "材料与化工"],
            "现代服务": ["现代服务与公共管理", "管理与工商"],
            "建筑工程": ["土木与交通工程", "智能制造与机械工程"],
            "商务服务": ["管理与工商", "财经与金融", "现代服务与公共管理"],
            "智能硬件": ["电子信息与自动化", "计算机与人工智能"],
            "房地产链条": ["土木与交通工程", "管理与工商"],
            "物流供应链": ["管理与工商", "现代服务与公共管理"],
            "人工智能": ["计算机与人工智能", "电子信息与自动化"],
            "医疗健康": ["医学与护理", "现代服务与公共管理"],
            "内容传媒": ["传媒与内容传播", "现代服务与公共管理"],
        }
        return [m for m in industry_map.get(self.industry, self.model.majors) if m in self.model.majors]

    def _choose_template(self, preferred_majors):
        """
        优先从岗位模板中挑选更接近当前行业和专业偏好的岗位。
        """
        templates = getattr(self.model, "job_templates", []) or []
        if not templates:
            return None

        preferred_set = set(preferred_majors or [])
        industry_matches = [j for j in templates if getattr(j, "industry", None) == self.industry]

        if industry_matches and random.random() < 0.75:
            return random.choice(industry_matches)

        major_matches = []
        for job in templates:
            major = self.model.major_code_to_name.get(getattr(job, "major_code", None))
            if major in preferred_set:
                major_matches.append(job)

        if major_matches:
            return random.choice(major_matches)

        return random.choice(templates)

    def _is_general_job(self, template):
        """
        判断是否为通用岗位。

        作用：
        - 通用岗位对专业要求更弱
        - 有助于提高跨专业流动，降低“异常高对口率”
        """
        if template is None:
            return False

        major_code = getattr(template, "major_code", None)
        if major_code in [None, "", "GENERAL", "ALL"]:
            return True

        template_name = str(getattr(template, "job_name", "") or "").lower()
        general_keywords = [
            "operation",
            "operations",
            "sales",
            "admin",
            "service",
            "assistant",
            "support",
            "管培",
            "运营",
            "销售",
            "行政",
            "助理",
            "服务",
        ]

        return any(keyword in template_name for keyword in general_keywords)

    def _get_job_layer_ratios(self):
        """
        获取岗位分层比例。
        默认值偏“吸纳型”
            - strict_major：20%
            - adjacent_major：25%
            - generalist：35%
            - trainable：20%
    
            企业可通过 profile 调整分层比例，以适应不同的招聘策略和市场环境。
            例如，在人才紧缺时增加 generalist 和 trainable 岗位的比例。
            反之，在人才充裕时增加 strict_major 岗位的比例以提升招聘质量。

        """
        return {
            "strict_major": float(self.profile.get("strict_major_ratio", 0.20)),
            "adjacent_major": float(self.profile.get("adjacent_major_ratio", 0.25)),
            "generalist": float(self.profile.get("generalist_ratio", 0.35)),
            "trainable": float(self.profile.get("trainable_ratio", 0.20)),
        }

    def _sample_job_layer(self):
        """
        按比例随机抽取岗位层级。
        """
        ratios = self._get_job_layer_ratios()

        total = sum(max(v, 0.0) for v in ratios.values())
        if total <= 0:
            return "generalist"

        draw = random.random() * total
        cum = 0.0

        for layer_name, layer_ratio in ratios.items():
            cum += max(layer_ratio, 0.0)
            if draw <= cum:
                return layer_name

        return "generalist"

    def _is_adjacent_major(self, student_major, job_major):
        """
        判断学生专业与岗位专业是否属于“相近专业”。
            作用：
            - 扩大相近专业范围，提升跨专业流动性
            - 反映现实中企业对相关专业的接受度
        """
        if student_major == job_major:
            return True

        adjacent_groups = [
            {"计算机与人工智能", "电子信息与自动化", "财经与金融"},
            {"电子信息与自动化", "智能制造与机械工程", "计算机与人工智能"},
            {"智能制造与机械工程", "材料与化工", "土木与交通工程"},
            {"土木与交通工程", "智能制造与机械工程"},
            {"管理与工商", "财经与金融", "现代服务与公共管理", "传媒与内容传播"},
            {"传媒与内容传播", "现代服务与公共管理", "管理与工商"},
            {"现代服务与公共管理", "管理与工商", "传媒与内容传播"},
            {"医学与护理", "现代服务与公共管理"},
        ]

        for group in adjacent_groups:
            if student_major in group and job_major in group:
                return True

        return False

    def _build_layered_job_attributes(
        self,
        job_layer,
        is_general_job,
        cross_major_allowed,
        skill_base,
        salary_base,
        industry_boom_factor,
        policy_support,
    ):
        """
        根据岗位层级，构建差异化的岗位属性。
        输入：
        - job_layer: 岗位层级
        - is_general_job: 是否为通用岗
        - cross_major_allowed: 是否允许跨专业
        - skill_base: 基础技能门槛
        - salary_base: 基础薪资
        - industry_boom_factor: 行业景气因子
        - policy_support: 政策支持强度

        输出：
        - cross_major_allowed
        - is_general_job
        - skill_req: 调整后的技能门槛
        - salary: 调整后的薪资
        """
        if job_layer == "strict_major":
            # 严格专业岗：
            # - 原则上要求本专业
            # - 技能门槛更高
            # - 薪资相对更高
            cross_major_allowed = False if not is_general_job else True
            skill_req = round(min(0.98, max(0.52, skill_base + 0.06)), 2)
            salary = round(
                salary_base
                * random.uniform(1.00, 1.22)
                * (1 + 0.05 * max(0.0, industry_boom_factor - 1.0))
                * (1 + 0.03 * policy_support),
                2
            )

        elif job_layer == "adjacent_major":
            # 相近专业岗：
            # - 接受相近专业
            # - 技能门槛中高
            # - 薪资中等偏上
            cross_major_allowed = True
            skill_req = round(min(0.94, max(0.42, skill_base + 0.01)), 2)
            salary = round(
                salary_base
                * random.uniform(0.95, 1.12)
                * (1 + 0.03 * max(0.0, industry_boom_factor - 1.0))
                * (1 + 0.02 * policy_support),
                2
            )

        elif job_layer == "generalist":
            # 通用岗：
            # - 专业约束弱
            # - 技能门槛偏低
            # - 薪资中等
            cross_major_allowed = True
            is_general_job = True
            skill_req = round(min(0.85, max(0.22, skill_base - 0.15)), 2)
            salary = round(
                salary_base
                * random.uniform(0.82, 1.02)
                * (1 + 0.01 * max(0.0, industry_boom_factor - 1.0))
                * (1 + 0.01 * policy_support),
                2
            )

        else:  # trainable
            # 培训岗：
            # - 专业限制最弱
            # - 即时门槛最低
            # - 起薪略低，但更容易吸纳人
            cross_major_allowed = True
            skill_req = round(min(0.78, max(0.18, skill_base - 0.20)), 2)
            salary = round(
                salary_base
                * random.uniform(0.78, 0.98)
                * (1 + 0.01 * max(0.0, industry_boom_factor - 1.0)),
                2
            )

        return cross_major_allowed, is_general_job, skill_req, salary

    def publish_jobs(self):
        """
        发布岗位。

        岗位数量受以下因素影响：
        1. 宏观经济
        2. 行业景气
        3. 政策支持
        4. 企业成长因子
        5. 企业自身基准岗位数

        同时：
        - 岗位专业分布会受行业偏好影响
        - 岗位会按层级进行差异化设置
        """
        self.open_jobs = []

        macro_economy = float(self.model.scenario_config.get("macro_economy", 1.0))
        industry_boom_factor = float(self.model.scenario_config.get("industry_boom_factor", 1.0))
        policy_support = float(self.model.scenario_config.get("policy_support", 0.5))
        city_attractiveness_gap = float(self.model.scenario_config.get("city_attractiveness_gap", 0.5))

        base_job_count = int(self.profile.get("base_job_count", random.randint(6, 12)))
        growth_factor = float(self.profile.get("growth_factor", 1.0))
        policy_factor = 1.0 + 0.2 * policy_support

        raw_job_count = (
            base_job_count
            * macro_economy
            * industry_boom_factor
            * policy_factor
            * growth_factor
        )

        raw_job_count *= random.uniform(0.90, 1.10)
        job_count = max(1, int(round(raw_job_count)))

        preferred_majors = self._get_industry_major_preferences()

        for _ in range(job_count):
            template = self._choose_template(preferred_majors)
            is_general_job = self._is_general_job(template)

            if template is not None and random.random() < 0.85:
                major = self.model.major_code_to_name.get(
                    getattr(template, "major_code", None),
                    random.choice(self.model.majors),
                )
                skill_base = float(getattr(template, "skill_required", 0.6) or 0.6)
                salary_base = float(getattr(template, "salary_base", self.base_salary) or self.base_salary)
                career_growth_base = float(getattr(template, "career_growth", 0.5) or 0.5)
                city_tier_base = float(getattr(template, "city_tier", self.profile.get("city_tier", 0.5)) or 0.5)
                industry_heat_base = float(getattr(template, "industry_heat", 1.0) or 1.0)
                cross_major_allowed = bool(getattr(template, "cross_major_allowed", True))
            else:
                if random.random() < 0.60 and preferred_majors:
                    major = random.choice(preferred_majors)
                else:
                    major = random.choice(self.model.majors)

                skill_base = random.uniform(0.4, 0.9)
                salary_base = self.base_salary
                career_growth_base = random.uniform(0.4, 0.95)
                city_tier_base = self.profile.get("city_tier", random.uniform(0.4, 0.95))
                industry_heat_base = 1.0

                is_general_job = random.random() < 0.35
                cross_major_allowed = True

            # 岗位层级
            job_layer = self._sample_job_layer()

            # 按岗位层级重新设置岗位属性
            cross_major_allowed, is_general_job, skill_req, salary = self._build_layered_job_attributes(
                job_layer=job_layer,
                is_general_job=is_general_job,
                cross_major_allowed=cross_major_allowed,
                skill_base=skill_base,
                salary_base=salary_base,
                industry_boom_factor=industry_boom_factor,
                policy_support=policy_support,
            )

            career_growth = round(
                min(1.0, max(0.3, career_growth_base + 0.05 * (growth_factor - 1.0))),
                2
            )

            # 培训岗给予成长补偿
            if job_layer == "trainable":
                career_growth = min(1.0, round(career_growth + 0.12, 2))
            elif job_layer == "generalist":
                career_growth = min(1.0, round(career_growth + 0.05, 2))

            city_tier = round(
                min(
                    1.0,
                    max(0.2, city_tier_base + random.uniform(-0.1, 0.1) * city_attractiveness_gap),
                ),
                2
            )
            industry_heat = round(
                industry_heat_base * industry_boom_factor * random.uniform(0.8, 1.2),
                2
            )

            job = {
                "major": major,
                "skill_req": skill_req,
                "salary": salary,
                "career_growth": career_growth,
                "city_tier": city_tier,
                "industry_heat": industry_heat,
                "industry": self.industry,
                "employer_type": self.employer_type,
                "region": self.profile.get("region"),
                "cross_major_allowed": cross_major_allowed,
                "is_general_job": is_general_job,
                "job_layer": job_layer,
                "filled": False,
                "hired_student_id": None,
            }
            self.open_jobs.append(job)

        self.last_job_count = len(self.open_jobs)

    def receive_application(self, student, job):
        """
        接收学生申请。
        """
        self.model.round_application_count += 1
        self.applications.append((student, job))

    def hire(self):
        """
        对每个岗位的候选人评分并发放 offer。

        注意：
        - 这里只发 offer，不直接录用
        - 最终是否就业由学生后续 choose_offer 决定

        本方法核心逻辑：
        1. 按岗位层级计算专业匹配
        2. 计算技能匹配与薪资匹配
        3. 形成总评分
        4. 根据岗位层级设定招聘阈值和 offer 数量
        """
        major_preference_strength = max(0.0, float(self.profile.get("major_preference_strength", 0.8)))
        skill_preference_strength = max(0.0, float(self.profile.get("skill_preference_strength", 0.9)))
        cross_major_tolerance = float(self.profile.get("cross_major_tolerance", 0.6))
        hire_threshold = float(self.profile.get("hire_threshold", 0.55))

        salary_weight = max(0.1, 1.0 - major_preference_strength - skill_preference_strength)
        total_weight = major_preference_strength + skill_preference_strength + salary_weight
        major_preference_strength /= total_weight
        skill_preference_strength /= total_weight
        salary_weight /= total_weight

        grouped_applications = {}
        self.last_application_count = len(self.applications)

        for student, job in self.applications:
            if job["filled"] or student.employed:
                continue

            job_id = id(job)
            if job_id not in grouped_applications:
                grouped_applications[job_id] = {
                    "job": job,
                    "candidates": [],
                }

            job_layer = job.get("job_layer", "generalist")

            # -------------------------
            # 1. 按岗位层级计算专业匹配得分
            # -------------------------
            if job_layer == "strict_major":
                if student.major == job["major"]:
                    major_match_score = 1.0
                else:
                    major_match_score = 0.0

            elif job_layer == "adjacent_major":
                if student.major == job["major"]:
                    major_match_score = 1.0
                elif self._is_adjacent_major(student.major, job["major"]):
                    major_match_score = 0.82
                elif job.get("cross_major_allowed", True):
                    mobility = float(getattr(self.model, "major_mobility", {}).get(student.major, 0.5))
                    major_match_score = 0.55 * cross_major_tolerance + 0.25 * mobility
                else:
                    major_match_score = 0.0

            elif job_layer == "generalist":
                if student.major == job["major"]:
                    major_match_score = 0.95
                elif self._is_adjacent_major(student.major, job["major"]):
                    major_match_score = 0.88
                else:
                    major_match_score = 0.78

            else:  # trainable
                if student.major == job["major"]:
                    major_match_score = 0.92
                elif self._is_adjacent_major(student.major, job["major"]):
                    major_match_score = 0.84
                else:
                    major_match_score = 0.76

            # -------------------------
            # 2. 技能匹配
            # -------------------------
            skill_gap = abs(student.skill - job["skill_req"])
            skill_score = max(0.0, 1 - skill_gap)

            # 通用岗、培训岗对技能差距更宽容
            if job_layer == "generalist":
                skill_score = min(1.0, skill_score + 0.12)
            elif job_layer == "trainable":
                skill_score = min(1.0, skill_score + 0.22)
            # -------------------------
            # 3. 薪资匹配
            # -------------------------
            salary_score = min(1.0, job["salary"] / max(student.expected_salary, 1))
            salary_score = max(0.55, salary_score)
            
            total_score = (
                major_preference_strength * major_match_score
                + skill_preference_strength * skill_score
                + salary_weight * salary_score
            )

            grouped_applications[job_id]["candidates"].append({
                "student": student,
                "score": total_score,
            })

        for _, item in grouped_applications.items():
            job = item["job"]
            candidates = sorted(item["candidates"], key=lambda x: x["score"], reverse=True)

            if not candidates:
                continue

            job_layer = job.get("job_layer", "generalist")
            effective_hire_threshold = hire_threshold

            # -------------------------
            # 按岗位层级设置不同阈值
            # -------------------------
            if job_layer == "generalist":
                effective_hire_threshold = max(0.18, hire_threshold - 0.16)
            elif job_layer == "trainable":
                effective_hire_threshold = max(0.10, hire_threshold - 0.25)
            elif job_layer == "adjacent_major":
                effective_hire_threshold = max(0.25, hire_threshold - 0.08)

            # -------------------------
            # 按岗位层级设置最多发放的 offer 数
            # -------------------------
            if job_layer == "strict_major":
                max_offers = 1
            elif job_layer == "adjacent_major":
                max_offers = 2
            elif job_layer == "generalist":
                max_offers = 2
            else:  # trainable
                max_offers = 3

            offer_count = 0
            for candidate in candidates:
                if offer_count >= max_offers:
                    break

                student = candidate["student"]
                score = candidate["score"]

                if student.employed:
                    continue

                if score >= effective_hire_threshold and not job["filled"]:
                    student.receive_offer(self, job)
                    offer_count += 1
        self.applications = []

    def adjust_strategy(self):
        """
        根据空缺率动态调整企业招聘策略：
        1. 空缺高时提高薪资、放宽招聘阈值、增加跨专业容忍度
        2. 空缺低且竞争充分时适度收紧
        """
        if not self.open_jobs:
            return

        vacancy_count = sum(1 for j in self.open_jobs if not j["filled"])
        vacancy_rate = vacancy_count / len(self.open_jobs)

        salary_elasticity = self.profile.get("salary_elasticity", 0.05)
        threshold_relax_speed = self.profile.get("threshold_relax_speed", 0.03)
        tolerance_increase_speed = self.profile.get("tolerance_increase_speed", 0.03)
        threshold_tighten_speed = self.profile.get("threshold_tighten_speed", 0.02)
        tolerance_decrease_speed = self.profile.get("tolerance_decrease_speed", 0.02)
        application_pressure = self.last_application_count / max(self.last_job_count, 1)

        if vacancy_rate > 0.5:
            self.base_salary *= (1 + salary_elasticity)

            self.profile["hire_threshold"] = max(
                0.24,
                self.profile.get("hire_threshold", 0.55) - threshold_relax_speed
            )

            self.profile["cross_major_tolerance"] = min(
                1.0,
                self.profile.get("cross_major_tolerance", 0.6) + tolerance_increase_speed
            )

        elif vacancy_rate < 0.15 and application_pressure >= 2.0:
            self.base_salary *= max(0.95, 1 - salary_elasticity * 0.25)

            self.profile["hire_threshold"] = min(
                0.90,
                self.profile.get("hire_threshold", 0.55) + threshold_tighten_speed
            )

            self.profile["cross_major_tolerance"] = max(
                0.20,
                self.profile.get("cross_major_tolerance", 0.6) - tolerance_decrease_speed
            )