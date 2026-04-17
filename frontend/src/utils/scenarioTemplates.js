export const scenarioTemplates = {
  baseline: {
    key: "baseline",
    name: "基准场景",
    description: "中性参数下的标准对照场景",
    overrides: {
      scenario_name: "baseline",
      scenario_config: {
        macro_economy: 1.0,
        policy_support: 0.5,
        industry_boom_factor: 1.0,
      },
      student_config: {
        interest_weight: 0.3,
        salary_weight: 0.2,
        market_signal_weight: 0.1,
        information_transparency: 0.8,
        cross_major_acceptance: 0.7,
      },
      employer_config: {
        hire_threshold: 0.55,
        major_preference_strength: 0.8,
        skill_preference_strength: 0.9,
        cross_major_tolerance: 0.6,
      },
      school_config: {
        capacity_adjust_speed: 0.1,
        employment_feedback_weight: 0.6,
        market_feedback_weight: 0.4,
        training_quality: 0.7,
      },
      type_config: {
        herd_strength: 0.3,
      },
    },
  },

  interest_oriented: {
    key: "interest_oriented",
    name: "兴趣导向增强",
    description: "学生更重兴趣，较少追逐市场热点与薪资",
    overrides: {
      scenario_name: "interest_oriented",
      student_config: {
        interest_weight: 0.5,
        salary_weight: 0.15,
        market_signal_weight: 0.05,
      },
    },
  },

  market_signal_oriented: {
    key: "market_signal_oriented",
    name: "市场信号导向增强",
    description: "学生更受热门专业和市场热度影响",
    overrides: {
      scenario_name: "market_signal_oriented",
      student_config: {
        interest_weight: 0.2,
        market_signal_weight: 0.3,
      },
      type_config: {
        herd_strength: 0.5,
      },
    },
  },

  low_information: {
    key: "low_information",
    name: "低信息透明度",
    description: "学生对真实市场信息感知不足",
    overrides: {
      scenario_name: "low_information",
      student_config: {
        information_transparency: 0.4,
      },
      type_config: {
        enable_information_delay: true,
        info_delay_steps: 2,
      },
    },
  },

  high_threshold: {
    key: "high_threshold",
    name: "高门槛招聘",
    description: "企业提高招聘门槛并强化专业偏好",
    overrides: {
      scenario_name: "high_threshold",
      employer_config: {
        hire_threshold: 0.75,
        major_preference_strength: 0.9,
      },
    },
  },

  relaxed_cross_major: {
    key: "relaxed_cross_major",
    name: "放宽跨专业招聘",
    description: "企业和学生两侧都更接受跨专业匹配",
    overrides: {
      scenario_name: "relaxed_cross_major",
      employer_config: {
        cross_major_tolerance: 0.8,
      },
      student_config: {
        cross_major_acceptance: 0.85,
      },
    },
  },

  fast_school_feedback: {
    key: "fast_school_feedback",
    name: "学校反馈较快",
    description: "学校更快根据市场和就业结果调整供给倾向",
    overrides: {
      scenario_name: "fast_school_feedback",
      school_config: {
        capacity_adjust_speed: 0.2,
        employment_feedback_weight: 0.7,
        market_feedback_weight: 0.5,
      },
      scenario_config: {
        school_feedback_lag: 2,
      },
    },
  },

  low_training_quality: {
    key: "low_training_quality",
    name: "低培养质量",
    description: "学校培养质量不足，能力错位更明显",
    overrides: {
      scenario_name: "low_training_quality",
      school_config: {
        training_quality: 0.5,
      },
    },
  },

  macro_downturn: {
    key: "macro_downturn",
    name: "宏观经济下行",
    description: "市场岗位总量收缩，招聘压力上升",
    overrides: {
      scenario_name: "macro_downturn",
      scenario_config: {
        macro_economy: 0.8,
        industry_boom_factor: 0.9,
      },
    },
  },

  ai_boom_jobs: {
    key: "ai_boom_jobs",
    name: "AI岗位景气上升",
    description: "数字/AI相关岗位景气增强，需求结构发生变化",
    overrides: {
      scenario_name: "ai_boom_jobs",
      scenario_config: {
        industry_boom_factor: 1.3,
        policy_support: 0.7,
        technology_change_rate: 0.35,
      },
    },
  },

  salary_oriented: {
    key: "salary_oriented",
    name: "薪资导向增强",
    description: "学生更重视薪资收益，降低兴趣和本地偏好权重。",
    overrides: {
      scenario_name: "salary_oriented",
      student_config: {
        salary_weight: 0.45,
        interest_weight: 0.2,
        region_weight: 0.02,
        reservation_utility: 0.65,
      },
    },
  },

  herding_enhanced: {
    key: "herding_enhanced",
    name: "从众效应增强",
    description: "社会影响与热门专业吸引增强，用于观察扎堆和结构错配。",
    overrides: {
      scenario_name: "herding_enhanced",
      student_config: {
        market_signal_weight: 0.3,
      },
      scenario_config: {
        market_heat_amplification: 1.4,
      },
      type_config: {
        enable_social_influence: true,
        herd_strength: 0.65,
        social_network_density: 0.45,
      },
    },
  },

  carryover_pressure: {
    key: "carryover_pressure",
    name: "未就业滞留压力",
    description: "开启跨轮未就业滞留，观察就业压力累积与再匹配表现。",
    overrides: {
      scenario_name: "carryover_pressure",
      student_config: {
        max_carryover_steps: 3,
        carryover_fraction: 0.8,
        carryover_skill_gain: 0.02,
        reservation_utility: 0.55,
      },
      scenario_config: {
        matching_rounds_per_step: 2,
      },
      type_config: {
        enable_unemployed_carryover: true,
      },
    },
  },

  regional_absorption_gap: {
    key: "regional_absorption_gap",
    name: "区域吸纳差异",
    description: "提高区域吸引力和迁移成本差异，观察本地就业与跨区域流动。",
    overrides: {
      scenario_name: "regional_absorption_gap",
      student_config: {
        region_weight: 0.2,
      },
      scenario_config: {
        city_attractiveness_gap: 0.8,
        migration_cost_weight: 0.35,
      },
      type_config: {
        enable_regional_preference: true,
      },
    },
  },

  multi_seed_baseline: {
    key: "multi_seed_baseline",
    name: "多种子稳健性基准",
    description: "用多个随机种子重复运行基准场景，降低单次随机波动影响。",
    overrides: {
      scenario_name: "multi_seed_baseline",
      base_config: {
        seed_runs: 5,
      },
    },
  },
};

export const scenarioTemplateList = Object.values(scenarioTemplates);
