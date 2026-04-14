from mesa import Agent
import random


class EmployerAgent(Agent):
    def __init__(self, unique_id, model, industry, base_salary, employer_type, profile):
        super().__init__(model)
        self.unique_id = unique_id
        self.industry = industry
        self.base_salary = base_salary
        self.employer_type = employer_type
        self.profile = profile
        self.open_jobs = []
        self.applications = []

    def publish_jobs(self):
        self.open_jobs = []

        macro_economy = self.model.scenario_config["macro_economy"]
        industry_boom_factor = self.model.scenario_config["industry_boom_factor"]

        job_count = max(1, int(random.randint(2, 5) * macro_economy * industry_boom_factor))

        # 优先从数据库岗位模板中筛选与企业行业匹配的岗位
        candidate_templates = [
            j for j in self.model.job_templates
            if j.industry == self.industry or j.industry is None
        ]

        # 如果当前行业没有模板，就退回到全部模板
        if not candidate_templates:
            candidate_templates = self.model.job_templates

        for _ in range(job_count):
            if candidate_templates:
                template = random.choice(candidate_templates)
                major_name = self.model.major_code_to_name.get(template.major_code, None)
                if major_name not in self.model.majors:
                    major_name = random.choice(self.model.majors)

                job = {
                    "major": major_name,
                    "skill_req": float(template.skill_required),
                    "salary": float(template.salary_base),
                    "filled": False,
                    "hired_student_id": None,
                    "job_name": template.job_name,
                    "industry": template.industry,
                    "cross_major_allowed": bool(template.cross_major_allowed),
                }
            else:
                # 没有数据库模板时兜底
                job = {
                    "major": random.choice(self.model.majors),
                    "skill_req": round(random.uniform(0.4, 0.9), 2),
                    "salary": round(self.base_salary * random.uniform(0.8, 1.2), 2),
                    "filled": False,
                    "hired_student_id": None,
                    "job_name": "Generated Job",
                    "industry": self.industry,
                    "cross_major_allowed": True,
                }

            self.open_jobs.append(job)
        print(f"DEBUG employer {self.unique_id} published {len(self.open_jobs)} jobs")
    
    def receive_application(self, student, job):
        self.applications.append((student, job))

    def hire(self):
        major_preference_strength = self.profile["major_preference_strength"]
        skill_preference_strength = self.profile["skill_preference_strength"]
        cross_major_tolerance = self.profile["cross_major_tolerance"]
        hire_threshold = self.profile["hire_threshold"]

        salary_weight = max(0.0, 1.0 - major_preference_strength - skill_preference_strength)

        grouped_applications = {}

        for student, job in self.applications:
            if job["filled"] or student.employed:
                continue

            job_id = id(job)
            if job_id not in grouped_applications:
                grouped_applications[job_id] = {
                    "job": job,
                    "candidates": []
                }

            if student.major == job["major"]:
                major_match_score = 1.0
            else:
                if job.get("cross_major_allowed", True):
                    major_match_score = cross_major_tolerance
                else:
                    major_match_score = 0.0
            skill_gap = abs(student.skill - job["skill_req"])
            skill_score = max(0.0, 1.0 - skill_gap)
            salary_score = 1.0 if job["salary"] >= student.expected_salary else 0.7

            total_score = (
                major_preference_strength * major_match_score
                + skill_preference_strength * skill_score
                + salary_weight * salary_score
            )

            grouped_applications[job_id]["candidates"].append({
                "student": student,
                "score": total_score
            })

        for _, item in grouped_applications.items():
            job = item["job"]
            candidates = sorted(item["candidates"], key=lambda x: x["score"], reverse=True)

            for c in candidates:
                student = c["student"]

                if job["filled"] or student.employed:
                    continue

                if c["score"] >= hire_threshold:
                    student.employed = True
                    student.current_offer = job
                    student.matched_job_major = (student.major == job["major"])
                    job["filled"] = True
                    job["hired_student_id"] = student.unique_id
                    break

        self.applications = []

    def adjust_strategy(self):
        if not self.open_jobs:
            return

        salary_elasticity = self.profile["salary_elasticity"]

        vacancy_count = sum(1 for j in self.open_jobs if not j["filled"])
        vacancy_rate = vacancy_count / len(self.open_jobs)

        if vacancy_rate > 0.5:
            self.base_salary *= (1 + salary_elasticity)