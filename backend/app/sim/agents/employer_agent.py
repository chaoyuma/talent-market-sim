from mesa import Agent
import random


class EmployerAgent(Agent):
    """
    企业主体：
    1. 发布岗位
    2. 接收学生申请
    3. 对候选人评分并发放 offer
    4. 根据空缺率动态调整招聘策略
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

    def _get_industry_major_preferences(self):
        """
        给不同行业一个较粗粒度的专业偏好映射，
        让岗位结构不再完全随机。
        """
        industry_map = {
            "Internet": ["CS", "Finance"],
            "AI": ["CS", "Finance"],
            "Finance": ["Finance", "CS"],
            "Manufacturing": ["Mechanical", "CS"],
            "Education": ["Education", "CS"],
            "Healthcare": ["Education", "Finance"],
        }
        return industry_map.get(self.industry, self.model.majors)

    def publish_jobs(self):
        """
        岗位发布数量受：
        1. 宏观经济
        2. 行业景气
        3. 政策支持
        4. 企业成长因子
        5. 企业基准岗位数
        共同影响。

        同时，岗位专业分布与企业所属行业存在一定对应关系。
        """
        self.open_jobs = []

        macro_economy = float(self.model.scenario_config.get("macro_economy", 1.0))
        industry_boom_factor = float(self.model.scenario_config.get("industry_boom_factor", 1.0))
        policy_support = float(self.model.scenario_config.get("policy_support", 0.5))

        # 企业画像参数
        base_job_count = int(self.profile.get("base_job_count", random.randint(2, 5)))
        growth_factor = float(self.profile.get("growth_factor", 1.0))

        # 政策支持转为适度的岗位扩张效应，避免过强
        policy_factor = 1.0 + 0.2 * policy_support

        # 岗位总量
        raw_job_count = (
            base_job_count
            * macro_economy
            * industry_boom_factor
            * policy_factor
            * growth_factor
        )

        # 增加一点波动，但不要太大
        raw_job_count *= random.uniform(0.85, 1.15)

        job_count = max(1, int(round(raw_job_count)))

        # 行业对应的偏好专业
        preferred_majors = self._get_industry_major_preferences()

        for _ in range(job_count):
            # 大概率从行业偏好专业里选，小概率从全专业里探索
            if random.random() < 0.75 and preferred_majors:
                major = random.choice(preferred_majors)
            else:
                major = random.choice(self.model.majors)

            # 技能要求：景气更高时，高要求岗位可略增
            skill_req = round(
                min(0.95, max(0.3, random.uniform(0.4, 0.9) + 0.05 * (industry_boom_factor - 1.0))),
                2
            )

            # 薪资：受基准薪资、景气、政策支持影响
            salary_multiplier = random.uniform(0.8, 1.2) * (1 + 0.1 * (industry_boom_factor - 1.0))
            salary_multiplier *= (1 + 0.05 * policy_support)
            salary = round(self.base_salary * salary_multiplier, 2)

            # 成长空间：成长型行业景气高时更高
            career_growth = round(
                min(1.0, max(0.3, random.uniform(0.4, 0.95) + 0.05 * (growth_factor - 1.0))),
                2
            )

            city_tier = round(random.uniform(0.4, 0.95), 2)
            industry_heat = round(industry_boom_factor * random.uniform(0.8, 1.2), 2)

            job = {
                "major": major,
                "skill_req": skill_req,
                "salary": salary,
                "career_growth": career_growth,
                "city_tier": city_tier,
                "industry_heat": industry_heat,
                "filled": False,
                "hired_student_id": None,
            }
            self.open_jobs.append(job)

    def receive_application(self, student, job):
        """
        接收学生申请。
        """
        self.applications.append((student, job))

    def hire(self):
        """
        对每个岗位的候选人统一评分，向最优学生发放 offer。
        注意：此处先发 offer，不直接让学生立即就业，由学生后续 choose_offer 决策。
        """
        major_preference_strength = self.profile.get("major_preference_strength", 0.8)
        skill_preference_strength = self.profile.get("skill_preference_strength", 0.9)
        cross_major_tolerance = self.profile.get("cross_major_tolerance", 0.6)
        hire_threshold = self.profile.get("hire_threshold", 0.55)

        salary_weight = max(0.0, 1.0 - major_preference_strength - skill_preference_strength)

        grouped_applications = {}

        for student, job in self.applications:
            if job["filled"] or student.employed:
                continue

            job_id = id(job)
            if job_id not in grouped_applications:
                grouped_applications[job_id] = {
                    "job": job,
                    "candidates": [],
                }

            major_match_score = 1.0 if student.major == job["major"] else cross_major_tolerance
            skill_gap = abs(student.skill - job["skill_req"])
            skill_score = max(0.0, 1 - skill_gap)
            salary_score = 1.0 if job["salary"] >= student.expected_salary else 0.7

            total_score = (
                major_preference_strength * major_match_score
                + skill_preference_strength * skill_score
                + salary_weight * salary_score
            )

            grouped_applications[job_id]["candidates"].append({
                "student": student,
                "score": total_score,
            })

        # 每个岗位只给最优候选人发 offer
        for _, item in grouped_applications.items():
            job = item["job"]
            candidates = sorted(item["candidates"], key=lambda x: x["score"], reverse=True)

            if not candidates:
                continue

            best_candidate = candidates[0]
            if best_candidate["score"] >= hire_threshold and not job["filled"]:
                best_candidate["student"].receive_offer(self, job)

        self.applications = []

    def adjust_strategy(self):
        """
        根据空缺率动态调整企业招聘策略：
        1. 提高薪资
        2. 放宽招聘阈值
        3. 增加跨专业容忍度
        """
        if not self.open_jobs:
            return

        vacancy_count = sum(1 for j in self.open_jobs if not j["filled"])
        vacancy_rate = vacancy_count / len(self.open_jobs)

        salary_elasticity = self.profile.get("salary_elasticity", 0.05)
        threshold_relax_speed = self.profile.get("threshold_relax_speed", 0.03)
        tolerance_increase_speed = self.profile.get("tolerance_increase_speed", 0.03)

        if vacancy_rate > 0.5:
            self.base_salary *= (1 + salary_elasticity)

            self.profile["hire_threshold"] = max(
                0.30,
                self.profile.get("hire_threshold", 0.55) - threshold_relax_speed
            )

            self.profile["cross_major_tolerance"] = min(
                1.0,
                self.profile.get("cross_major_tolerance", 0.6) + tolerance_increase_speed
            )