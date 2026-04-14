from mesa import Model
from app.sim.agents.student_agent import StudentAgent
from app.sim.agents.school_agent import SchoolAgent
from app.sim.agents.employer_agent import EmployerAgent
from app.services.data_manage_service import load_simulation_data

import random
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

        self.students = []
        self.schools = []
        self.employers = []

        self.last_round_major_stats = {}
        self.metrics_history = []

        self.db_data = load_simulation_data()
        self.job_templates = self.db_data["jobs"]
        self._create_agents()

    def _create_agents(self):
        # 1. majors 从数据库读取
        db_majors = self.db_data["majors"]
        if db_majors:
            self.majors = [m.major_name for m in db_majors]
            self.major_market_heat = {
                m.major_name: float(m.heat_init) for m in db_majors
            }
            self.major_code_to_name = {m.major_code: m.major_name for m in db_majors}
            self.major_name_to_code = {m.major_name: m.major_code for m in db_majors}
        else:
            self.major_code_to_name = {}
            self.major_name_to_code = {}
        # 2. schools 从数据库读取
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

        # 3. employers 从数据库读取
        db_employers = self.db_data["employers"]
        for e in db_employers:
            employer_type = e.employer_type
            employer_profile = EMPLOYER_TYPE_PROFILES.get(
                employer_type,
                random.choice(list(EMPLOYER_TYPE_PROFILES.values()))
            )

            employer = EmployerAgent(
                unique_id=f"employer_{e.id}",
                model=self,
                industry=e.industry,
                base_salary=float(e.base_salary),
                employer_type=employer_type,
                profile=employer_profile,
            )
            self.employers.append(employer)

        # 4. students 从数据库读取
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

    def step(self, step_idx):
        for student in self.students:
            if student.major is None:
                student.choose_major()
            student.study()

        for employer in self.employers:
            employer.publish_jobs()

        for student in self.students:
            student.apply_jobs()

        for employer in self.employers:
            employer.hire()

        metrics = self.collect_metrics(step_idx)
        self.metrics_history.append(metrics)

        self.update_major_stats()

        for school in self.schools:
            school.adjust_capacity()

        for employer in self.employers:
            employer.adjust_strategy()

        for student in self.students:
            student.employed = False
            student.current_offer = None
            student.matched_job_major = False

    def collect_metrics(self, step_idx):
        total_students = len(self.students)
        employed_students_list = [s for s in self.students if s.current_offer is not None]
        employed_students = len(employed_students_list)
        matched_students = sum(1 for s in employed_students_list if s.matched_job_major)
        cross_major_students = employed_students - matched_students

        all_jobs = [job for e in self.employers for job in e.open_jobs]
        total_jobs = len(all_jobs)
        vacant_jobs = sum(1 for job in all_jobs if not job["filled"])
        filled_jobs = total_jobs - vacant_jobs

        avg_salary = (
            sum(s.current_offer["salary"] for s in employed_students_list) / employed_students
            if employed_students else 0
        )

        return {
            "step": step_idx,
            "employment_rate": employed_students / total_students if total_students else 0,
            "matching_rate": matched_students / employed_students if employed_students else 0,
            "cross_major_rate": cross_major_students / employed_students if employed_students else 0,
            "vacancy_rate": vacant_jobs / total_jobs if total_jobs else 0,
            "filled_jobs": filled_jobs,
            "avg_salary": avg_salary,
        }

    def update_major_stats(self):
        stats = {}
        for major in self.majors:
            major_students = [s for s in self.students if s.major == major]
            employed_major_students = [s for s in major_students if s.current_offer is not None]

            stats[major] = {
                "student_count": len(major_students),
                "employment_rate": len(employed_major_students) / len(major_students) if major_students else 0
            }

        self.last_round_major_stats = stats

    def run_model(self, steps=5):
        for i in range(steps):
            self.step(i)

        return self.metrics_history