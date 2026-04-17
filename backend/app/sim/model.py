# backend/app/sim/model.py
# 调度仿真流程，维护主体容器，收集指标数据，提供运行信息接口
import random

from mesa import Model

from app.sim.model_init import (
    create_static_agents,
    refresh_students_for_new_cohort,
    calculate_school_training_quality_avg,
)
from app.sim.model_metrics import collect_metrics, update_major_stats
from app.sim.model_structure import update_structure_analysis
from app.sim.model_market import update_major_market_heat

class TalentMarketModel(Model):
    """
    人才市场 ABM 主模型。
 
    """

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

        # -------------------------
        # 1. 配置保存
        # -------------------------
        self.base_config = base_config
        self.student_config = student_config
        self.employer_config = employer_config
        self.school_config = school_config
        self.scenario_config = scenario_config
        self.type_config = type_config
        self.data_config = data_config
        self.llm_config = llm_config

        # 仿真规模参数
        self.num_students = base_config["num_students"]
        self.num_schools = base_config["num_schools"]
        self.num_employers = base_config["num_employers"]

        # 反馈时滞参数
        self.enterprise_feedback_lag = int(
            self.scenario_config.get("enterprise_feedback_lag", 2)
        )
        self.school_feedback_lag = int(
            self.scenario_config.get("school_feedback_lag", 4)
        )

        # 低满意度阈值
        self.satisfaction_threshold = float(
            self.scenario_config.get("satisfaction_threshold", 0.75)
        )

        # 随机种子
        random.seed(base_config["random_seed"])

        # -------------------------
        # 2. 默认专业与市场初始化
        # -------------------------
        self.majors = ["CS", "Finance", "Mechanical", "Education"]

        self.major_market_heat = {
            "CS": 1.0,
            "Finance": 0.9,
            "Mechanical": 0.8,
            "Education": 0.7,
        }

        self.major_salary_expectation = {
            "CS": 0.95,
            "Finance": 0.85,
            "Mechanical": 0.75,
            "Education": 0.65,
        }
        self.major_mobility = {}
        self.major_policy_support_weight = {}
        self.major_industry_match = {}

        # -------------------------
        # 3. 主体容器
        # -------------------------
        self.students = []
        self.schools = []
        self.employers = []

        # -------------------------
        # 4. 运行过程缓存
        # -------------------------
        self.last_round_major_stats = {}
        self.metrics_history = []
        self.previous_major_distribution = {}
        self.major_market_heat_history = []
        self.latest_major_market_signals = {}

        # 学校专业调整偏置
        self.major_school_adjustment_bias = {}

        # 结构分析缓存
        self.latest_structure_analysis = {}

        # 数据缓存
        self.db_data = {}
        self.job_templates = []

        # 单轮过程指标缓存
        self.round_application_count = 0
        self.round_offer_count = 0
        self.round_accepted_offer_count = 0
        self.round_rejected_offer_count = 0
        self.round_carryover_student_count = 0
        self.round_new_cohort_student_count = 0

        # 跨 step 累计结果缓存，用于真正意义上的“累计指标”
        self.cumulative_seen_student_ids = set()
        self.cumulative_employed_student_ids = set()
        self.cumulative_matching_count = 0
        self.cumulative_cross_major_count = 0
        self.cumulative_low_satisfaction_count = 0
        self.cumulative_same_region_count = 0
        self.cumulative_salary_sum = 0.0
        self.cumulative_satisfaction_sum = 0.0

        # -------------------------
        # 5. 创建主体
        # -------------------------
        create_static_agents(self)
        self.major_market_heat_history.append(dict(self.major_market_heat))

        # -------------------------
        # 6. 学校平均培养质量
        # -------------------------
        self.school_training_quality_avg = calculate_school_training_quality_avg(self)

    def step(self, step_idx: int):
        """
        单轮仿真主流程。
        """
        self.round_application_count = 0
        self.round_offer_count = 0
        self.round_accepted_offer_count = 0
        self.round_rejected_offer_count = 0
        self.round_carryover_student_count = 0
        self.round_new_cohort_student_count = 0
        
        # 1. 重置学生本轮状态
        refresh_students_for_new_cohort(self, step_idx)
        # 2. 首轮选专业
        # 当前版本中，新一届学生的专业通常在 cohort 生成阶段已确定；
        # 若某些学生未分配成功，则在此兜底调用 choose_major()
        for student in self.students:
            if student.major is None:
                student.choose_major()

        # 3. 更新学校平均培养质量
        self.school_training_quality_avg = calculate_school_training_quality_avg(self)

        # 4. 学生学习
        for student in self.students:
            student.study()

        # 5. 未就业学生进入岗位市场
        active_job_seekers = [s for s in self.students if not s.employed]

        if active_job_seekers:
            # 企业发布岗位
            for employer in self.employers:
                employer.publish_jobs()

            matching_rounds = int(self.scenario_config.get("matching_rounds_per_step", 1))
            for _round_idx in range(max(1, matching_rounds)):
                active_job_seekers = [s for s in self.students if not s.employed]
                if not active_job_seekers:
                    break

                for student in active_job_seekers:
                    student.apply_jobs()

                offers_before = self.round_offer_count
                for employer in self.employers:
                    employer.hire()

                for student in active_job_seekers:
                    student.choose_offer()

                if self.round_offer_count == offers_before:
                    break
        else:
            # 若无活跃求职者，则清空本轮岗位
            for employer in self.employers:
                employer.open_jobs = []

        # 6. 企业反馈（短时滞）
        if (
            self.type_config.get("enable_feedback_adjustment", True)
            and (step_idx + 1) % self.enterprise_feedback_lag == 0
        ):
            for employer in self.employers:
                employer.adjust_strategy()

        # 6. 更新市场热度（需求侧向供给侧传导）
        update_major_market_heat(self)
        self.major_market_heat_history.append(dict(self.major_market_heat))

        # 7. 更新专业统计
        update_major_stats(self)

        # 8. 学校记录反馈
        for school in self.schools:
            if hasattr(school, "record_feedback"):
                school.record_feedback()

        # 9. 学校反馈（长时滞）
        if (
            self.type_config.get("enable_feedback_adjustment", True)
            and (step_idx + 1) % self.school_feedback_lag == 0
        ):
            # 本轮重新记录学校对各专业的调整偏置
            self.major_school_adjustment_bias = {}

            for school in self.schools:
                if hasattr(school, "adjust_major_capacity"):
                    school.adjust_major_capacity()
                if hasattr(school, "adjust_training_quality"):
                    school.adjust_training_quality()
                elif hasattr(school, "adjust_capacity"):
                    school.adjust_capacity()

        # 10. 收集本轮指标
        metrics = collect_metrics(self, step_idx)
        self.metrics_history.append(metrics)

        # 11. 更新结构分析缓存
        update_structure_analysis(self)

    def get_runtime_info(self):
        """
        返回本次仿真实际参与规模与运行模式。
        """
        return {
            "student_count": len(self.students),
            "school_count": len(self.schools),
            "employer_count": len(self.employers),
            "major_count": len(self.majors),
            "data_mode": self.data_config.get("data_mode", "database"),
        }

    def run_model(self, steps=5):
        """
        运行多轮仿真。
        """
        for i in range(steps):
            self.step(i)

        return self.metrics_history
