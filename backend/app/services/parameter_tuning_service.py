# backend/app/services/parameter_tuning_service.py

import json
from typing import Any

import requests

from app.core.config import settings

import re


def extract_json_block(text: str) -> str:
    """
    从模型返回文本中提取 JSON 主体。
    兼容：
    1. 纯 JSON
    2. ```json ... ``` 代码块
    3. 前后带解释文字
    """
    if not text:
        return ""

    text = text.strip()

    # 情况1：```json ... ```
    code_block_match = re.search(r"```json\s*(.*?)\s*```", text, re.S | re.I)
    if code_block_match:
        return code_block_match.group(1).strip()

    # 情况2：``` ... ```
    generic_block_match = re.search(r"```\s*(.*?)\s*```", text, re.S)
    if generic_block_match:
        return generic_block_match.group(1).strip()

    # 情况3：截取最外层 JSON 对象
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1].strip()

    return text


def try_parse_llm_json(text: str) -> dict | None:
    """
    尝试把大模型输出解析成 JSON。
    """
    if not text:
        return None

    candidate = extract_json_block(text)
    if not candidate:
        return None

    try:
        return json.loads(candidate)
    except Exception:
        return None
    

ALLOWED_PARAMETERS = {
    "employer_config": [
        "hire_threshold",
        "cross_major_tolerance",
        "major_preference_strength",
        "salary_elasticity",
    ],
    "student_config": [
        "market_signal_weight",
        "cross_major_acceptance",
        "information_transparency",
    ],
    "school_config": [
        "capacity_adjust_speed",
        "employment_feedback_weight",
        "market_feedback_weight",
    ],
    "scenario_config": [
        "macro_economy",
        "policy_support",
        "industry_boom_factor",
    ],
}


def build_parameter_tuning_material(payload: dict[str, Any]) -> dict[str, Any]:
    """
    构建参数调优建议所需的精简输入材料。
    仅保留最核心的参数、汇总指标和结构分析，避免 prompt 过大。
    """
    params = payload.get("params", {}) or {}
    summary = payload.get("summary", {}) or {}
    results = payload.get("results", []) or []
    structure_analysis = payload.get("structure_analysis", {}) or {}

    def sample_trend(rows, key):
        return [
            {"step": row.get("step"), key: row.get(key)}
            for row in rows
            if row.get(key) is not None
        ]

    return {
        "experiment_id": payload.get("experiment_id"),
        "scenario_name": payload.get("scenario_name"),
        "params": {
            group: params.get(group, {})
            for group in ALLOWED_PARAMETERS.keys()
        },
        "summary": summary,
        "key_trends": {
            "employment_rate_trend": sample_trend(results, "employment_rate"),
            "vacancy_rate_trend": sample_trend(results, "round_vacancy_rate"),
            "mismatch_index_trend": sample_trend(results, "mismatch_index"),
            "herding_index_trend": sample_trend(results, "herding_index"),
        },
        "structure_analysis": {
            "major_supply_demand_gap": structure_analysis.get("major_supply_demand_gap", []),
            "major_school_adjustment_bias": structure_analysis.get("major_school_adjustment_bias", []),
        },
    }


def build_fallback_parameter_suggestions(payload: dict[str, Any]) -> dict[str, Any]:
    """
    当大模型不可用时，使用规则方式给出基础参数建议。
    """
    summary = payload.get("summary", {}) or {}
    params = payload.get("params", {}) or {}

    diagnosis = []
    suggestions = []
    suggested_params = {}

    final_employment_rate = summary.get("final_employment_rate", 0.0)
    final_vacancy_rate = summary.get("final_round_vacancy_rate", 0.0)
    final_mismatch_index = summary.get("final_mismatch_index", 0.0)
    final_herding_index = summary.get("final_herding_index", 0.0)

    employer_config = params.get("employer_config", {}) or {}
    student_config = params.get("student_config", {}) or {}
    scenario_config = params.get("scenario_config", {}) or {}

    if final_employment_rate < 0.4:
        diagnosis.append("累计就业率偏低，岗位供给或匹配机制存在明显约束。")

    if final_vacancy_rate > 0.4:
        current = float(employer_config.get("hire_threshold", 0.55))
        target = max(0.3, round(current - 0.05, 3))
        suggestions.append({
            "config_group": "employer_config",
            "parameter": "hire_threshold",
            "direction": "decrease",
            "current_value": current,
            "suggested_value": target,
            "reason": "岗位空缺率偏高，说明招聘门槛偏严。",
            "expected_effect": "提高岗位匹配成功率，降低空缺率",
        })
        suggested_params.setdefault("employer_config", {})["hire_threshold"] = target

    if final_mismatch_index > 0.5:
        current = float(employer_config.get("cross_major_tolerance", 0.6))
        target = min(1.0, round(current + 0.1, 3))
        suggestions.append({
            "config_group": "employer_config",
            "parameter": "cross_major_tolerance",
            "direction": "increase",
            "current_value": current,
            "suggested_value": target,
            "reason": "结构错配指数较高，适度提高跨专业容忍度有助于缓解错配。",
            "expected_effect": "降低结构错配指数，提高就业率",
        })
        suggested_params.setdefault("employer_config", {})["cross_major_tolerance"] = target

    if final_herding_index > 1.3:
        current = float(student_config.get("market_signal_weight", 0.1))
        target = min(1.0, round(current + 0.05, 3))
        suggestions.append({
            "config_group": "student_config",
            "parameter": "market_signal_weight",
            "direction": "increase",
            "current_value": current,
            "suggested_value": target,
            "reason": "扎堆指数偏高，学生对市场信号响应不足。",
            "expected_effect": "削弱扎堆现象，改善专业分布",
        })
        suggested_params.setdefault("student_config", {})["market_signal_weight"] = target

    if final_employment_rate < 0.4:
        current = float(scenario_config.get("industry_boom_factor", 1.0))
        target = round(current + 0.1, 3)
        suggestions.append({
            "config_group": "scenario_config",
            "parameter": "industry_boom_factor",
            "direction": "increase",
            "current_value": current,
            "suggested_value": target,
            "reason": "就业率偏低时，可适度提高行业景气因子以增加岗位供给。",
            "expected_effect": "增加岗位数量，改善就业率",
        })
        suggested_params.setdefault("scenario_config", {})["industry_boom_factor"] = target

    if not diagnosis:
        diagnosis.append("当前结果整体处于可接受范围，建议小步微调关键参数并继续观察。")

    return {
        "diagnosis": diagnosis,
        "parameter_suggestions": suggestions,
        "suggested_params": suggested_params,
        "used_llm": False,
        "fallback_reason": "rule_based_fallback",
    }


def call_llm_for_parameter_suggestions(payload: dict[str, Any]) -> dict[str, Any]:
    """
    调用大模型生成参数调优建议。
    """
    material = build_parameter_tuning_material(payload)
    params = payload.get("params", {}) or {}
    llm_config = params.get("llm_config", {}) or {}

    llm_enabled = llm_config.get("enabled", False) and llm_config.get("use_for_analysis", True)
    api_key = getattr(settings, "LLM_API_KEY", "") or ""
    base_url = getattr(settings, "LLM_BASE_URL", "") or ""
    model_name = llm_config.get("model_name") or getattr(settings, "LLM_MODEL", "") or "gpt-4o-mini"
    temperature = llm_config.get("temperature", 0.2)

    if not (llm_enabled and api_key and base_url):
        return build_fallback_parameter_suggestions(payload)

    allowed_parameters_text = json.dumps(ALLOWED_PARAMETERS, ensure_ascii=False, indent=2)
    material_text = json.dumps(material, ensure_ascii=False, indent=2)

    output_example = """
    {
    "diagnosis": ["..."],
    "parameter_suggestions": [
        {
        "config_group": "employer_config",
        "parameter": "hire_threshold",
        "direction": "increase/decrease/keep",
        "current_value": 0.55,
        "suggested_value": 0.50,
        "reason": "...",
        "expected_effect": "..."
        }
    ],
    "suggested_params": {
        "employer_config": {
        "hire_threshold": 0.50
        }
    }
    }
    """.strip()

    prompt = (
        "你是人才市场供需动态仿真系统的参数调优助手。\n\n"
        "请根据当前实验的参数配置、汇总结果、关键趋势和结构分析，输出参数调整建议。\n\n"
        "要求：\n"
        "1. 只允许从下列参数中选择建议对象：\n"
        f"{allowed_parameters_text}\n\n"
        "2. 最多建议 5 个参数。\n"
        "3. 每个参数调整幅度不要过大，原则上不超过当前值的 ±20%。\n"
        "4. 建议必须结合结果指标解释原因，例如累计就业率、岗位空缺率、结构错配指数、扎堆指数、专业供需缺口等。\n"
        "5. 你的回复必须且只能是 JSON 对象本身。\n"
        "6. 不要输出任何解释文字，不要输出 markdown，不要使用 ```json 代码块。\n"
        "7. 输出开头必须是 { ，结尾必须是 } 。\n"
        "8. 输出格式必须严格如下：\n"
        f"{output_example}\n\n"
        "当前实验材料：\n"
        f"{material_text}"
    )



    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model_name,
        "temperature": temperature,
        "messages": [
            {
                "role": "system",
                "content": "你是一名擅长仿真参数分析和结构化 JSON 输出的中文研究助理。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=600)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()

        # print("DEBUG parameter suggestion raw content =", repr(content))

        parsed = try_parse_llm_json(content)
        if parsed is None:
            raise ValueError(f"llm output is not valid json: {content[:500]}")

        parsed["used_llm"] = True
        parsed["fallback_reason"] = ""
        return parsed
    except Exception as exc:
        result = build_fallback_parameter_suggestions(payload)
        result["fallback_reason"] = f"llm_failed: {repr(exc)}"
        return result