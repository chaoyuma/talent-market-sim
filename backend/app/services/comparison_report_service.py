import json
from typing import Any

import requests

from app.core.config import settings
from app.services.experiment_service import load_output_payload
from app.services.presentation_service import build_explanation_ready_payload
from pathlib import Path
from app.services.report_task_service import (
    update_report_task,
    REPORT_OUTPUT_DIR,
)

from pathlib import Path
from datetime import datetime

from app.core.database import SessionLocal
from app.repositories.report_repository import create_report


REPORT_OUTPUT_DIR = Path("outputs/reports")
REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def persist_comparison_report(result: dict, experiment_ids: list[str]) -> dict:
    """
    将报告保存到本地目录，并写入数据库。
    """
    report_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    title = result.get("title") or "仿真对比分析报告"
    report_markdown = result.get("report_markdown") or ""
    used_llm = bool(result.get("used_llm", False))
    fallback_reason = result.get("fallback_reason", "")

    file_name = f"{report_id}.md"
    file_path = REPORT_OUTPUT_DIR / file_name
    file_path.write_text(report_markdown, encoding="utf-8")

    db = SessionLocal()
    try:
        create_report(
            db=db,
            report_id=report_id,
            title=title,
            report_type="comparison",
            status="finished",
            experiment_ids_json=experiment_ids,
            report_markdown=report_markdown,
            file_name=file_name,
            file_path=str(file_path),
            used_llm=used_llm,
            fallback_reason=fallback_reason,
            error_message=None,
        )
    finally:
        db.close()

    return {
        "report_id": report_id,
        "title": title,
        "file_name": file_name,
        "file_path": str(file_path),
        "used_llm": used_llm,
        "fallback_reason": fallback_reason,
        "report_markdown": report_markdown,
    }
def execute_comparison_report_task(task_id: str, experiment_ids: list[str]):
    """
    后台执行对比报告生成任务。
    """
    update_report_task(task_id, status="running", error="")

    try:
        result = generate_comparison_report(experiment_ids)

        title = result.get("title") or "仿真对比分析报告"
        report_markdown = result.get("report_markdown") or ""
        used_llm = result.get("used_llm", False)
        fallback_reason = result.get("fallback_reason", "")

        safe_filename = f"{task_id}.md"
        output_path = REPORT_OUTPUT_DIR / safe_filename

        # 直接写 markdown 文件，便于后续下载
        output_path.write_text(report_markdown, encoding="utf-8")
        saved = persist_comparison_report(result, experiment_ids)

        update_report_task(
            task_id,
            status="finished",
            title=saved["title"],
            report_markdown=saved["report_markdown"],
            download_filename=saved["file_name"],
            download_path=saved["file_path"],
            used_llm=saved["used_llm"],
            fallback_reason=saved["fallback_reason"],
            report_id=saved["report_id"],
        )
       

    except Exception as exc:
        update_report_task(
            task_id,
            status="failed",
            error=repr(exc),
        )

def generate_comparison_report(experiment_ids: list[str]) -> dict[str, Any]:
    """
    生成多组实验的对比分析报告。
    """
    payloads = []
    for experiment_id in experiment_ids:
        payload = load_output_payload(experiment_id)
        if payload:
            payloads.append(payload)

    if not payloads:
        return {
            "title": "仿真对比分析报告",
            "report_markdown": "未找到可用于生成报告的实验结果。",
            "experiments": [],
            "used_llm": False,
            "fallback_reason": "no_payloads",
        }

    # 只要所选实验中任意一组启用了 llm，就允许尝试用大模型生成报告
    llm_enabled = any(
        (((payload.get("params", {}) or {}).get("llm_config", {}) or {}).get("enabled", False))
        for payload in payloads
    )

    # 模型名仍优先取第一组实验参数，其次读系统配置
    first_llm_config = ((payloads[0].get("params", {}) or {}).get("llm_config", {}) or {})
    api_key = getattr(settings, "LLM_API_KEY", "") or ""
    base_url = getattr(settings, "LLM_BASE_URL", "") or ""
    model_name = first_llm_config.get("model_name") or getattr(settings, "LLM_MODEL", "") or "gpt-4o-mini"
    temperature = first_llm_config.get("temperature", 0.3)

    # # print("DEBUG comparison report llm_enabled =", llm_enabled)
    # # print("DEBUG comparison report has_api_key =", bool(api_key))
    # # print("DEBUG comparison report has_base_url =", bool(base_url))
    # # print("DEBUG comparison report model_name =", model_name)

    used_llm = False
    fallback_reason = ""

    if llm_enabled and api_key and base_url:
        try:
            # print("DEBUG comparison report will call llm")
            report_markdown = _call_llm_for_report(
                payloads=payloads,
                api_key=api_key,
                base_url=base_url,
                model_name=model_name,
                temperature=temperature,
            )
            used_llm = True
        except Exception as exc:
            print("comparison report llm failed:", repr(exc))
            report_markdown = build_fallback_comparison_report(payloads)
            fallback_reason = f"llm_failed: {repr(exc)}"
            # # print("DEBUG comparison report using fallback, reason =", fallback_reason)
    else:
        report_markdown = build_fallback_comparison_report(payloads)

        if not llm_enabled:
            fallback_reason = "llm_disabled"
        elif not api_key:
            fallback_reason = "missing_api_key"
        elif not base_url:
            fallback_reason = "missing_base_url"
        else:
            fallback_reason = "unknown"

        # print("DEBUG comparison report using fallback, reason =", fallback_reason)

    return {
        "title": f"仿真对比分析报告（{len(payloads)}组实验）",
        "report_markdown": report_markdown,
        "experiments": [
            {
                "experiment_id": item.get("experiment_id"),
                "scenario_name": item.get("scenario_name"),
            }
            for item in payloads
        ],
        "used_llm": used_llm,
        "fallback_reason": fallback_reason,
    }


def _call_llm_for_report(
    payloads: list[dict[str, Any]],
    api_key: str,
    base_url: str,
    model_name: str,
    temperature: float,
) -> str:
    """
    调用大模型生成多实验对比分析报告。
    """
    material = [build_explanation_ready_payload(payload) for payload in payloads]

    prompt = f"""
你是人才市场供需动态仿真系统的研究报告助手。

请基于下面多组实验结果，生成一份中文对比分析报告。要求：
1. 报告用于项目内部研判，语言正式、清晰。
2. 只使用中文字段名称，不直接输出代码字段名。
3. 重点比较：累计就业率、累计对口率、岗位空缺率、结构错配指数、扎堆指数、平均薪资、同区域就业率、专业供需缺口。
4. 输出结构：
   # 报告标题
   ## 一、总体结论
   ## 二、关键差异比较
   ## 三、结构性现象
   ## 四、机制解释
   ## 五、建议与后续实验
5. 如果实验数量大于 1，请明确指出哪组实验更优、哪组实验风险更高，以及差异可能由哪些参数变化驱动。
6. 不要输出 JSON，不要输出代码。

实验材料：
{json.dumps(material, ensure_ascii=False, indent=2)}
""".strip()

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
                "content": (
                    "你是一名擅长撰写仿真比较分析报告的中文研究助理。"
                    "你严格使用中文字段名，报告结构清晰，避免代码味表达。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }

    response = requests.post(url, headers=headers, json=body, timeout=600)
    response.raise_for_status()

    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def build_fallback_comparison_report(payloads: list[dict[str, Any]]) -> str:
    """
    当大模型不可用时，使用规则模板生成回退版对比报告。
    """
    rows = []
    for payload in payloads:
        summary = payload.get("summary", {}) or {}
        rows.append({
            "experiment_id": payload.get("experiment_id"),
            "scenario_name": payload.get("scenario_name"),
            "employment_rate": summary.get("final_employment_rate", 0.0),
            "matching_rate": summary.get("final_matching_rate", 0.0),
            "vacancy_rate": summary.get("final_round_vacancy_rate", 0.0),
            "mismatch_index": summary.get("final_mismatch_index", 0.0),
            "avg_salary": summary.get("final_avg_salary", 0.0),
            "herding_index": summary.get("final_herding_index", 0.0),
        })

    best_employment = max(rows, key=lambda item: item["employment_rate"])
    worst_mismatch = max(rows, key=lambda item: item["mismatch_index"])

    lines = [
        "# 仿真对比分析报告",
        "",
        "## 一、总体结论",
        (
            f"本次共比较 {len(rows)} 组实验。从累计就业率看，表现最优的是实验 "
            f"{best_employment['experiment_id']}（场景：{best_employment['scenario_name']}），"
            f"累计就业率为 {best_employment['employment_rate'] * 100:.1f}%。"
        ),
        (
            f"从结构错配指数看，风险最高的是实验 {worst_mismatch['experiment_id']}，"
            f"结构错配指数为 {worst_mismatch['mismatch_index']:.3f}。"
        ),
        "",
        "## 二、关键差异比较",
    ]

    for row in rows:
        lines.append(
            (
                f"- 实验 {row['experiment_id']}（{row['scenario_name']}）："
                f"累计就业率 {row['employment_rate'] * 100:.1f}%，"
                f"累计对口率 {row['matching_rate'] * 100:.1f}%，"
                f"本轮空缺率 {row['vacancy_rate'] * 100:.1f}%，"
                f"结构错配指数 {row['mismatch_index']:.3f}，"
                f"平均薪资 {row['avg_salary']:.3f}，"
                f"扎堆指数 {row['herding_index']:.3f}。"
            )
        )

    lines.extend([
        "",
        "## 三、结构性现象",
        "需要结合专业供需缺口、专业市场信号和区域流动指标继续观察各实验差异。",
        "",
        "## 四、机制解释",
        "当前为规则回退报告，建议在已配置大模型的情况下重新生成，以获得更细致的机制解释和参数归因。",
        "",
        "## 五、建议与后续实验",
        "建议围绕招聘阈值、市场信号权重、企业跨专业容忍度、信息透明度和未就业滞留机制开展对照实验。",
    ])
    return "\n".join(lines)