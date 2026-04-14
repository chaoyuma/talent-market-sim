from collections import Counter
import random

from mesa import Model

from app.sim.agents.student_agent import StudentAgent
from app.sim.agents.school_agent import SchoolAgent
from app.sim.agents.employer_agent import EmployerAgent
from app.services.data_manage_service import load_simulation_data
from app.sim.profiles import (
    STUDENT_TYPE_PROFILES,
    SCHOOL_TYPE_PROFILES,
    EMPLOYER_TYPE_PROFILES,
)


class TalentMarketModel(Model):
    def __init__(
        self,
        base_config,
        student_config,
        employer_config,
        school_config,
        scenario_config,
        type_config,
        data_config,
        llm_config,
    ):
        super().__init__()

        self.base_config = base_config
        self.student_config = student_config
        self.employer_config = employer_config
        self.school_config = school_config
        self.scenario_config = scenario_config
        self.type_config = type_config
        self.data_config = data_config
        self.llm_config = llm_config

        self.num_students = base_config["num_students"]
        self.num_schools = base_config["num_schools"]
        self.num_employers = base_config["num_employers"]

        random.seed(base_config["random_seed"])

        self.majors = ["CS", "Finance", "Mechanical", "Education"]
        self.major_market_heat = {
            "CS": 1.0,
            "Finance": 0.9,
            "Mechanical": 0.8,
            "Education": 0.7,
        }

        # 新增：学生专业选择时用到的专业薪资预期
        self.major_salary_expectation = {
            "CS": 0.95,
            "Finance": 0.85,
            "Mechanical": 0.75,
            "Education": 0.65,
        }

        self.students = []
        self.schools = []
        self.employers = []

        self.last_round_major_stats = {}
        self.metrics_history = []

        self.db_data = load_simulation_data()
        self.job_templates = self.db_data["jobs"]

        self._create_agents()

        # 新增：学生学习阶段用到的学校平均培养质量
        self.school_training_quality_avg = self._calculate_school_training_quality_avg()

    def _create_agents(self):
        # 1. 专业数据
        db_majors = self.db_data["majors"]
        if db_majors:
            self.majors = [m.major_name for m in db_majors]
            self.major_market_heat = {
                m.major_name: float(m.heat_init) for m in db_majors
            }

            # 如果数据库里有薪资预期字段，可替换成真实字段
            self.major_salary_expectation = {
                m.major_name: float(getattr(m, "salary_expectation", 0.7) or 0.7)
                for m in db_majors
            }

            self.major_code_to_name = {m.major_code: m.major_name for m in db_majors}
            self.major_name_to_code = {m.major_name: m.major_code for m in db_majors}
        else:
            self.major_code_to_name = {}
            self.major_name_to_code = {}

        # 2. 学校主体
        db_schools = self.db_data["schools"]
        for s in db_schools:
            school_type = s.school_type
            school_profile = SCHOOL_TYPE_PROFILES.get(
                school_type,
                random.choice(list(SCHOOL_TYPE_PROFILES.values()))
            )

            school = SchoolAgent(
                unique_id=f"school_{s.id}",
                model=self,
                name=s.school_name,
                major_capacity={m: 50 for m in self.majors},
                school_type=school_type,
                profile=school_profile,
            )
            self.schools.append(school)

        # 3. 企业主体
        db_employers = self.db_data["employers"]
        for e in db_employers:
            employer_type = e.employer_type
            employer_profile = EMPLOYER_TYPE_PROFILES.get(
                employer_type,
                random.choice(list(EMPLOYER_TYPE_PROFILES.values()))
            )

            # 保证企业画像里带有当前配置参数
            employer_profile = {
                **employer_profile,
                "major_preference_strength": self.employer_config.get(
                    "major_preference_strength",
                    employer_profile.get("major_preference_strength", 0.8),
                ),
                "skill_preference_strength": self.employer_config.get(
                    "skill_preference_strength",
                    employer_profile.get("skill_preference_strength", 0.9),
                ),
                "salary_elasticity": self.employer_config.get(
                    "salary_elasticity",
                    employer_profile.get("salary_elasticity", 0.05),
                ),
                "hire_threshold": self.employer_config.get(
                    "hire_threshold",
                    employer_profile.get("hire_threshold", 0.55),
                ),
                "cross_major_tolerance": self.employer_config.get(
                    "cross_major_tolerance",
                    employer_profile.get("cross_major_tolerance", 0.6),
                ),
            }

            employer = EmployerAgent(
                unique_id=f"employer_{e.id}",
                model=self,
                industry=e.industry,
                base_salary=float(e.base_salary),
                employer_type=employer_type,
                profile=employer_profile,
            )
            self.employers.append(employer)

        # 4. 学生主体
        db_students = self.db_data["students"]
        for s in db_students:
            student_type = s.student_type
            student_profile = STUDENT_TYPE_PROFILES.get(
                student_type,
                random.choice(list(STUDENT_TYPE_PROFILES.values()))
            )

            student_interest = s.interest_major
            if not self.majors:
                student_interest = "CS"
            elif student_interest not in self.majors:
                student_interest = random.choice(self.majors)

            student = StudentAgent(
                unique_id=f"student_{s.id}",
                model=self,
                ability=float(s.ability),
                interest=student_interest,
                expected_salary=float(s.expected_salary),
                student_type=student_type,
                profile=student_profile,
            )
            self.students.append(student)

        print("DEBUG majors =", self.majors)
        print("DEBUG students loaded =", len(self.students))
        print("DEBUG schools loaded =", len(self.schools))
        print("DEBUG employers loaded =", len(self.employers))

    def _calculate_school_training_quality_avg(self):
        if not self.schools:
            return self.school_config.get("training_quality", 0.7)

        qualities = []
        for school in self.schools:
            q = school.profile.get(
                "training_quality",
                self.school_config.get("training_quality", 0.7),
            )
            qualities.append(float(q))

        return sum(qualities) / len(qualities) if qualities else 0.7

    def step(self, step_idx: int):
        # 0. 重置本轮临时状态
        for student in self.students:
            if hasattr(student, "reset_round_state"):
                student.reset_round_state()

        # 1. 首轮选专业
        for student in self.students:
            if student.major is None:
                student.choose_major()

        # 2. 每轮开始时重新计算学校平均培养质量
        self.school_training_quality_avg = self._calculate_school_training_quality_avg()

        # 3. 学习能力演化
        for student in self.students:
            student.study()

        # 4. 只让未就业学生参与本轮岗位市场
        active_job_seekers = [s for s in self.students if not s.employed]

        if active_job_seekers:
            for employer in self.employers:
                employer.publish_jobs()

            for student in active_job_seekers:
                student.apply_jobs()

            for employer in self.employers:
                employer.hire()

            for student in active_job_seekers:
                student.choose_offer()
        else:
            for employer in self.employers:
                employer.open_jobs = []

        # 5. 企业调整招聘策略
        for employer in self.employers:
            employer.adjust_strategy()

        # 6. 学校反馈
        for school in self.schools:
            if hasattr(school, "adjust_major_capacity"):
                school.adjust_major_capacity()
            if hasattr(school, "adjust_training_quality"):
                school.adjust_training_quality()
            elif hasattr(school, "adjust_capacity"):
                school.adjust_capacity()

        # 7. 更新专业统计
        self.update_major_stats()

        # 8. 记录指标
        metrics = self.collect_metrics(step_idx)
        self.metrics_history.append(metrics)

    def collect_metrics(self, step_idx: int):
        total_students = len(self.students)

        # 存量口径：截至当前轮，已经就业的人
        employed_students = [s for s in self.students if s.employed]

        # 流量口径：本轮新就业的人
        newly_employed_students = [s for s in self.students if getattr(s, "just_matched_this_round", False)]

        # 本轮仍在找工作的学生
        active_job_seekers = [s for s in self.students if not s.employed]

        # 本轮岗位
        all_jobs = [job for e in self.employers for job in e.open_jobs]
        round_job_count = len(all_jobs)
        round_filled_jobs = sum(1 for j in all_jobs if j["filled"])
        round_vacancy_rate = (
            (round_job_count - round_filled_jobs) / round_job_count
            if round_job_count > 0 else 0.0
        )

        # 累计指标
        employment_rate = len(employed_students) / total_students if total_students else 0.0

        matching_count = sum(1 for s in employed_students if s.matched_job_major)
        matching_rate = matching_count / len(employed_students) if employed_students else 0.0

        cross_major_rate = (
            sum(1 for s in employed_students if not s.matched_job_major) / len(employed_students)
            if employed_students else 0.0
        )

        avg_salary = (
            sum(s.current_offer["salary"] for s in employed_students if s.current_offer) / len(employed_students)
            if employed_students else 0.0
        )

        avg_satisfaction = (
            sum(getattr(s, "satisfaction", 0.0) for s in employed_students) / len(employed_students)
            if employed_students else 0.0
        )

        # 本轮新增就业率
        round_new_employment_rate = (
            len(newly_employed_students) / total_students
            if total_students else 0.0
        )

        mismatch_index = self.calculate_mismatch_index()
        herding_index = self.calculate_herding_index()

        avg_hire_threshold = (
            sum(e.profile.get("hire_threshold", 0.55) for e in self.employers) / len(self.employers)
            if self.employers else 0.0
        )

        avg_cross_major_tolerance = (
            sum(e.profile.get("cross_major_tolerance", 0.6) for e in self.employers) / len(self.employers)
            if self.employers else 0.0
        )

        return {
            "step": step_idx,

            # 存量指标
            "employment_rate": employment_rate,
            "matching_rate": matching_rate,
            "cross_major_rate": cross_major_rate,
            "avg_salary": avg_salary,
            "avg_satisfaction": avg_satisfaction,

            # 流量指标
            "active_job_seekers": len(active_job_seekers),
            "round_job_count": round_job_count,
            "round_filled_jobs": round_filled_jobs,
            "round_vacancy_rate": round_vacancy_rate,
            "round_new_employment_rate": round_new_employment_rate,

            # 结构与机制指标
            "mismatch_index": mismatch_index,
            "herding_index": herding_index,
            "avg_hire_threshold": avg_hire_threshold,
            "avg_cross_major_tolerance": avg_cross_major_tolerance,
        }

    def calculate_mismatch_index(self):
        student_major_counter = Counter([s.major for s in self.students if s.major is not None])
        job_major_counter = Counter([j["major"] for e in self.employers for j in e.open_jobs])

        total_students = sum(student_major_counter.values())
        total_jobs = sum(job_major_counter.values())

        if total_students == 0 or total_jobs == 0:
            return 0.0

        mismatch = 0.0
        for major in self.majors:
            supply_share = student_major_counter.get(major, 0) / total_students
            demand_share = job_major_counter.get(major, 0) / total_jobs
            mismatch += abs(supply_share - demand_share)

        return mismatch

    def calculate_herding_index(self):
        student_major_counter = Counter([s.major for s in self.students if s.major is not None])
        if not student_major_counter or not self.students:
            return 0.0

        max_share = max(student_major_counter.values()) / len(self.students)
        avg_share = (sum(student_major_counter.values()) / len(student_major_counter)) / len(self.students)

        if avg_share == 0:
            return 0.0

        return max_share / avg_share

    def update_major_stats(self):
        stats = {}
        for major in self.majors:
            major_students = [s for s in self.students if s.major == major]
            employed_major_students = [s for s in major_students if s.current_offer is not None]

            stats[major] = {
                "student_count": len(major_students),
                "employment_rate": (
                    len(employed_major_students) / len(major_students)
                    if major_students else 0.0
                ),
            }

        self.last_round_major_stats = stats

    def run_model(self, steps=5):
        for i in range(steps):
            self.step(i)

        return self.metrics_history