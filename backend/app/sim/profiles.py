STUDENT_TYPE_PROFILES = {
    "employment_oriented": {
        "interest_weight": 0.2,
        "salary_weight": 0.35,
        "major_weight": 0.25,
        "market_signal_weight": 0.2,
        "cross_major_acceptance": 0.8,
        "information_transparency": 0.8,
    },
    "interest_oriented": {
        "interest_weight": 0.45,
        "salary_weight": 0.15,
        "major_weight": 0.25,
        "market_signal_weight": 0.15,
        "cross_major_acceptance": 0.5,
        "information_transparency": 0.7,
    },
    "prestige_oriented": {
        "interest_weight": 0.2,
        "salary_weight": 0.2,
        "major_weight": 0.4,
        "market_signal_weight": 0.2,
        "cross_major_acceptance": 0.6,
        "information_transparency": 0.75,
    },
    "trend_sensitive": {
        "interest_weight": 0.15,
        "salary_weight": 0.2,
        "major_weight": 0.2,
        "market_signal_weight": 0.45,
        "cross_major_acceptance": 0.75,
        "information_transparency": 0.9,
    },
}

SCHOOL_TYPE_PROFILES = {
    "research_university": {
        "training_quality": 0.9,
        "capacity_adjust_speed": 0.05,
        "employment_feedback_weight": 0.4,
        "market_feedback_weight": 0.3,
    },
    "applied_university": {
        "training_quality": 0.75,
        "capacity_adjust_speed": 0.1,
        "employment_feedback_weight": 0.6,
        "market_feedback_weight": 0.4,
    },
    "vocational_college": {
        "training_quality": 0.65,
        "capacity_adjust_speed": 0.15,
        "employment_feedback_weight": 0.75,
        "market_feedback_weight": 0.5,
    },
}

EMPLOYER_TYPE_PROFILES = {
    "tech_strict": {
    "major_preference_strength": 0.35,
    "skill_preference_strength": 0.45,
    "hire_threshold": 0.6,
    "cross_major_tolerance": 0.45,
    "salary_elasticity": 0.08,
    },
    "growth_firm": {
        "major_preference_strength": 0.2,
        "skill_preference_strength": 0.4,
        "hire_threshold": 0.45,
        "cross_major_tolerance": 0.8,
        "salary_elasticity": 0.1,
    },
    "traditional_firm": {
        "major_preference_strength": 0.4,
        "skill_preference_strength": 0.3,
        "hire_threshold": 0.55,
        "cross_major_tolerance": 0.5,
        "salary_elasticity": 0.05,
    },
    "cost_sensitive": {
        "major_preference_strength": 0.25,
        "skill_preference_strength": 0.3,
        "hire_threshold": 0.5,
        "cross_major_tolerance": 0.7,
        "salary_elasticity": 0.03,
    },
}