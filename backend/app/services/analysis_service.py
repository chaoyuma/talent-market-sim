import json
from typing import Any, Dict, List, Optional

import requests

from app.core.config import settings
from app.services.presentation_service import build_explanation_ready_payload


def explain_simulation_result(req_data: Dict[str, Any]) -> str:
    llm_enabled = (
        req_data.get("params", {})
        .get("llm_config", {})
        .get("enabled", False)
    )

    api_key = getattr(settings, "LLM_API_KEY", "") or ""
    base_url = getattr(settings, "LLM_BASE_URL", "") or ""
    model_name = (
        req_data.get("params", {})
        .get("llm_config", {})
        .get("model_name", "")
        or getattr(settings, "LLM_MODEL", "")
        or "gpt-4o-mini"
    )
    temperature = (
        req_data.get("params", {})
        .get("llm_config", {})
        .get("temperature", 0.3)
    )

    if not llm_enabled or not api_key or not base_url:
        return build_fallback_explanation(req_data)

    prompt = build_result_explanation_prompt(req_data)

    try:
        return call_openai_style_llm(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
        )
    except Exception as exc:
        print("LLM call failed:", repr(exc))
        return build_fallback_explanation(req_data)


def build_result_explanation_prompt(req_data: Dict[str, Any]) -> str:
    explanation_payload = build_explanation_ready_payload(req_data)
    results = req_data.get("results", []) or []
    latest = (results or [{}])[-1]

    metric_notes = {
        "累计指标说明": (
            "累计就业率、累计对口率、累计跨专业率、累计平均薪资、累计平均满意度，"
            "表示截至当前轮、覆盖所有已进入市场 cohort 的累计结果。"
        ),
        "本轮指标说明": (
            "本轮新增就业率、本轮岗位数、本轮空缺率、本轮申请数、本轮Offer数等，"
            "表示当前这一轮市场撮合过程中的流量结果。"
        ),
        "模型口径提醒": (
            "如果未启用未就业滞留机制，则本轮新生就业率主要反映当轮 cohort 的结果；"
            "不要把它和累计就业率混写为同一个概念。"
        ),
    }

    return f"""
你是人才市场供需动态仿真系统的中文分析助手。

请基于下面这份仿真结果生成“结果解释”，要求：
1. 只使用中文字段名称，不要直接输出 employment_rate、carryover_pool_share、threshold_relax_speed 这类代码名。
2. 解释必须和现有指标口径严格对应，明确区分“累计指标”和“本轮流量指标”。
3. 如果发现指标口径或结果表现存在明显异常，要直接指出并解释，不要回避。
4. 输出采用以下结构：
   一、总体判断
   二、关键指标解读
   三、结构性现象
   四、模型口径提醒
   五、调参与实验建议
5. 调参建议尽量引用中文参数名。
6. 语言正式、简洁，不堆砌空话。

指标口径说明：
{json.dumps(metric_notes, ensure_ascii=False, indent=2)}

实验材料：
{json.dumps(explanation_payload, ensure_ascii=False, indent=2)}

最后一轮原始关键值：
{json.dumps(latest, ensure_ascii=False, indent=2)}
""".strip()


def call_openai_style_llm(
    api_key: str,
    base_url: str,
    model_name: str,
    prompt: str,
    temperature: float = 0.3,
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_name,
        "temperature": temperature,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一名擅长解释仿真实验结果的中文分析专家。"
                    "你会使用正式、清晰的中文，并严格避免直接输出代码字段名。"
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def build_fallback_explanation(req_data: Dict[str, Any]) -> str:
    latest = req_data.get("latest_result", {}) or {}
    actual_runtime = req_data.get("actual_runtime", {}) or {}
    params = req_data.get("params", {}) or {}
    structure_analysis = req_data.get("structure_analysis", {}) or {}

    base_config = params.get("base_config", {})
    scenario_config = params.get("scenario_config", {})
    student_config = params.get("student_config", {})
    employer_config = params.get("employer_config", {})
    type_config = params.get("type_config", {})

    lines: List[str] = []
    lines.append("一、总体判断")
    lines.append(
        f"本次实验实际运行规模为学生 {actual_runtime.get('student_count', '-')} 人、"
        f"学校 {actual_runtime.get('school_count', '-')} 所、企业 {actual_runtime.get('employer_count', '-')} 家，"
        f"共运行 {base_config.get('steps', '-')} 轮。"
    )
    lines.append(
        f"截至当前轮，累计就业率为 {format_percent(latest.get('employment_rate'))}，"
        f"累计对口率为 {format_percent(latest.get('matching_rate'))}，"
        f"累计平均薪资为 {format_float(latest.get('avg_salary'))}。"
    )

    lines.append("")
    lines.append("二、关键指标解读")
    lines.append(
        f"本轮新增就业率为 {format_percent(latest.get('round_new_employment_rate'))}，"
        f"本轮岗位空缺率为 {format_percent(latest.get('round_vacancy_rate'))}，"
        f"岗位竞争度为 {format_float(latest.get('avg_applications_per_job'))}。"
    )
    lines.append(
        f"本轮 Offer 数为 {latest.get('round_offer_count', '-') }，"
        f"Offer 接受数为 {latest.get('round_accepted_offer_count', '-') }，"
        f"Offer 拒绝数为 {latest.get('round_rejected_offer_count', '-') }。"
    )
    if type_config.get("enable_unemployed_carryover", False):
        lines.append(
            f"当前滞留求职人数为 {latest.get('carryover_student_count', '-') }，"
            f"滞留就业率为 {format_percent(latest.get('carryover_employment_rate'))}，"
            f"滞留池占比为 {format_percent(latest.get('carryover_pool_share'))}。"
        )
    else:
        lines.append(
            f"当前未启用未就业滞留机制，因此本轮新生就业率 "
            f"{format_percent(latest.get('new_cohort_employment_rate'))} "
            f"基本反映本轮 cohort 的就业吸纳情况。"
        )

    lines.append("")
    lines.append("三、结构性现象")
    lines.append(
        f"结构错配指数为 {format_float(latest.get('mismatch_index'))}，"
        f"扎堆指数为 {format_float(latest.get('herding_index'))}。"
    )
    major_gaps = structure_analysis.get("major_supply_demand_gap", []) or []
    if major_gaps:
        sorted_gaps = sorted(major_gaps, key=lambda x: abs(x.get("gap", 0)), reverse=True)
        top_gap = sorted_gaps[0]
        lines.append(
            f"当前供需偏差最明显的专业是 {top_gap.get('major', '-') }，"
            f"供需差值为 {format_percent(abs(top_gap.get('gap', 0)))}。"
        )

    lines.append("")
    lines.append("四、模型口径提醒")
    if not type_config.get("enable_unemployed_carryover", False):
        lines.append(
            "当前未启用未就业滞留机制时，每一轮都会生成新的毕业生 cohort。"
            "因此，本轮新生就业率反映的是当前 cohort 的结果，而累计就业率反映的是截至当前轮所有 cohort 的累计结果，"
            "两者不能混作同一口径解读。"
        )
    else:
        lines.append(
            "当前已启用未就业滞留机制，累计就业率与本轮新生就业率、滞留就业率需要分开解读。"
        )

    if latest.get("round_offer_count", 0) and latest.get("round_accepted_offer_count", 0):
        acceptance_gap = latest.get("round_offer_count", 0) - latest.get("round_accepted_offer_count", 0)
        if acceptance_gap > 0:
            lines.append(
                "当前 Offer 发放数与接受数存在差距，说明岗位匹配并非只受岗位数量约束，"
                "还受到学生效用判断和企业筛选机制共同影响。"
            )

    lines.append("")
    lines.append("五、调参与实验建议")
    lines.append(
        f"1. 如果希望提高就业吸纳能力，可优先观察“招聘阈值”当前值 {format_float(employer_config.get('hire_threshold'))} "
        "以及“企业跨专业容忍度”的设定。"
    )
    lines.append(
        f"2. 如果希望缓解结构错配，可对比调整“市场信号权重”"
        f"（当前 {format_float(student_config.get('market_signal_weight'))}）和“信息透明度”"
        f"（当前 {format_float(student_config.get('information_transparency'))}）。"
    )
    lines.append(
        f"3. 如果希望观察更充分的撮合过程，可提高“每轮撮合轮数”"
        f"（当前 {scenario_config.get('matching_rounds_per_step', '-') }）并关注 Offer 接受与拒绝变化。"
    )
    lines.append(
        "4. 建议将“企业反馈时滞”“学校反馈时滞”“是否启用未就业滞留机制”组成对照实验，"
        "更容易观察中短期反馈与跨期积压的差异。"
    )

    return "\n".join(lines)


def format_percent(value: Optional[float]) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.1f}%"


def format_float(value: Optional[float]) -> str:
    if value is None:
        return "-"
    return f"{value:.3f}"
