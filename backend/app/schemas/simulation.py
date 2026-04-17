from pydantic import BaseModel, Field
from typing import Optional




# 基础配置
class BaseConfig(BaseModel):
    num_students: int = 200
    num_schools: int = 3
    num_employers: int = 20
    num_majors: Optional[int] = None
    num_job_types: Optional[int] = None
    steps: int = 5
    random_seed: int = 42
    seed_runs: int = Field(default=1, ge=1)


# 学生配置
class StudentConfig(BaseModel):
    interest_weight: float = Field(default=0.3, ge=0.0)
    salary_weight: float = Field(default=0.2, ge=0.0)
    major_weight: float = Field(default=0.3, ge=0.0)
    city_weight: float = Field(default=0.1, ge=0.0)
    region_weight: float = Field(default=0.05, ge=0.0)
    market_signal_weight: float = Field(default=0.1, ge=0.0)
    cross_major_acceptance: float = Field(default=0.7, ge=0.0, le=1.0)
    information_transparency: float = Field(default=0.8, ge=0.0, le=1.0)
    max_applications_per_step: int = Field(default=3, ge=1)
    reservation_utility: float = Field(default=0.0, ge=0.0)
    max_carryover_steps: int = Field(default=1, ge=0)
    carryover_fraction: float = Field(default=1.0, ge=0.0, le=1.0)
    carryover_skill_gain: float = Field(default=0.01, ge=0.0)


# 企业配置
class EmployerConfig(BaseModel):
    major_preference_strength: float = Field(default=0.4, ge=0.0)
    skill_preference_strength: float = Field(default=0.4, ge=0.0)
    salary_elasticity: float = Field(default=0.05, ge=0.0)
    hire_threshold: float = Field(default=0.55, ge=0.0, le=1.0)
    cross_major_tolerance: float = Field(default=0.6, ge=0.0, le=1.0)
    threshold_relax_speed: float = Field(default=0.03, ge=0.0)
    tolerance_increase_speed: float = Field(default=0.03, ge=0.0)
    threshold_tighten_speed: float = Field(default=0.02, ge=0.0)
    tolerance_decrease_speed: float = Field(default=0.02, ge=0.0)


# 学校配置
class SchoolConfig(BaseModel):
    capacity_adjust_speed: float = Field(default=0.1, ge=0.0)
    employment_feedback_weight: float = Field(default=0.6, ge=0.0)
    market_feedback_weight: float = Field(default=0.4, ge=0.0)
    training_quality: float = Field(default=0.7, ge=0.0, le=1.0)
    adjustment_lag: int = Field(default=1, ge=1)
    resource_support: float = Field(default=0.03, ge=0.0)


# 场景配置
class ScenarioConfig(BaseModel):
    macro_economy: float = Field(default=1.0, ge=0.0)
    policy_support: float = Field(default=0.5, ge=0.0, le=1.0)
    industry_boom_factor: float = Field(default=1.0, ge=0.0)
    market_heat_amplification: float = Field(default=1.0, ge=0.0)
    city_attractiveness_gap: float = Field(default=0.5, ge=0.0)
    technology_change_rate: float = Field(default=0.0, ge=0.0)
    information_shock: float = Field(default=0.0)
    migration_cost_weight: float = Field(default=0.15, ge=0.0, le=1.0)
    matching_rounds_per_step: int = Field(default=1, ge=1)
    enterprise_feedback_lag: int = Field(default=2, ge=1)
    school_feedback_lag: int = Field(default=4, ge=1)
    satisfaction_threshold: float = Field(default=0.75, ge=0.0)


# 类型配置
class TypeConfig(BaseModel):
    # 控制模型结构复杂度
    enable_social_influence: bool = True
    enable_information_delay: bool = True
    enable_feedback_adjustment: bool = True
    enable_unemployed_carryover: bool = False
    enable_regional_preference: bool = True

    # 控制机制强度
    herd_strength: float = 0.3
    social_network_density: float = 0.2
    info_delay_steps: int = 1

    employment_oriented_ratio: Optional[float] = None
    interest_oriented_ratio: Optional[float] = None
    prestige_oriented_ratio: Optional[float] = None
    trend_sensitive_ratio: Optional[float] = None

    research_university_ratio: Optional[float] = None
    applied_university_ratio: Optional[float] = None
    vocational_college_ratio: Optional[float] = None

    tech_strict_ratio: Optional[float] = None
    growth_firm_ratio: Optional[float] = None
    traditional_firm_ratio: Optional[float] = None
    cost_sensitive_ratio: Optional[float] = None


# 数据配置
class DataConfig(BaseModel):
    data_mode: str = "database"
    use_mock_data: bool = True
    use_census_distribution: bool = True
    auto_generate_missing_data: bool = True
    student_data_path: str = ""
    school_data_path: str = ""
    employer_data_path: str = ""
    major_data_path: str = ""
    job_data_path: str = ""

    # 数据生成参数
    generate_if_missing: bool = True
    distribution_type: str = "normal"  # normal / uniform


# LLM配置
class LLMConfig(BaseModel):
    enabled: bool = False
    provider: str = "openai"
    model_name: str = "gpt-4o-mini"

    # 用途控制
    use_for_agent_decision: bool = False
    use_for_analysis: bool = True
    use_for_scenario_generation: bool = False
    use_for_profile_generation: bool = False
    use_for_result_explanation: bool = True
    use_for_report_generation: bool = True

    temperature: float = 0.7
    max_tokens: int = 1500


# 最终请求结构
class SimulationRequest(BaseModel):
    scenario_name: Optional[str] = "baseline"
    base_config: BaseConfig = BaseConfig()
    student_config: StudentConfig = StudentConfig()
    employer_config: EmployerConfig = EmployerConfig()
    school_config: SchoolConfig = SchoolConfig()
    scenario_config: ScenarioConfig = ScenarioConfig()

    type_config: TypeConfig = TypeConfig()
    data_config: DataConfig = DataConfig()
    llm_config: LLMConfig = LLMConfig()


    
    
