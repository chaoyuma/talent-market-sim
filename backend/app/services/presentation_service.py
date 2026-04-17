""" 
用于将实验结果中的英文字段转换为中文展示
构建适合LLM报告的参数结构。
"""
from __future__ import annotations

from copy import deepcopy


TOP_LEVEL_LABELS = {
    "message": "消息",
    "experiment_id": "实验ID",
    "scenario_name": "场景名称",
    "params": "参数配置",
    "results": "逐轮结果",
    "summary": "汇总结果",
    "structure_analysis": "结构分析",
    "actual_runtime": "实际运行规模",
    "multi_seed": "多随机种子",
    "seed_results": "单种子结果",
}

PARAM_GROUP_LABELS = {
    "scenario_name": "场景名称",
    "base_config": "基础配置",
    "student_config": "学生配置",
    "employer_config": "企业配置",
    "school_config": "学校配置",
    "scenario_config": "场景机制配置",
    "type_config": "机制开关配置",
    "data_config": "数据配置",
    "llm_config": "大模型配置",
}

FIELD_LABELS = {
    "base_config": {
        "num_students": "学生数量",
        "num_schools": "学校数量",
        "num_employers": "企业数量",
        "num_majors": "专业数量",
        "num_job_types": "岗位类型数量",
        "steps": "仿真轮次",
        "random_seed": "随机种子",
        "seed_runs": "随机种子重复次数",
    },
    "student_config": {
        "interest_weight": "兴趣权重",
        "salary_weight": "薪资权重",
        "major_weight": "专业匹配权重",
        "city_weight": "城市权重",
        "region_weight": "地区权重",
        "market_signal_weight": "市场信号权重",
        "cross_major_acceptance": "学生跨专业接受度",
        "information_transparency": "信息透明度",
        "max_applications_per_step": "每轮最大投递数",
        "reservation_utility": "最低接受效用阈值",
        "max_carryover_steps": "最长滞留轮次",
        "carryover_fraction": "滞留保留比例",
        "carryover_skill_gain": "滞留技能提升",
    },
    "employer_config": {
        "major_preference_strength": "企业专业偏好强度",
        "skill_preference_strength": "企业技能偏好强度",
        "salary_elasticity": "薪资调整弹性",
        "hire_threshold": "招聘阈值",
        "cross_major_tolerance": "企业跨专业容忍度",
        "threshold_relax_speed": "阈值放宽速度",
        "tolerance_increase_speed": "跨专业容忍提升速度",
        "threshold_tighten_speed": "阈值收紧速度",
        "tolerance_decrease_speed": "跨专业容忍回调速度",
    },
    "school_config": {
        "capacity_adjust_speed": "学校容量调整速度",
        "employment_feedback_weight": "就业反馈权重",
        "market_feedback_weight": "市场反馈权重",
        "training_quality": "培养质量",
        "adjustment_lag": "调整滞后",
        "resource_support": "资源支持强度",
    },
    "scenario_config": {
        "macro_economy": "宏观经济景气度",
        "policy_support": "政策支持强度",
        "industry_boom_factor": "行业景气因子",
        "market_heat_amplification": "市场热度放大系数",
        "city_attractiveness_gap": "城市吸引力差异",
        "technology_change_rate": "技术变化速度",
        "information_shock": "信息冲击强度",
        "migration_cost_weight": "迁移成本权重",
        "matching_rounds_per_step": "每轮撮合轮数",
        "enterprise_feedback_lag": "企业反馈时滞",
        "school_feedback_lag": "学校反馈时滞",
        "satisfaction_threshold": "低满意度阈值",
    },
    "type_config": {
        "enable_social_influence": "启用社会影响",
        "enable_information_delay": "启用信息延迟",
        "enable_feedback_adjustment": "启用反馈调节",
        "enable_unemployed_carryover": "启用未就业滞留",
        "enable_regional_preference": "启用地区偏好",
        "herd_strength": "扎堆强度",
        "social_network_density": "社交网络密度",
        "info_delay_steps": "信息延迟步数",
        "employment_oriented_ratio": "就业导向学生占比",
        "interest_oriented_ratio": "兴趣导向学生占比",
        "prestige_oriented_ratio": "声望导向学生占比",
        "trend_sensitive_ratio": "趋势敏感学生占比",
        "research_university_ratio": "研究型大学占比",
        "applied_university_ratio": "应用型大学占比",
        "vocational_college_ratio": "职业院校占比",
        "tech_strict_ratio": "技术严格企业占比",
        "growth_firm_ratio": "成长型企业占比",
        "traditional_firm_ratio": "传统企业占比",
        "cost_sensitive_ratio": "成本敏感企业占比",
    },
    "data_config": {
        "data_mode": "数据模式",
        "use_mock_data": "使用模拟数据",
        "use_census_distribution": "使用分布抽样",
        "auto_generate_missing_data": "自动补齐缺失数据",
        "student_data_path": "学生数据路径",
        "school_data_path": "学校数据路径",
        "employer_data_path": "企业数据路径",
        "major_data_path": "专业数据路径",
        "job_data_path": "岗位数据路径",
        "generate_if_missing": "自动生成缺失数据",
        "distribution_type": "分布类型",
    },
    "llm_config": {
        "enabled": "启用大模型能力",
        "provider": "模型服务商",
        "model_name": "模型名称",
        "use_for_agent_decision": "用于主体决策",
        "use_for_analysis": "用于结果分析",
        "use_for_scenario_generation": "用于场景生成",
        "use_for_profile_generation": "用于画像生成",
        "use_for_result_explanation": "用于结果解释",
        "use_for_report_generation": "用于报告生成",
        "temperature": "温度参数",
        "max_tokens": "最大输出长度",
    },
    "experiment_metrics": {
        "step": "轮次",
        "student_count": "学生数",
        "school_count": "学校数",
        "employer_count": "企业数",
        "employment_rate": "累计就业率",
        "matching_rate": "累计对口率",
        "cross_major_rate": "累计跨专业率",
        "avg_salary": "累计平均薪资",
        "avg_satisfaction": "累计平均满意度",
        "low_satisfaction_employment_rate": "累计低满意就业率",
        "same_region_employment_rate": "累计同区域就业率",
        "carryover_student_count": "滞留求职人数",
        "new_cohort_student_count": "本轮新生人数",
        "new_cohort_employment_rate": "本轮新生就业率",
        "carryover_employment_rate": "本轮滞留就业率",
        "carryover_pool_share": "滞留池占比",
        "avg_carryover_rounds": "平均滞留轮次",
        "active_job_seekers": "活跃求职人数",
        "round_job_count": "本轮岗位数",
        "round_filled_jobs": "本轮已填岗位数",
        "round_vacancy_rate": "本轮空缺率",
        "round_new_employment_rate": "本轮新增就业率",
        "round_application_count": "本轮申请数",
        "round_offer_count": "本轮Offer数",
        "round_accepted_offer_count": "本轮Offer接受数",
        "round_rejected_offer_count": "本轮Offer拒绝数",
        "avg_applications_per_job": "岗位竞争度",
        "avg_offers_per_student": "人均Offer数",
        "mismatch_index": "结构错配指数",
        "herding_index": "扎堆指数",
        "avg_hire_threshold": "平均招聘阈值",
        "avg_cross_major_tolerance": "平均跨专业容忍度",
        "avg_training_quality": "平均培养质量",
    },
    "experiment_summary": {
        "final_employment_rate": "最终累计就业率",
        "final_matching_rate": "最终累计对口率",
        "final_cross_major_rate": "最终累计跨专业率",
        "final_avg_salary": "最终累计平均薪资",
        "final_avg_satisfaction": "最终累计平均满意度",
        "final_low_satisfaction_employment_rate": "最终累计低满意就业率",
        "final_same_region_employment_rate": "最终累计同区域就业率",
        "final_carryover_student_count": "最终滞留求职人数",
        "final_new_cohort_student_count": "最终本轮新生人数",
        "final_new_cohort_employment_rate": "最终本轮新生就业率",
        "final_carryover_employment_rate": "最终本轮滞留就业率",
        "final_carryover_pool_share": "最终滞留池占比",
        "final_avg_carryover_rounds": "最终平均滞留轮次",
        "final_active_job_seekers": "最终活跃求职人数",
        "final_round_job_count": "最终本轮岗位数",
        "final_round_filled_jobs": "最终本轮已填岗位数",
        "final_round_vacancy_rate": "最终本轮空缺率",
        "final_round_new_employment_rate": "最终本轮新增就业率",
        "final_round_application_count": "最终本轮申请数",
        "final_round_offer_count": "最终本轮Offer数",
        "final_round_accepted_offer_count": "最终本轮Offer接受数",
        "final_round_rejected_offer_count": "最终本轮Offer拒绝数",
        "final_avg_applications_per_job": "最终岗位竞争度",
        "final_avg_offers_per_student": "最终人均Offer数",
        "final_mismatch_index": "最终结构错配指数",
        "final_herding_index": "最终扎堆指数",
        "final_avg_hire_threshold": "最终平均招聘阈值",
        "final_avg_cross_major_tolerance": "最终平均跨专业容忍度",
        "final_avg_training_quality": "最终平均培养质量",
    },
    "actual_runtime": {
        "student_count": "学生数",
        "school_count": "学校数",
        "employer_count": "企业数",
        "major_count": "专业数",
        "data_mode": "数据模式",
        "seed_runs": "随机种子重复次数",
        "aggregation": "聚合方式",
    },
}

STRUCTURE_LABELS = {
    "major_supply_demand_gap": "专业供需缺口",
    "major_school_adjustment_bias": "学校专业调整偏置",
    "major_student_distribution": "专业学生分布",
    "major_job_distribution": "专业岗位分布",
    "industry_job_distribution": "行业岗位分布",
    "major_market_signals": "专业市场信号",
    "major_outcomes": "专业结果表现",
    "student_type_outcomes": "学生类型结果",
    "employer_type_metrics": "企业类型指标",
    "school_type_metrics": "学校类型指标",
    "regional_flow_metrics": "区域流动指标",
}

STRUCTURE_ROW_LABELS = {
    "major_supply_demand_gap": {
        "major": "专业",
        "student_count": "学生数",
        "job_count": "岗位数",
        "student_share": "学生占比",
        "job_share": "岗位占比",
        "gap": "供需差值",
    },
    "major_school_adjustment_bias": {
        "major": "专业",
        "school_adjustment_bias": "学校调整偏置",
    },
    "major_student_distribution": {
        "major": "专业",
        "count": "数量",
        "share": "占比",
    },
    "major_job_distribution": {
        "major": "专业",
        "count": "数量",
        "share": "占比",
    },
    "industry_job_distribution": {
        "industry": "行业",
        "count": "数量",
        "share": "占比",
    },
    "major_market_signals": {
        "major": "专业",
        "market_heat": "市场热度",
        "perceived_heat": "感知热度",
        "job_count": "岗位数",
        "filled_count": "已填岗位数",
        "vacancy_rate": "空缺率",
        "avg_salary": "平均薪资",
        "salary_signal": "薪资信号",
    },
    "major_outcomes": {
        "major": "专业",
        "student_count": "学生数",
        "employment_rate": "就业率",
        "avg_salary": "平均薪资",
        "avg_satisfaction": "平均满意度",
    },
    "student_type_outcomes": {
        "student_type": "学生类型",
        "student_count": "学生数",
        "employment_rate": "就业率",
        "avg_salary": "平均薪资",
        "avg_satisfaction": "平均满意度",
    },
    "employer_type_metrics": {
        "employer_type": "企业类型",
        "employer_count": "企业数",
        "job_count": "岗位数",
        "vacancy_rate": "空缺率",
        "avg_hire_threshold": "平均招聘阈值",
        "avg_cross_major_tolerance": "平均跨专业容忍度",
    },
    "school_type_metrics": {
        "school_type": "学校类型",
        "school_count": "学校数",
        "avg_training_quality": "平均培养质量",
        "total_capacity": "总容量",
    },
    "regional_flow_rows": {
        "region": "区域",
        "student_count": "学生数",
        "job_count": "岗位数",
        "employed_job_count": "就业岗位数",
        "student_job_gap": "学生岗位缺口",
    },
}


def display_name(label: str, key: str) -> str:
    # 生成名称格式
    # 例如：
    # label='学生数量', key='num_students'
    # => 学生数量（num_students）
    return f"{label}（{key}）" if label and label != key else key


def get_field_label(table_name: str, key: str) -> str:
    # 获取黄中文
    return FIELD_LABELS.get(table_name, {}).get(key, key)


def localize_flat_object(table_name: str, obj: dict | None) -> dict:
    # 中文叠加
    obj = obj or {}
    return {
        display_name(get_field_label(table_name, key), key): value
        for key, value in obj.items()
    }


def localize_params(params: dict | None) -> dict:
    # 翻译config参数
    params = params or {}
    output = {}
    for key, value in params.items():
        group_label = PARAM_GROUP_LABELS.get(key, key)
        display_key = display_name(group_label, key)
        if isinstance(value, dict):
            output[display_key] = localize_flat_object(key, value)
        else:
            output[display_key] = value
    return output


def localize_structure_analysis(structure_analysis: dict | None) -> dict:
    # 结构分析中部分字段是列表，需要特殊处理成表格形式展示
    structure_analysis = structure_analysis or {}
    localized = {}
    for section_key, value in structure_analysis.items():
        section_label = STRUCTURE_LABELS.get(section_key, section_key)
        display_section = display_name(section_label, section_key)
        if section_key == "regional_flow_metrics" and isinstance(value, dict):
            localized[display_section] = {
                display_name("区域明细", "rows"): [
                    {
                        display_name(
                            STRUCTURE_ROW_LABELS["regional_flow_rows"].get(item_key, item_key),
                            item_key,
                        ): item_value
                        for item_key, item_value in row.items()
                    }
                    for row in value.get("rows", [])
                ],
                display_name("同区域就业率", "same_region_employment_rate"): value.get(
                    "same_region_employment_rate", 0.0
                ),
            }
            continue

        if isinstance(value, list):
            row_labels = STRUCTURE_ROW_LABELS.get(section_key, {})
            localized[display_section] = [
                {
                    display_name(row_labels.get(item_key, item_key), item_key): item_value
                    for item_key, item_value in row.items()
                }
                for row in value
            ]
        else:
            localized[display_section] = value
    return localized


def localize_result_payload(payload: dict | None) -> dict:
    # 翻译payload
    payload = deepcopy(payload or {})
    localized = {}
    for key, value in payload.items():
        display_key = display_name(TOP_LEVEL_LABELS.get(key, key), key)
        if key == "params":
            localized[display_key] = localize_params(value)
        elif key == "results":
            localized[display_key] = [
                localize_flat_object("experiment_metrics", row)
                for row in value or []
            ]
        elif key == "summary":
            localized[display_key] = localize_flat_object("experiment_summary", value)
        elif key == "actual_runtime":
            localized[display_key] = localize_flat_object("actual_runtime", value)
        elif key == "structure_analysis":
            localized[display_key] = localize_structure_analysis(value)
        else:
            localized[display_key] = value
    return localized


def build_explanation_ready_payload(payload: dict) -> dict:
    # 构建llm报告的参数
    params = payload.get("params", {})
    base_config = params.get("base_config", {})
    student_config = params.get("student_config", {})
    employer_config = params.get("employer_config", {})
    scenario_config = params.get("scenario_config", {})
    type_config = params.get("type_config", {})
    summary = payload.get("summary", {})

    key_parameter_summary = {
        "样本规模": {
            "学生数量": base_config.get("num_students"),
            "学校数量": base_config.get("num_schools"),
            "企业数量": base_config.get("num_employers"),
            "仿真轮次": base_config.get("steps"),
            "随机种子重复次数": base_config.get("seed_runs", 1),
        },
        "学生机制": {
            "兴趣权重": student_config.get("interest_weight"),
            "薪资权重": student_config.get("salary_weight"),
            "市场信号权重": student_config.get("market_signal_weight"),
            "信息透明度": student_config.get("information_transparency"),
            "最低接受效用阈值": student_config.get("reservation_utility"),
        },
        "企业机制": {
            "招聘阈值": employer_config.get("hire_threshold"),
            "企业跨专业容忍度": employer_config.get("cross_major_tolerance"),
            "企业专业偏好强度": employer_config.get("major_preference_strength"),
            "企业技能偏好强度": employer_config.get("skill_preference_strength"),
        },
        "场景机制": {
            "宏观经济景气度": scenario_config.get("macro_economy"),
            "政策支持强度": scenario_config.get("policy_support"),
            "行业景气因子": scenario_config.get("industry_boom_factor"),
            "每轮撮合轮数": scenario_config.get("matching_rounds_per_step"),
            "启用未就业滞留": type_config.get("enable_unemployed_carryover"),
        },
    }

    return {
        "实验ID": payload.get("experiment_id"),
        "场景名称": payload.get("scenario_name"),
        "实际运行规模": localize_flat_object("actual_runtime", payload.get("actual_runtime", {})),
        "关键参数摘要": key_parameter_summary,
        "汇总结果": localize_flat_object("experiment_summary", summary),
        "最后一轮结果": localize_flat_object(
            "experiment_metrics",
            (payload.get("results") or [{}])[-1],
        ),
        "结构分析": localize_structure_analysis(payload.get("structure_analysis", {})),
        "多随机种子": payload.get("multi_seed", {}),
    }
