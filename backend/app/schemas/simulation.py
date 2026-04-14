from pydantic import BaseModel


# ================= 基础配置 =================
class BaseConfig(BaseModel):
    num_students: int = 200
    num_schools: int = 3
    num_employers: int = 20
    steps: int = 5
    random_seed: int = 42


# ================= 学生配置 =================
class StudentConfig(BaseModel):
    interest_weight: float = 0.3
    salary_weight: float = 0.2
    major_weight: float = 0.3
    city_weight: float = 0.1
    market_signal_weight: float = 0.1
    cross_major_acceptance: float = 0.7
    information_transparency: float = 0.8


# ================= 企业配置 =================
class EmployerConfig(BaseModel):
    major_preference_strength: float = 0.4
    skill_preference_strength: float = 0.4
    salary_elasticity: float = 0.05
    hire_threshold: float = 0.55
    cross_major_tolerance: float = 0.6


# ================= 学校配置 =================
class SchoolConfig(BaseModel):
    capacity_adjust_speed: float = 0.1
    employment_feedback_weight: float = 0.6
    market_feedback_weight: float = 0.4
    training_quality: float = 0.7


# ================= 场景配置 =================
class ScenarioConfig(BaseModel):
    macro_economy: float = 1.0
    policy_support: float = 0.5
    industry_boom_factor: float = 1.0


# ================= ⭐ 新增：类型配置 =================
class TypeConfig(BaseModel):
    # 控制模型结构复杂度
    enable_social_influence: bool = True
    enable_information_delay: bool = True
    enable_feedback_adjustment: bool = True

    # 控制机制强度
    herd_strength: float = 0.3
    social_network_density: float = 0.2
    info_delay_steps: int = 1


# ================= ⭐ 新增：数据配置 =================
class DataConfig(BaseModel):
    use_mock_data: bool = True
    student_data_path: str = ""
    school_data_path: str = ""
    employer_data_path: str = ""

    # 数据生成参数
    generate_if_missing: bool = True
    distribution_type: str = "normal"  # normal / uniform


# ================= ⭐ 新增：LLM配置 =================
class LLMConfig(BaseModel):
    enabled: bool = False
    provider: str = "openai"
    model_name: str = "gpt-4o-mini"

    # 用途控制
    use_for_agent_decision: bool = False
    use_for_analysis: bool = True
    use_for_scenario_generation: bool = False

    temperature: float = 0.7


# ================= ⭐ 最终请求结构 =================
class SimulationRequest(BaseModel):
    base_config: BaseConfig = BaseConfig()
    student_config: StudentConfig = StudentConfig()
    employer_config: EmployerConfig = EmployerConfig()
    school_config: SchoolConfig = SchoolConfig()
    scenario_config: ScenarioConfig = ScenarioConfig()

    # 新增三大配置
    type_config: TypeConfig = TypeConfig()
    data_config: DataConfig = DataConfig()
    llm_config: LLMConfig = LLMConfig()