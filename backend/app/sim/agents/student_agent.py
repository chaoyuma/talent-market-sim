from mesa import Agent
import random

from app.sim.market_signals import perceive_market_heat, get_social_major_score


class StudentAgent(Agent):
    """
    学生主体：
    1. 负责专业选择
    2. 负责学习阶段能力演化
    3. 负责岗位投递
    4. 负责 offer 选择
    5. 负责未就业后的去向分流
        6. 负责满意度计算
        7. 负责滞留状态管理
        8. 负责个体化决策参数管理
        9. 负责地区偏好管理
        10. 负责岗位层级偏好管理
        11. 负责连续求职失败后的动态调整

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

        self.student_type = student_type
        self.profile = profile or {}

        self.major = None
        self.skill = ability
        self.employed = False
        self.matched_job_major = False
        self.current_offer = None

        # -------------------------
        # 本轮临时状态
        # -------------------------
        self.just_matched_this_round = False
        self.received_offers = []

        # -------------------------
        # 个体偏好属性
        # -------------------------
        self.city_preference = self.profile.get("city_preference", random.uniform(0.3, 0.9))
        self.career_growth_preference = self.profile.get("career_growth_preference", random.uniform(0.3, 0.9))
        self.risk_preference = self.profile.get("risk_preference", random.uniform(0.2, 0.8))

        # 新增：学生来源地 / 学校城市 / 城市去向偏好
        self.home_region = self.profile.get("home_region", self.profile.get("region"))
        self.school_city = self.profile.get("school_city")
        self.school_region = self.profile.get("school_region")

        self.stay_school_city_preference = self.profile.get("stay_school_city_preference", 0.4)
        self.go_big_city_preference = self.profile.get("go_big_city_preference", 0.5)
        self.return_home_preference = self.profile.get("return_home_preference", 0.3)

        self.satisfaction = 0.0

        # -------------------------
        # 学校 / cohort / 滞留信息
        # -------------------------
        self.school = None
        self.school_type = None
        self.cohort_step = 0
        self.carryover_rounds = 0
        self.is_carryover = False
        self.rejected_job_ids = set()

        # -------------------------
        # 去向状态
        # -------------------------
        # destination:
        # - job_searching：继续求职
        # - employed：已就业
        # - further_study：升学
        # - public_exam：考公考编
        # - flexible_employment：灵活就业
        self.destination = "job_searching"

        # 是否退出岗位市场
        self.exit_market = False

        # 连续求职失败轮次
        self.failed_search_rounds = 0

    
    # 基础辅助方法
    
    def _decision_param(self, key, default):
        """
        读取学生个体化决策参数。

        优先级：
        1. 学生画像 profile
        2. 全局 student_config
        3. 默认值
        """
        return self.profile.get(key, self.model.student_config.get(key, default))

    def _cross_major_acceptance(self, job_major=None):
        """
        计算学生对跨专业岗位的基础接受度。
        """
        base = float(self._decision_param("cross_major_acceptance", 0.7))

        if job_major and job_major != self.major:
            mobility = float(getattr(self.model, "major_mobility", {}).get(self.major, 0.5))
            return max(0.0, min(1.0, 0.7 * base + 0.3 * mobility))

        return base

    def _effective_expected_salary(self):
        """
        计算当前轮的有效薪资预期。

        作用：
        - 滞留学生连续求职失败后，会逐步降低薪资预期
        - 更贴近现实中的“先找工作、后找理想工作”行为
        """
        decay = 1.0 - 0.06 * getattr(self, "carryover_rounds", 0)
        decay = max(0.72, decay)
        return max(1.0, self.expected_salary * decay)

    def _effective_cross_major_acceptance(self, job_major=None):
        """
        计算当前轮的有效跨专业接受度。

        作用：
        - 连续滞留后，学生更容易接受跨专业岗位
        """
        base = self._cross_major_acceptance(job_major)
        bonus = min(0.25, 0.06 * getattr(self, "carryover_rounds", 0))
        return max(0.0, min(1.0, base + bonus))

    def _region_match_score(self, job):
        """
        计算地区匹配得分。
        """
        if not self.model.type_config.get("enable_regional_preference", True):
            return 1.0

        student_region = self.profile.get("region")
        job_region = job.get("region")

        if not student_region or not job_region:
            return 0.8

        if student_region == job_region:
            return 1.0

        migration_cost = float(self.model.scenario_config.get("migration_cost_weight", 0.15))
        return max(0.4, 1.0 - migration_cost)

    def _effective_region_match_score(self, job):
        """
        计算当前轮的有效地区匹配得分。

        作用：
        - 滞留学生会逐步放宽地区偏好
        """
        base_score = self._region_match_score(job)
        bonus = min(0.20, 0.05 * getattr(self, "carryover_rounds", 0))
        return max(base_score, min(1.0, base_score + bonus))
    def _location_preference_score(self, job):
        """
        计算学生对岗位地点的综合偏好得分。

        """
        job_city = job.get("city")
        job_region = job.get("region")
        job_city_tier = job.get("city_tier", 0.5)

        score = 0.0

        # -------------------------
        # 1. 留学校城市 / 学校区域
        # -------------------------
        if self.school_city and job_city == self.school_city:
            score += 0.32 * self.stay_school_city_preference
        elif self.school_region and job_region == self.school_region:
            score += 0.15 * self.stay_school_city_preference

        # -------------------------
        # 2. 回家乡
        # -------------------------
        if self.home_region and job_region == self.home_region:
            score += 0.28 * self.return_home_preference

        # -------------------------
        # 3. 去大城市
        # -------------------------
        score += 0.38 * self.go_big_city_preference * job_city_tier

        # -------------------------
        # 4. 滞留学生逐渐更现实：
        # -------------------------
        if getattr(self, "carryover_rounds", 0) > 0:
            carry_bonus = min(0.08, 0.02 * self.carryover_rounds)
            if (self.school_region and job_region == self.school_region) or (
                self.home_region and job_region == self.home_region
            ):
                score += carry_bonus

        return max(0.0, min(1.0, score)) 
    def _job_layer_preference_score(self, job, for_offer=False):
        """
        根据岗位层级计算学生偏好得分。

        job_layer:
        - strict_major
        - adjacent_major
        - generalist
        - trainable

        说明：
        - for_offer=False：用于投递阶段
        - for_offer=True：用于接 offer 阶段
        """
        job_layer = job.get("job_layer", "generalist")
        is_same_major = (job.get("major") == self.major)

        # -------------------------
        # 基础偏好
        # -------------------------
        if job_layer == "strict_major":
            score = 1.0 if is_same_major else 0.50
        elif job_layer == "adjacent_major":
            score = 0.92
        elif job_layer == "generalist":
            score = 0.82
        else:  # trainable
            score = 0.76

        # -------------------------
        # 学生类型修正
        # -------------------------
        if self.student_type == "interest_oriented":
            if job_layer == "strict_major":
                score += 0.08
            elif job_layer == "trainable":
                score -= 0.05

        elif self.student_type == "employment_oriented":
            if job_layer in ("generalist", "trainable"):
                score += 0.08

        elif self.student_type == "salary_oriented":
            if job_layer == "trainable":
                score -= 0.06
            elif job_layer == "strict_major":
                score += 0.03

        elif self.student_type == "prestige_oriented":
            if job_layer == "strict_major":
                score += 0.06
            elif job_layer == "generalist":
                score -= 0.04

        elif self.student_type == "trend_sensitive":
            # 趋势敏感型更容易接受通用岗位和热门行业岗位
            if job_layer in ("adjacent_major", "generalist"):
                score += 0.05

        # -------------------------
        # 滞留轮次修正
        # -------------------------
        # 滞留越久，对 generalist / trainable 越开放
        if getattr(self, "carryover_rounds", 0) > 0:
            bonus = min(0.20, 0.05 * self.carryover_rounds)
            if job_layer in ("generalist", "trainable"):
                score += bonus
            elif job_layer == "strict_major":
                score -= min(0.10, 0.03 * self.carryover_rounds)

        # -------------------------
        # 接 offer 阶段，对 trainable 给予成长补偿
        # -------------------------
        if for_offer and job_layer == "trainable":
            score += 0.06

        return max(0.0, min(1.2, score))

    
    # 状态管理
    
    def reset_round_state(self):
        """
        重置学生本轮临时状态，不清空历史就业结果。
        """
        self.just_matched_this_round = False
        self.received_offers = []
        self.current_offer = None
        self.matched_job_major = False

    def prepare_for_carryover(self):
        """
        为未就业滞留学生进入下一轮做准备。

        作用：
        1. 重置本轮临时状态
        2. 标记为滞留学生
        3. 累积滞留轮次
        4. 给一定技能增益，模拟继续学习或求职磨合
        """
        self.reset_round_state()
        self.carryover_rounds += 1
        self.is_carryover = True
        self.employed = False
        self.satisfaction = 0.0
        self.rejected_job_ids = set()

        # 继续留在市场中的学生，其去向仍是继续求职
        self.destination = "job_searching"
        self.exit_market = False

        skill_gain = float(self.model.student_config.get("carryover_skill_gain", 0.01))
        self.skill = min(1.0, self.skill + skill_gain)

    
    # 专业选择与学习
    
    def choose_major(self):
        """
        专业选择：
        综合考虑兴趣、能力、市场热度、预期薪资、政策支持、
        以及学校供给侧慢反馈形成的专业偏置。
        """
        majors = self.model.majors
        scores = {}

        scenario_cfg = self.model.scenario_config

        interest_weight = self._decision_param("interest_weight", 0.3)
        market_signal_weight = self._decision_param("market_signal_weight", 0.1)
        salary_weight = self._decision_param("salary_weight", 0.2)
        herd_strength = float(self.model.type_config.get("herd_strength", 0.0))

        policy_support = scenario_cfg.get("policy_support", 0.5)

        for major in majors:
            perceived_market_heat = perceive_market_heat(
                model=self.model,
                major=major,
                information_level=self.profile.get("information_level"),
                transparency=self._decision_param("information_transparency", 0.8),
            )

            interest_match = 1.0 if major == self.interest else 0.5
            ability_match = self.ability
            salary_score = self.model.major_salary_expectation.get(major, 0.6)
            policy_weight = getattr(self.model, "major_policy_support_weight", {}).get(major, 0.5)

            policy_bonus = 0.1 * policy_support * policy_weight

            school_adjustment_bias = self.model.major_school_adjustment_bias.get(major, 0.0)
            if isinstance(school_adjustment_bias, list):
                school_adjustment_bias = (
                    sum(school_adjustment_bias) / len(school_adjustment_bias)
                    if school_adjustment_bias else 0.0
                )

            total_score = (
                interest_weight * interest_match
                + 0.25 * ability_match
                + market_signal_weight * perceived_market_heat
                + salary_weight * salary_score
                + policy_bonus
                + school_adjustment_bias
                + herd_strength * get_social_major_score(self.model, major)
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

        school_quality = (
            self.school.profile.get("training_quality", self.model.school_training_quality_avg)
            if self.school is not None
            else self.model.school_training_quality_avg
        )
        learning_effort = self.profile.get("learning_effort", random.uniform(0.5, 1.0))
        major_match_bonus = 0.05 if self.major == self.interest else 0.0

        delta = random.uniform(0.03, 0.12) * school_quality * learning_effort + major_match_bonus
        self.skill = min(1.0, self.skill + delta)

    
    # 岗位投递
    
    def apply_jobs(self):
        """
        岗位投递：
        不只投一个岗位，而是对岗位打分后，投递 top-k 个岗位。

        本版本优化：
        1. 学生会识别 job_layer
        2. 滞留学生会更愿意投 generalist / trainable
        3. 不同学生类型对岗位层级偏好不同
        """
        if self.employed or self.exit_market:
            return

        self.received_offers = []

        # 滞留学生会适度增加投递数量
        base_max_applications = int(self._decision_param("max_applications_per_step", 3))
        carryover_bonus = min(6, getattr(self, "carryover_rounds", 0) * 2)
        max_applications = max(1, base_max_applications + carryover_bonus)

        major_weight = self._decision_param("major_weight", 0.3)
        salary_weight = self._decision_param("salary_weight", 0.2)
        city_weight = self._decision_param("city_weight", 0.1)
        region_weight = self._decision_param("region_weight", 0.05)
        market_signal_weight = self._decision_param("market_signal_weight", 0.1)

        effective_expected_salary = self._effective_expected_salary()

        candidate_jobs = []

        for employer in self.model.employers:
            for job in employer.open_jobs:
                if job["filled"]:
                    continue
                if id(job) in self.rejected_job_ids:
                    continue

                # -------------------------
                # 专业匹配
                # -------------------------
                if job.get("is_general_job", False):
                    major_match = 0.85
                else:
                    if job["major"] == self.major:
                        major_match = 1.0
                    elif not job.get("cross_major_allowed", True):
                        major_match = 0.0
                    else:
                        major_match = self._effective_cross_major_acceptance(job["major"])

                # -------------------------
                # 技能匹配
                # -------------------------
                skill_match = max(0.0, 1 - abs(job["skill_req"] - self.skill))

                # 培训岗、通用岗对技能不足更宽容
                job_layer = job.get("job_layer", "generalist")
                if job_layer == "generalist":
                    skill_match = min(1.0, skill_match + 0.05)
                elif job_layer == "trainable":
                    skill_match = min(1.0, skill_match + 0.12)

                # -------------------------
                # 薪资与城市
                # -------------------------
                salary_score = min(1.0, job["salary"] / max(effective_expected_salary, 1))

                                # -------------------------
                # 城市/地区偏好：
                # 留学校城市、回家乡、去大城市三类力量共同作用
                # -------------------------
                city_score = self._location_preference_score(job)

                growth_score = job.get("career_growth", 0.5)

                # 风险偏好越低，越看重稳定性
                stability_score = employer.profile.get("stability", 0.6)
                stability_preference_score = (
                    (1 - self.risk_preference) * stability_score
                    + self.risk_preference * 0.5
                )

                market_score = job.get("industry_heat", 1.0)
                region_score = self._effective_region_match_score(job)

                # -------------------------
                # 岗位层级偏好
                # -------------------------
                job_layer_score = self._job_layer_preference_score(job, for_offer=False)

                total_score = (
                    major_weight * major_match
                    + 0.25 * skill_match
                    + salary_weight * salary_score
                    + city_weight * city_score
                    + region_weight * region_score
                    + 0.15 * (self.career_growth_preference * growth_score)
                    + 0.10 * stability_preference_score
                    + market_signal_weight * market_score
                    + 0.08 * job_layer_score
                )

                candidate_jobs.append((total_score, employer, job))

        candidate_jobs.sort(key=lambda x: x[0], reverse=True)

        # 前若干名中保留一定探索性
        pool_size = min(len(candidate_jobs), max(20, max_applications * 3))
        top_pool = candidate_jobs[:pool_size]

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
        self.model.round_offer_count += 1
        self.received_offers.append((employer, job))

    
    # 未就业去向分流
    
    def decide_post_failure_destination(self):
        """
        未就业后的去向分流决策。

        目标：
        1. 不让所有未就业学生都继续留在求职池
        2. 模拟升学、考公考编、灵活就业等现实分流路径
        """
        if self.employed:
            self.destination = "employed"
            self.exit_market = True
            return

        self.failed_search_rounds += 1

        search_persistence_base = float(
            self.model.student_config.get("search_persistence_base", 0.75)
        )
        further_study_base_rate = float(
            self.model.student_config.get("further_study_base_rate", 0.08)
        )
        public_exam_base_rate = float(
            self.model.student_config.get("public_exam_base_rate", 0.06)
        )
        flexible_employment_base_rate = float(
            self.model.student_config.get("flexible_employment_base_rate", 0.05)
        )
        failed_search_exit_boost = float(
            self.model.student_config.get("failed_search_exit_boost", 0.08)
        )

        p_search = search_persistence_base
        p_study = further_study_base_rate
        p_exam = public_exam_base_rate
        p_flexible = flexible_employment_base_rate

        # 连续失败会降低继续求职概率
        exit_boost = min(0.30, self.failed_search_rounds * failed_search_exit_boost)
        p_search = max(0.20, p_search - exit_boost)

        # 学生类型修正
        if self.student_type == "interest_oriented":
            p_study += 0.06
        elif self.student_type == "prestige_oriented":
            p_study += 0.04
            p_exam += 0.04
        elif self.student_type == "salary_oriented":
            p_search += 0.05
        elif self.student_type == "employment_oriented":
            p_search += 0.05
            p_flexible += 0.03
        elif self.student_type == "trend_sensitive":
            p_flexible += 0.05

        # 风险偏好修正
        risk_preference = float(getattr(self, "risk_preference", 0.5))
        p_exam += max(0.0, (0.5 - risk_preference) * 0.10)
        p_flexible += max(0.0, (risk_preference - 0.5) * 0.12)

        total = p_search + p_study + p_exam + p_flexible
        p_search /= total
        p_study /= total
        p_exam /= total
        p_flexible /= total

        draw = self.random.random()

        if draw < p_search:
            self.destination = "job_searching"
            self.exit_market = False
        elif draw < p_search + p_study:
            self.destination = "further_study"
            self.exit_market = True
        elif draw < p_search + p_study + p_exam:
            self.destination = "public_exam"
            self.exit_market = True
        else:
            self.destination = "flexible_employment"
            self.exit_market = True

    
    # 接收 offer
    
    def choose_offer(self):
        """
        若收到多个 offer，则学生基于效用函数选择一个最优岗位。

        本版本优化：
        1. 感知 job_layer
        2. 培训岗给予成长补偿
        3. 滞留学生会更愿意接受 generalist / trainable
        """
        if self.employed or not self.received_offers:
            if not self.employed and not self.received_offers:
                self.decide_post_failure_destination()
            return

        best_offer = None
        best_utility = -1

        effective_expected_salary = self._effective_expected_salary()

        for employer, job in self.received_offers:
            salary_score = min(1.2, job["salary"] / max(effective_expected_salary, 1))

            if job.get("is_general_job", False):
                major_match = 0.85
            else:
                if job["major"] == self.major:
                    major_match = 1.0
                elif not job.get("cross_major_allowed", True):
                    major_match = 0.0
                else:
                    major_match = self._effective_cross_major_acceptance(job["major"])

            city_score = self._location_preference_score(job)
            region_score = self._effective_region_match_score(job)
            growth_score = job.get("career_growth", 0.5)
            stability_score = employer.profile.get("stability", 0.6)

            job_layer = job.get("job_layer", "generalist")

            # 培训岗给成长补偿
            if job_layer == "trainable":
                growth_score = min(1.0, growth_score + 0.12)
            elif job_layer == "generalist":
                growth_score = min(1.0, growth_score + 0.04)

            growth_component = self.career_growth_preference * growth_score
            stability_component = (1 - self.risk_preference) * stability_score

            job_layer_score = self._job_layer_preference_score(job, for_offer=True)

            utility = (
                0.28 * salary_score
                + 0.22 * major_match
                + 0.14 * city_score
                + 0.05 * region_score
                + 0.18 * growth_component
                + 0.08 * stability_component
                + 0.05 * job_layer_score
            )

            best_candidate = utility
            if best_candidate > best_utility:
                best_utility = best_candidate
                best_offer = (employer, job)

        # 滞留学生适度降低接受阈值
        base_reservation_utility = float(self._decision_param("reservation_utility", 0.0))
        reservation_discount = min(0.14, 0.04 * getattr(self, "carryover_rounds", 0))
        reservation_utility = max(0.0, base_reservation_utility - reservation_discount)

        if best_offer is not None and best_utility >= reservation_utility:
            _, chosen_job = best_offer

            self.employed = True
            self.just_matched_this_round = True
            self.current_offer = chosen_job
            self.matched_job_major = (self.major == chosen_job["major"])
            chosen_job["filled"] = True
            chosen_job["hired_student_id"] = self.unique_id

            self.model.round_accepted_offer_count += 1
            self.model.round_rejected_offer_count += max(0, len(self.received_offers) - 1)

            self.destination = "employed"
            self.exit_market = True

            self.satisfaction = self._calculate_satisfaction(chosen_job, best_offer[0])

            for _employer, job in self.received_offers:
                if job is not chosen_job:
                    self.rejected_job_ids.add(id(job))
        else:
            self.model.round_rejected_offer_count += len(self.received_offers)
            for _employer, job in self.received_offers:
                self.rejected_job_ids.add(id(job))

            self.decide_post_failure_destination()

        self.received_offers = []

    def _calculate_satisfaction(self, job, employer=None):
        """
        满意度：薪资、专业匹配、城市、成长空间、稳定性的综合。
        """
        effective_expected_salary = self._effective_expected_salary()
        salary_satisfaction = min(1.2, job["salary"] / max(effective_expected_salary, 1))

        if job.get("is_general_job", False):
            major_match = 0.85
        else:
            major_match = (
                1.0 if job["major"] == self.major
                else self._effective_cross_major_acceptance(job["major"])
            )

        city_match = self._location_preference_score(job)
        region_match = self._effective_region_match_score(job)
        growth_match = self.career_growth_preference * job.get("career_growth", 0.5)

        # 培训岗成长补偿
        if job.get("job_layer", "generalist") == "trainable":
            growth_match = min(1.0, growth_match + 0.08)

        stability_score = 0.6
        if employer is not None:
            stability_score = employer.profile.get("stability", 0.6)
        stability_match = (1 - self.risk_preference) * stability_score

        return (
            0.30 * salary_satisfaction
            + 0.22 * major_match
            + 0.14 * city_match
            + 0.05 * region_match
            + 0.19 * growth_match
            + 0.10 * stability_match
        )