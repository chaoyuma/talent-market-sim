from mesa import Agent
import random


class StudentAgent(Agent):
    """
    学生主体：
    1. 负责专业选择
    2. 负责学习阶段能力演化
    3. 负责岗位投递
    4. 负责 offer 选择
    """

    def __init__(
        self,
        unique_id,
        model,
        ability,
        interest,
        expected_salary,
        student_type=None,
        profile=None,
    ):
        super().__init__(model)
        self.unique_id = unique_id
        self.ability = ability
        self.interest = interest
        self.expected_salary = expected_salary

        self.just_matched_this_round = False
        self.received_offers = []

        self.student_type = student_type
        self.profile = profile or {}

        self.major = None
        self.skill = ability
        self.employed = False
        self.matched_job_major = False
        self.current_offer = None

        # 个体偏好属性
        self.city_preference = self.profile.get("city_preference", random.uniform(0.3, 0.9))
        self.career_growth_preference = self.profile.get("career_growth_preference", random.uniform(0.3, 0.9))
        self.risk_preference = self.profile.get("risk_preference", random.uniform(0.2, 0.8))
        self.satisfaction = 0.0

        self.received_offers = []

    def reset_round_state(self):
        """
        重置学生本轮临时状态，不清空历史就业结果。
        """
        self.just_matched_this_round = False
        self.received_offers = []

    def choose_major(self):
        """
        专业选择：
        综合考虑兴趣、能力、市场热度、预期薪资、政策支持、
        以及学校供给侧慢反馈形成的专业偏置。
        """
        majors = self.model.majors
        scores = {}

        student_cfg = self.model.student_config
        scenario_cfg = self.model.scenario_config

        interest_weight = student_cfg.get("interest_weight", 0.3)
        market_signal_weight = student_cfg.get("market_signal_weight", 0.1)
        salary_weight = student_cfg.get("salary_weight", 0.2)

        policy_support = scenario_cfg.get("policy_support", 0.5)
        info_transparency = student_cfg.get("information_transparency", 0.8)

        for major in majors:
            true_market_heat = self.model.major_market_heat.get(major, 1.0)

            # 感知热度 = 真实热度 + 噪声
            noisy_signal = true_market_heat * random.uniform(0.7, 1.3)
            perceived_market_heat = (
                info_transparency * true_market_heat
                + (1 - info_transparency) * noisy_signal
            )

            interest_match = 1.0 if major == self.interest else 0.5
            ability_match = self.ability
            salary_score = self.model.major_salary_expectation.get(major, 0.6)

            # 政策支持加成
            policy_bonus = 0.1 * policy_support

            # 新增：学校慢反馈对专业供给倾向的影响
            school_adjustment_bias = self.model.major_school_adjustment_bias.get(major, 0.0)

            total_score = (
                interest_weight * interest_match
                + 0.25 * ability_match
                + market_signal_weight * perceived_market_heat
                + salary_weight * salary_score
                + policy_bonus
                + school_adjustment_bias
            )

            scores[major] = total_score

        self.major = max(scores, key=scores.get)

    def study(self):
        """
        学习阶段能力演化：
        能力受学校培养质量、个人投入、专业匹配影响。
        """
        if self.major is None:
            return

        school_quality = self.model.school_training_quality_avg
        learning_effort = self.profile.get("learning_effort", random.uniform(0.5, 1.0))
        major_match_bonus = 0.05 if self.major == self.interest else 0.0

        delta = random.uniform(0.03, 0.12) * school_quality * learning_effort + major_match_bonus
        self.skill = min(1.0, self.skill + delta)

    def apply_jobs(self):
        """
        岗位投递：
        不只投一个岗位，而是对岗位打分后，投递 top-k 个岗位。
        同时引入成长偏好与风险偏好。
        """
        if self.employed:
            return

        self.received_offers = []

        student_cfg = self.model.student_config
        max_applications = int(student_cfg.get("max_applications_per_step", 3))
        major_weight = student_cfg.get("major_weight", 0.3)
        salary_weight = student_cfg.get("salary_weight", 0.2)
        city_weight = student_cfg.get("city_weight", 0.1)
        market_signal_weight = student_cfg.get("market_signal_weight", 0.1)

        candidate_jobs = []

        for employer in self.model.employers:
            for job in employer.open_jobs:
                if job["filled"]:
                    continue

                major_match = (
                    1.0
                    if job["major"] == self.major
                    else self.model.student_config.get("cross_major_acceptance", 0.7)
                )
                skill_match = max(0.0, 1 - abs(job["skill_req"] - self.skill))
                salary_score = min(1.0, job["salary"] / max(self.expected_salary, 1))
                city_score = 1.0 if job.get("city_tier", 0.5) >= self.city_preference else 0.7
                growth_score = job.get("career_growth", 0.5)

                # 新增：风险偏好越低，越看重稳定性
                stability_score = employer.profile.get("stability", 0.6)
                stability_preference_score = (
                    (1 - self.risk_preference) * stability_score
                    + self.risk_preference * 0.5
                )

                market_score = job.get("industry_heat", 1.0)

                total_score = (
                    major_weight * major_match
                    + 0.25 * skill_match
                    + salary_weight * salary_score
                    + city_weight * city_score
                    + 0.15 * (self.career_growth_preference * growth_score)
                    + 0.10 * stability_preference_score
                    + market_signal_weight * market_score
                )

                candidate_jobs.append((total_score, employer, job))

        candidate_jobs.sort(key=lambda x: x[0], reverse=True)

        # 前若干名中保留一定探索性，避免全是死板 top-k
        top_pool = candidate_jobs[: min(len(candidate_jobs), 20)]
        selected_jobs = []

        strict_count = max(1, int(max_applications * 0.7))
        selected_jobs.extend(top_pool[:strict_count])

        remaining_needed = max_applications - len(selected_jobs)
        if remaining_needed > 0:
            remaining_pool = top_pool[strict_count:]
            if remaining_pool:
                selected_jobs.extend(
                    random.sample(
                        remaining_pool,
                        k=min(remaining_needed, len(remaining_pool))
                    )
                )

        for _, employer, job in selected_jobs:
            employer.receive_application(self, job)

    def receive_offer(self, employer, job):
        """
        企业向学生发 offer。
        """
        self.received_offers.append((employer, job))

    def choose_offer(self):
        """
        若收到多个 offer，则学生基于效用函数选择一个最优岗位。
        引入成长偏好与风险偏好，体现职业发展与稳定性差异。
        """
        if self.employed or not self.received_offers:
            return

        best_offer = None
        best_utility = -1

        for employer, job in self.received_offers:
            salary_score = min(1.2, job["salary"] / max(self.expected_salary, 1))
            major_match = (
                1.0
                if job["major"] == self.major
                else self.model.student_config.get("cross_major_acceptance", 0.7)
            )
            city_score = 1.0 if job.get("city_tier", 0.5) >= self.city_preference else 0.7
            growth_score = job.get("career_growth", 0.5)
            stability_score = employer.profile.get("stability", 0.6)

            growth_component = self.career_growth_preference * growth_score
            stability_component = (1 - self.risk_preference) * stability_score

            utility = (
                0.30 * salary_score
                + 0.25 * major_match
                + 0.15 * city_score
                + 0.20 * growth_component
                + 0.10 * stability_component
            )

            if utility > best_utility:
                best_utility = utility
                best_offer = (employer, job)

        if best_offer is not None:
            _, chosen_job = best_offer
            self.employed = True
            self.just_matched_this_round = True
            self.current_offer = chosen_job
            self.matched_job_major = (self.major == chosen_job["major"])
            chosen_job["filled"] = True
            chosen_job["hired_student_id"] = self.unique_id

            # 计算满意度
            self.satisfaction = self._calculate_satisfaction(chosen_job, best_offer[0])

        self.received_offers = []

    def _calculate_satisfaction(self, job, employer=None):
        """
        满意度：薪资、专业匹配、城市、成长空间、稳定性的综合。
        """
        salary_satisfaction = min(1.2, job["salary"] / max(self.expected_salary, 1))
        major_match = (
            1.0
            if job["major"] == self.major
            else self.model.student_config.get("cross_major_acceptance", 0.7)
        )
        city_match = 1.0 if job.get("city_tier", 0.5) >= self.city_preference else 0.7
        growth_match = self.career_growth_preference * job.get("career_growth", 0.5)

        stability_score = 0.6
        if employer is not None:
            stability_score = employer.profile.get("stability", 0.6)
        stability_match = (1 - self.risk_preference) * stability_score

        return (
            0.30 * salary_satisfaction
            + 0.25 * major_match
            + 0.15 * city_match
            + 0.20 * growth_match
            + 0.10 * stability_match
        )