// 每个参数面板中显示哪些字段
// 后续如果要调整字段顺序、隐藏某些字段，只需要改这里。

export const baseConfigFields = [
  "num_students",
  "num_schools",
  "num_employers",
  "steps",
  "random_seed",
];

export const studentConfigFields = [
  "interest_weight",
  "salary_weight",
  "major_weight",
  "market_signal_weight",
  "cross_major_acceptance",
  "information_transparency",
  "max_applications_per_step",
];

export const schoolConfigFields = [
  "training_quality",
  "capacity_adjust_speed",
  "employment_feedback_weight",
  "market_feedback_weight",
  "adjustment_lag",
  "resource_support",
];

export const employerConfigFields = [
  "major_preference_strength",
  "skill_preference_strength",
  "hire_threshold",
  "cross_major_tolerance",
  "salary_elasticity",
  "threshold_relax_speed",
  "tolerance_increase_speed",
];

export const scenarioConfigFields = [
  "macro_economy",
  "policy_support",
  "industry_boom_factor",
];

export const advancedScenarioFields = [
  "market_heat_amplification",
  "city_attractiveness_gap",
  "technology_change_rate",
  "information_shock",
  "enterprise_feedback_lag",
  "school_feedback_lag",
];

export const dataConfigFields = [
  "data_mode",
  "use_census_distribution",
  "auto_generate_missing_data",
  "student_data_path",
  "school_data_path",
  "employer_data_path",
];

export const llmConfigFields = [
  "enabled",
  "use_for_scenario_generation",
  "use_for_result_explanation",
  "use_for_report_generation",
  "model_name",
  "temperature",
  "max_tokens",
];