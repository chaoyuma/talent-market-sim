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

    def publish_jobs(self):
        """
        岗位发布数量受宏观经济与行业景气影响。
        """
        self.open_jobs = []

        macro_economy = self.model.scenario_config.get("macro_economy", 1.0)
        industry_boom_factor = self.model.scenario_config.get("industry_boom_factor", 1.0)

        base_count = random.randint(2, 5)
        job_count = max(1, int(base_count * macro_economy * industry_boom_factor))

        for _ in range(job_count):
            major = random.choice(self.model.majors)
            job = {
                "major": major,
                "skill_req": round(random.uniform(0.4, 0.9), 2),
                "salary": round(self.base_salary * random.uniform(0.8, 1.2), 2),
                "career_growth": round(random.uniform(0.4, 0.95), 2),
                "city_tier": round(random.uniform(0.4, 0.95), 2),
                "industry_heat": round(industry_boom_factor * random.uniform(0.8, 1.2), 2),
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