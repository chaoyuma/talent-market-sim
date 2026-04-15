import json
from typing import Any, Dict, List, Optional

import requests

from app.core.config import settings


def explain_simulation_result(req_data: Dict[str, Any]) -> str:
    """
    优先调用大模型生成实验结果解释；
    如果未配置大模型或调用失败，则回退到规则解释。
    """
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

    # 若未启用或未配置，则直接回退
    if not llm_enabled or not api_key or not base_url:
        print(
            "LLM fallback because config missing:",
            {
                "llm_enabled": llm_enabled,
                "has_api_key": bool(api_key),
                "has_base_url": bool(base_url),
                "model_name": model_name,
            }
        )
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
    except Exception as e:
        print("LLM call failed:", repr(e))
        return build_fallback_explanation(req_data)


def build_result_explanation_prompt(req_data: Dict[str, Any]) -> str:
    """
    构造实验结果解释 prompt。
    """
    experiment_id = req_data.get("experiment_id", "")
    params = req_data.get("params", {})
    actual_runtime = req_data.get("actual_runtime", {})
    summary = req_data.get("summary", {})
    latest_result = req_data.get("latest_result", {})
    results = req_data.get("results", [])

    prompt = f"""
你是一名人才市场供需动态仿真系统分析助手。
请根据下面给出的实验参数、实际运行规模和仿真结果，生成一份结构化的中文结果解释。

要求：
1. 输出分为四部分：
   一、总体判断
   二、关键现象
   三、可能原因
   四、调参建议
2. 语言要专业、清晰，不要空话。
3. 要特别注意区分“累计指标”和“本轮流量指标”。
4. 若实际运行样本较小，请明确指出“小样本下部分指标仅供参考”。
5. 调参建议要尽量具体，指出应该优先调整哪些参数。

实验ID：
{experiment_id}

实际运行规模：
{json.dumps(actual_runtime, ensure_ascii=False, indent=2)}

实验参数：
{json.dumps(params, ensure_ascii=False, indent=2)}

结果摘要：
{json.dumps(summary, ensure_ascii=False, indent=2)}

最新一轮结果：
{json.dumps(latest_result, ensure_ascii=False, indent=2)}

完整逐轮结果：
{json.dumps(results, ensure_ascii=False, indent=2)}
"""
    return prompt.strip()


def call_openai_style_llm(
    api_key: str,
    base_url: str,
    model_name: str,
    prompt: str,
    temperature: float = 0.3,
) -> str:
    """
    调用 OpenAI 风格 Chat Completions 接口。
    要求 base_url 指向形如：
    https://xxx/v1
    """
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
                "content": "你是一名擅长解释仿真实验结果的中文分析助手。",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()

    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def build_fallback_explanation(req_data: Dict[str, Any]) -> str:
    """
    规则版兜底解释。
    """
    latest = req_data.get("latest_result", {}) or {}
    actual_runtime = req_data.get("actual_runtime", {}) or {}

    lines: List[str] = []

    student_count = actual_runtime.get("student_count", "-")
    school_count = actual_runtime.get("school_count", "-")
    employer_count = actual_runtime.get("employer_count", "-")

    lines.append("一、总体判断")
    lines.append(
        f"本次实验实际参与学生 {student_count} 人、学校 {school_count} 所、企业 {employer_count} 家。"
    )
    lines.append(
        f"截至当前轮，累计就业率为 {format_percent(latest.get('employment_rate'))}，"
        f"累计对口率为 {format_percent(latest.get('matching_rate'))}，"
        f"累计跨专业率为 {format_percent(latest.get('cross_major_rate'))}。"
    )

    if isinstance(student_count, int) and student_count < 30:
        lines.append("本次实验实际样本量较小，部分结构类指标和反馈类指标更适合做机制验证，不宜直接用于总体结论判断。")

    lines.append("")
    lines.append("二、关键现象")
    lines.append(
        f"本轮新增就业率为 {format_percent(latest.get('round_new_employment_rate'))}，"
        f"活跃求职人数为 {latest.get('active_job_seekers', '-') }，"
        f"本轮岗位数为 {latest.get('round_job_count', '-') }，"
        f"本轮空缺率为 {format_percent(latest.get('round_vacancy_rate'))}。"
    )
    lines.append(
        f"结构错配指数为 {format_float(latest.get('mismatch_index'))}，"
        f"扎堆指数为 {format_float(latest.get('herding_index'))}，"
        f"平均招聘阈值为 {format_float(latest.get('avg_hire_threshold'))}，"
        f"平均培养质量为 {format_float(latest.get('avg_training_quality'))}。"
    )

    lines.append("")
    lines.append("三、可能原因")
    lines.append("1. 当前结果受到实际参与样本规模影响，若学生和企业数量偏少，首轮匹配后市场可能很快清空。")
    lines.append("2. 若企业招聘阈值偏低、跨专业容忍度偏高，学生更容易在首轮完成匹配。")
    lines.append("3. 若后续活跃求职人数为 0，则后续轮次更多反映存量状态维持，而不是新的市场撮合过程。")
    lines.append("4. 学校反馈通常慢于企业反馈，因此培养质量和容量变化往往滞后出现。")

    lines.append("")
    lines.append("四、调参建议")
    lines.append("1. 优先扩充学生与企业样本量，避免第一轮即完成全部匹配。")
    lines.append("2. 提高 hire_threshold，降低 cross_major_tolerance，观察就业过程是否由“一轮清空”变为逐轮演化。")
    lines.append("3. 降低信息透明度、降低每轮最大投递数，可增强市场动态过程。")
    lines.append("4. 对比不同宏观景气度、政策支持强度、企业反馈时滞和学校反馈时滞，开展标准场景实验。")

    return "\n".join(lines)


def format_percent(value: Optional[float]) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.1f}%"


def format_float(value: Optional[float]) -> str:
    if value is None:
        return "-"
    return f"{value:.3f}"