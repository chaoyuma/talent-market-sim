from mesa import Agent
import random


class StudentAgent(Agent):
    def __init__(self, unique_id, model, ability, interest, expected_salary,student_type, profile):
        super().__init__(model)
        self.unique_id = unique_id
        self.ability = ability
        self.interest = interest
        self.expected_salary = expected_salary
        self.student_type = student_type
        self.profile = profile
        self.major = None
        self.skill = ability
        self.employed = False
        self.matched_job_major = False
        self.current_offer = None

    def choose_major(self):
        majors = self.model.majors
        scores = {}

        interest_weight = self.profile["interest_weight"]
        salary_weight = self.profile["salary_weight"]
        major_weight = self.profile["major_weight"]
        market_signal_weight = self.profile["market_signal_weight"]
        cross_major_acceptance = self.profile["cross_major_acceptance"]
        information_transparency = self.profile["information_transparency"]

        for major in majors:
            market_heat = self.model.major_market_heat.get(major, 1.0)
            interest_match = 1.0 if major == self.interest else 0.6

            perceived_market_heat = 1 + (market_heat - 1) * information_transparency

            scores[major] = (
                interest_weight * interest_match
                + major_weight * self.ability
                + market_signal_weight * perceived_market_heat
            )

        self.major = max(scores, key=scores.get)

    def study(self):
        school_quality = self.model.school_config["training_quality"]
        self.skill = min(1.0, self.skill + random.uniform(0.05, 0.15) * school_quality)

    def apply_jobs(self):
        if self.employed:
            return

        candidate_jobs = []

        salary_weight = self.model.student_config["salary_weight"]
        major_weight = self.model.student_config["major_weight"]
        cross_major_acceptance = self.model.student_config["cross_major_acceptance"]

        # 为了让总和接近1，动态补齐 skill 权重
        skill_weight = max(0.0, 1.0 - salary_weight - major_weight)

        for employer in self.model.employers:
            for job in employer.open_jobs:
                if job["filled"]:
                    continue

                major_match = 1.0 if job["major"] == self.major else cross_major_acceptance
                skill_match = max(0.0, 1 - abs(job["skill_req"] - self.skill))
                salary_match = 1.0 if job["salary"] >= self.expected_salary else 0.4

                score = (
                    major_weight * major_match
                    + skill_weight * skill_match
                    + salary_weight * salary_match
                )

                candidate_jobs.append((score, employer, job))

        candidate_jobs.sort(key=lambda x: x[0], reverse=True)

        # 最小版先只投递3岗位
        top_k = 5
        for _, employer, job in candidate_jobs[:top_k]:
            employer.receive_application(self, job)