#!/usr/bin/env python3
"""
mysql_seed_generator.py

用途：
1. 按宏观约束生成 majors / major_industry_mapping / schools / employers / jobs / students 六张表数据
2. 输出为 CSV 和 INSERT SQL
3. 不写入 id / created_at，依赖 MySQL 自增与默认值

本版优化点：
1. 学生兴趣专业分布可控
2. 岗位专业分布可控
3. 岗位生成由“目标专业占比 + 行业映射 + 模板抽样”共同决定
4. 企业增加规模类型与基础岗位数
5. 输出 CSV 与 SQL，方便直接入库

运行示例：
python mysql_seed_generator.py --output ./seed_output --students 10000 --schools 200 --employers 1000 --jobs 5000 --seed 42

依赖：
- Python 3.10+
- 标准库即可
"""

from __future__ import annotations
import argparse
import csv
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple


# -----------------------------
# 基础工具
# -----------------------------
def clamp(x: float, lo: float, hi: float) -> float:
    """限制数值范围。"""
    return max(lo, min(hi, x))


def rnd(a: float, b: float) -> float:
    """生成并保留 4 位小数的均匀随机数。"""
    return round(random.uniform(a, b), 4)


def weighted_choice(items: List[Tuple[str, float]]) -> str:
    """
    从 [(item, weight), ...] 中按权重抽样。
    """
    total = sum(max(w, 0.0) for _, w in items)
    if total <= 0:
        return items[-1][0]

    r = random.random() * total
    acc = 0.0
    for item, w in items:
        acc += max(w, 0.0)
        if r <= acc:
            return item
    return items[-1][0]


def gaussian_clip(mu: float, sigma: float, lo: float, hi: float) -> float:
    """
    正态抽样后裁剪到指定范围。
    """
    val = random.gauss(mu, sigma)
    return round(clamp(val, lo, hi), 4)


def ensure_dir(p: Path) -> None:
    """确保输出目录存在。"""
    p.mkdir(parents=True, exist_ok=True)


def normalize_weight_dict(d: Dict[str, float]) -> Dict[str, float]:
    """
    将权重字典归一化，避免总和不为 1。
    """
    total = sum(max(v, 0.0) for v in d.values())
    if total <= 0:
        n = len(d)
        return {k: 1.0 / n for k in d}
    return {k: max(v, 0.0) / total for k, v in d.items()}


def weighted_choice_from_dict(d: Dict[str, float]) -> str:
    """
    从 {item: weight} 字典中按权重抽样。
    """
    norm = normalize_weight_dict(d)
    return weighted_choice(list(norm.items()))


def build_major_name_to_code(majors: List[Dict]) -> Dict[str, str]:
    """
    构建 major_name -> major_code 映射。
    """
    return {m["major_name"]: m["major_code"] for m in majors}


def build_industry_major_weight_map(mappings: List[Dict]) -> Dict[str, Dict[str, float]]:
    """
    将 major_industry_mapping 转成：
    {
        industry: {
            major_name: match_score
        }
    }
    """
    result: Dict[str, Dict[str, float]] = {}
    for row in mappings:
        industry = row["industry"]
        major_name = row["major_name"]
        score = float(row["match_score"])
        result.setdefault(industry, {})
        result[industry][major_name] = score
    return result


# -----------------------------
# 宏观约束
# -----------------------------
DEFAULT_CONSTRAINTS = {
    "student_macro": {
        "discipline_distribution": {
            "工学": 1565928,
            "管理学": 849793,
            "文学": 466944,
            "艺术学": 449084,
            "医学": 333657,
            "理学": 298672,
            "经济学": 262452,
            "教育学": 222013,
            "法学": 166470,
            "农学": 76567,
            "历史学": 21665,
            "哲学": 2413,
        },
        "province_top_samples": {
            "河南": 374711,
            "广东": 349512,
            "山东": 327899,
            "江苏": 311178,
            "湖北": 262450,
            "河北": 250983,
            "湖南": 214303,
            "安徽": 199170,
            "辽宁": 190350,
            "浙江": 183320,
            "江西": 182388,
            "广西": 168769,
        },
    },
    "school_macro": {
        "school_type_weights_for_simulation": {
            "research_university": 0.12,
            "general_university": 0.48,
            "applied_university": 0.30,
            "vocational_undergraduate": 0.10,
        },
        "tier_defaults": {
            "research_university": "A",
            "general_university": "B",
            "applied_university": "C",
            "vocational_undergraduate": "V",
        }
    },
    "city_tier_weights": {
        "超大城市": 1.0,
        "特大城市": 0.85,
        "I型大城市": 0.70,
        "II型大城市": 0.55,
        "中等城市": 0.40,
        "I型小城市": 0.25,
        "II型小城市": 0.10
    },
    "industry_macro": {
        "industry_weights_for_employers": {
            "人工智能": 0.10,
            "智能硬件": 0.08,
            "先进制造": 0.16,
            "医疗健康": 0.12,
            "现代服务": 0.16,
            "物流供应链": 0.10,
            "建筑工程": 0.10,
            "内容传媒": 0.06,
            "商务服务": 0.08,
            "房地产链条": 0.04
        },
        "salary_anchor": {
            "人工智能": {"mean": 22000, "low": 18000, "high": 27000, "heat": 0.92},
            "智能硬件": {"mean": 10624, "low": 9000, "high": 13500, "heat": 0.74},
            "先进制造": {"mean": 10400, "low": 9000, "high": 12500, "heat": 0.78},
            "医疗健康": {"mean": 10655, "low": 8500, "high": 13000, "heat": 0.81},
            "现代服务": {"mean": 9300, "low": 6800, "high": 11000, "heat": 0.68},
            "物流供应链": {"mean": 7800, "low": 6500, "high": 9500, "heat": 0.45},
            "建筑工程": {"mean": 9600, "low": 8000, "high": 12000, "heat": 0.52},
            "内容传媒": {"mean": 8500, "low": 7000, "high": 11000, "heat": 0.50},
            "商务服务": {"mean": 8800, "low": 7000, "high": 11000, "heat": 0.56},
            "房地产链条": {"mean": 8200, "low": 6500, "high": 10000, "heat": 0.30}
        }
    }
}


PROVINCE_REGION = {
    "北京": "东部", "天津": "东部", "河北": "东部", "江苏": "东部", "浙江": "东部", "山东": "东部", "广东": "东部",
    "福建": "东部", "上海": "东部", "海南": "东部",
    "山西": "中部", "安徽": "中部", "江西": "中部", "河南": "中部", "湖北": "中部", "湖南": "中部",
    "辽宁": "东北", "吉林": "东北", "黑龙江": "东北",
    "内蒙古": "西部", "广西": "西部", "重庆": "西部", "四川": "西部", "贵州": "西部", "云南": "西部",
    "西藏": "西部", "陕西": "西部", "甘肃": "西部", "青海": "西部", "宁夏": "西部", "新疆": "西部",
}


CITY_POOL = [
    ("北京", "超大城市", 1.00), ("上海", "超大城市", 1.00), ("深圳", "超大城市", 1.00), ("广州", "超大城市", 1.00),
    ("杭州", "特大城市", 0.85), ("成都", "特大城市", 0.85), ("武汉", "特大城市", 0.85), ("南京", "特大城市", 0.85),
    ("西安", "I型大城市", 0.70), ("苏州", "I型大城市", 0.70), ("郑州", "I型大城市", 0.70),
    ("长沙", "II型大城市", 0.55), ("合肥", "II型大城市", 0.55), ("南昌", "II型大城市", 0.55),
    ("南宁", "中等城市", 0.40), ("贵阳", "中等城市", 0.40), ("兰州", "中等城市", 0.40),
]


EMPLOYER_TYPE_WEIGHTS = [
    ("state_owned", 0.18),
    ("private", 0.48),
    ("foreign", 0.10),
    ("startup", 0.16),
    ("platform", 0.08),
]


STUDENT_TYPE_WEIGHTS = [
    ("employment_oriented", 0.32),
    ("salary_oriented", 0.18),
    ("interest_oriented", 0.20),
    ("trend_sensitive", 0.18),
    ("prestige_oriented", 0.12),
]


# -----------------------------
# 可控的专业目标分布
# -----------------------------
SIM_MAJOR_STUDENT_SHARE = {
    "计算机与人工智能": 0.135,
    "电子信息与自动化": 0.120,
    "智能制造与机械工程": 0.105,
    "材料与化工": 0.090,
    "土木与交通工程": 0.095,
    "医学与护理": 0.080,
    "管理与工商": 0.095,
    "财经与金融": 0.090,
    "传媒与内容传播": 0.085,
    "现代服务与公共管理": 0.105,
}


SIM_MAJOR_JOB_SHARE = {
    "计算机与人工智能": 0.150,
    "电子信息与自动化": 0.185,
    "智能制造与机械工程": 0.040,
    "材料与化工": 0.055,
    "土木与交通工程": 0.090,
    "医学与护理": 0.135,
    "管理与工商": 0.155,
    "财经与金融": 0.055,
    "传媒与内容传播": 0.075,
    "现代服务与公共管理": 0.060,
}


EMPLOYER_SIZE_WEIGHTS = [
    ("small", 0.50),
    ("medium", 0.35),
    ("large", 0.15),
]


EMPLOYER_SIZE_JOB_COUNT_RANGE = {
    "small": (3, 8),
    "medium": (8, 16),
    "large": (15, 30),
}


SIM_MAJOR_DEFS = [
    {
        "major_code": "MJR001", "major_name": "计算机与人工智能", "category": "工学",
        "skill_direction": "AI,Algorithm,Programming", "heat_init": 0.95, "mobility": 0.90,
        "salary_expectation": 19000, "policy_support_weight": 0.95,
        "industries": [("人工智能", 0.98), ("智能硬件", 0.86), ("商务服务", 0.52), ("内容传媒", 0.36)]
    },
    {
        "major_code": "MJR002", "major_name": "电子信息与自动化", "category": "工学",
        "skill_direction": "Embedded,Automation,Control", "heat_init": 0.84, "mobility": 0.72,
        "salary_expectation": 13500, "policy_support_weight": 0.88,
        "industries": [("智能硬件", 0.96), ("先进制造", 0.82), ("人工智能", 0.66)]
    },
    {
        "major_code": "MJR003", "major_name": "智能制造与机械工程", "category": "工学",
        "skill_direction": "Manufacturing,Mechanical,Process", "heat_init": 0.80, "mobility": 0.62,
        "salary_expectation": 11800, "policy_support_weight": 0.86,
        "industries": [("先进制造", 0.95), ("智能硬件", 0.74), ("建筑工程", 0.42)]
    },
    {
        "major_code": "MJR004", "major_name": "材料与化工", "category": "工学",
        "skill_direction": "Material,Chemical,Process", "heat_init": 0.76, "mobility": 0.56,
        "salary_expectation": 10500, "policy_support_weight": 0.80,
        "industries": [("先进制造", 0.86), ("医疗健康", 0.40)]
    },
    {
        "major_code": "MJR005", "major_name": "土木与交通工程", "category": "工学",
        "skill_direction": "Civil,Infrastructure,Transport", "heat_init": 0.62, "mobility": 0.45,
        "salary_expectation": 9800, "policy_support_weight": 0.74,
        "industries": [("建筑工程", 0.97), ("物流供应链", 0.40), ("房地产链条", 0.52)]
    },
    {
        "major_code": "MJR006", "major_name": "医学与护理", "category": "医学",
        "skill_direction": "Clinical,Care,Health", "heat_init": 0.78, "mobility": 0.38,
        "salary_expectation": 11200, "policy_support_weight": 0.90,
        "industries": [("医疗健康", 0.99), ("现代服务", 0.32)]
    },
    {
    "major_code": "MJR007", "major_name": "管理与工商", "category": "管理学",
    "skill_direction": "Management,Operation,Business", "heat_init": 0.66, "mobility": 0.84,
    "salary_expectation": 9800, "policy_support_weight": 0.65,
    "industries": [
        ("商务服务", 0.82),
        ("现代服务", 0.58),
        ("物流供应链", 0.62),
        ("人工智能", 0.36),
        ("智能硬件", 0.30),
        ("先进制造", 0.28),
        ("房地产链条", 0.30)
    ]
},
    {
        "major_code": "MJR008", "major_name": "财经与金融", "category": "经济学",
        "skill_direction": "Finance,Accounting,Data", "heat_init": 0.64, "mobility": 0.80,
        "salary_expectation": 10800, "policy_support_weight": 0.60,
        "industries": [("商务服务", 0.80), ("现代服务", 0.44), ("房地产链条", 0.40), ("人工智能", 0.30)]
    },
    {
        "major_code": "MJR009", "major_name": "传媒与内容传播", "category": "文学",
        "skill_direction": "Media,Content,Communication", "heat_init": 0.58, "mobility": 0.76,
        "salary_expectation": 8600, "policy_support_weight": 0.52,
        "industries": [("内容传媒", 0.96), ("现代服务", 0.50), ("商务服务", 0.42)]
    },
    {
        "major_code": "MJR010", "major_name": "现代服务与公共管理", "category": "管理学",
        "skill_direction": "Service,HR,PublicAdmin", "heat_init": 0.60, "mobility": 0.74,
        "salary_expectation": 8400, "policy_support_weight": 0.58,
        "industries": [("现代服务", 0.82), ("商务服务", 0.56), ("医疗健康", 0.34)]
    },
]


JOB_TEMPLATES = {
    "人工智能": [
        ("算法工程师", "MJR001", 0.90, 1.10, 0),
        ("机器人算法工程师", "MJR001", 0.92, 1.20, 0),
        ("AI产品经理", "MJR001", 0.78, 0.98, 1),
        ("数据分析师", "MJR008", 0.72, 0.92, 1),
        ("商业运营专员", "MJR007", 0.62, 0.96, 1),
    ],
    "智能硬件": [
        ("嵌入式工程师", "MJR002", 0.80, 1.00, 0),
        ("硬件测试工程师", "MJR002", 0.68, 0.92, 1),
        ("自动化控制工程师", "MJR002", 0.76, 0.98, 0),
        ("项目运营专员", "MJR007", 0.60, 0.92, 1),
    ],
    "先进制造": [
        ("智能制造工程师", "MJR003", 0.78, 1.00, 0),
        ("工艺工程师", "MJR004", 0.70, 0.92, 1),
        ("质量工程师", "MJR003", 0.62, 0.90, 1),
    ],
    "医疗健康": [
        ("临床助理", "MJR006", 0.72, 0.95, 0),
        ("护理专员", "MJR006", 0.60, 0.85, 0),
        ("医疗产品专员", "MJR010", 0.62, 0.90, 1),
    ],
    "现代服务": [
        ("产品运营专员", "MJR007", 0.60, 0.96, 1),
        ("用户增长专员", "MJR007", 0.62, 0.98, 1),
        ("客户成功经理", "MJR010", 0.56, 0.92, 1),
        ("培训顾问", "MJR010", 0.52, 0.86, 1),
        ("健康服务协调员", "MJR006", 0.52, 0.86, 1),
        ("内容运营专员", "MJR009", 0.54, 0.88, 1),
    ],
    "物流供应链": [
        ("供应链分析师", "MJR007", 0.64, 0.98, 1),
        ("供应链运营专员", "MJR007", 0.60, 0.90, 1),
        ("物流计划专员", "MJR005", 0.56, 0.84, 1),
        ("仓配调度专员", "MJR007", 0.52, 0.80, 1),
    ],
    "建筑工程": [
        ("土木工程师", "MJR005", 0.72, 0.95, 0),
        ("BIM工程师", "MJR005", 0.68, 0.90, 1),
        ("工程造价专员", "MJR007", 0.55, 0.82, 1),
    ],
    "内容传媒": [
        ("内容运营", "MJR009", 0.48, 0.82, 1),
        ("品牌传播专员", "MJR009", 0.52, 0.86, 1),
        ("新媒体策划", "MJR009", 0.56, 0.88, 1),
    ],
    "商务服务": [
        ("咨询分析师", "MJR008", 0.70, 1.00, 1),
        ("商业运营分析师", "MJR007", 0.66, 0.98, 1),
        ("市场研究专员", "MJR007", 0.60, 0.90, 1),
        ("人力资源专员", "MJR010", 0.54, 0.86, 1),
        ("商业分析师", "MJR001", 0.68, 0.98, 1),
        ("传播策划专员", "MJR009", 0.54, 0.86, 1),
    ],
    "房地产链条": [
        ("商业策划专员", "MJR007", 0.58, 0.90, 1),
        ("资产运营专员", "MJR008", 0.60, 0.92, 1),
        ("项目管理助理", "MJR005", 0.58, 0.86, 1),
    ],
}


# -----------------------------
# 生成函数
# -----------------------------
def generate_majors():
    """
    生成 majors 与 major_industry_mapping 两张表。
    """
    rows = []
    mappings = []

    for m in SIM_MAJOR_DEFS:
        rows.append({
            "major_code": m["major_code"],
            "major_name": m["major_name"],
            "category": m["category"],
            "skill_direction": m["skill_direction"],
            "heat_init": m["heat_init"],
            "mobility": m["mobility"],
            "salary_expectation": m["salary_expectation"],
            "policy_support_weight": m["policy_support_weight"],
        })

        for industry, score in m["industries"]:
            mappings.append({
                "major_name": m["major_name"],
                "industry": industry,
                "match_score": score,
            })

    return rows, mappings


def sample_province():
    """
    按省份样本权重抽样省份。
    """
    items = list(DEFAULT_CONSTRAINTS["student_macro"]["province_top_samples"].items())
    return weighted_choice(items)


def province_to_region(p):
    """
    将省份映射为区域。
    """
    return PROVINCE_REGION.get(p, "中部")


def sample_city():
    """
    从城市池中抽样城市。
    """
    return random.choice(CITY_POOL)


def generate_schools(n: int):
    """
    生成学校数据。
    """
    rows = []
    school_type_weights = list(DEFAULT_CONSTRAINTS["school_macro"]["school_type_weights_for_simulation"].items())
    tier_defaults = DEFAULT_CONSTRAINTS["school_macro"]["tier_defaults"]

    for i in range(1, n + 1):
        school_type = weighted_choice(school_type_weights)
        province = sample_province()
        city_name, city_tag, city_tier = sample_city()

        if school_type == "research_university":
            tq = gaussian_clip(0.88, 0.04, 0.75, 0.96)
            rep = gaussian_clip(0.90, 0.05, 0.70, 0.98)
            rs = gaussian_clip(0.085, 0.015, 0.05, 0.12)
            cap = int(random.randint(2500, 5000))
        elif school_type == "general_university":
            tq = gaussian_clip(0.74, 0.06, 0.60, 0.88)
            rep = gaussian_clip(0.72, 0.08, 0.50, 0.90)
            rs = gaussian_clip(0.060, 0.015, 0.03, 0.10)
            cap = int(random.randint(1500, 3200))
        elif school_type == "applied_university":
            tq = gaussian_clip(0.66, 0.06, 0.52, 0.82)
            rep = gaussian_clip(0.62, 0.08, 0.45, 0.82)
            rs = gaussian_clip(0.045, 0.012, 0.02, 0.08)
            cap = int(random.randint(1000, 2500))
        else:
            tq = gaussian_clip(0.58, 0.06, 0.45, 0.75)
            rep = gaussian_clip(0.52, 0.07, 0.40, 0.72)
            rs = gaussian_clip(0.035, 0.010, 0.02, 0.06)
            cap = int(random.randint(800, 1800))

        rows.append({
            "school_code": f"SCH{i:05d}",
            "school_name": f"{province}_{school_type}_{i:03d}",
            "school_type": school_type,
            "region": province,
            "tier": tier_defaults[school_type],
            "training_quality": tq,
            "reputation": rep,
            "resource_support": rs,
            "capacity_base": cap,
            "city_tier": city_tier,
        })

    return rows


def generate_employers(n: int):
    """
    生成企业数据。

    本版增加：
    - size_type
    - base_job_count
    """
    rows = []
    ind_weights = list(DEFAULT_CONSTRAINTS["industry_macro"]["industry_weights_for_employers"].items())
    anchors = DEFAULT_CONSTRAINTS["industry_macro"]["salary_anchor"]

    for i in range(1, n + 1):
        industry = weighted_choice(ind_weights)
        employer_type = weighted_choice(EMPLOYER_TYPE_WEIGHTS)
        size_type = weighted_choice(EMPLOYER_SIZE_WEIGHTS)

        city_name, city_tag, city_tier = sample_city()
        region = "东部" if city_tier >= 0.85 else ("中部" if city_tier >= 0.55 else "西部")
        anchor = anchors[industry]
        base_salary = random.randint(anchor["low"], anchor["high"])

        job_lo, job_hi = EMPLOYER_SIZE_JOB_COUNT_RANGE[size_type]
        base_job_count = random.randint(job_lo, job_hi)

        if industry in ("人工智能", "智能硬件"):
            mp = gaussian_clip(0.82, 0.08, 0.60, 0.95)
            sp = gaussian_clip(0.86, 0.06, 0.65, 0.98)
            ht = gaussian_clip(0.72, 0.07, 0.52, 0.90)
            ct = gaussian_clip(0.36, 0.10, 0.15, 0.65)
        elif industry in ("先进制造", "建筑工程", "医疗健康"):
            mp = gaussian_clip(0.70, 0.10, 0.45, 0.92)
            sp = gaussian_clip(0.76, 0.08, 0.50, 0.95)
            ht = gaussian_clip(0.64, 0.08, 0.45, 0.86)
            ct = gaussian_clip(0.45, 0.12, 0.20, 0.78)
        else:
            mp = gaussian_clip(0.56, 0.10, 0.35, 0.85)
            sp = gaussian_clip(0.63, 0.10, 0.45, 0.90)
            ht = gaussian_clip(0.56, 0.08, 0.42, 0.78)
            ct = gaussian_clip(0.66, 0.12, 0.30, 0.90)

        growth_base = anchor["heat"]
        if employer_type == "startup":
            growth = gaussian_clip(min(0.98, growth_base + 0.10), 0.08, 0.40, 0.98)
            stability = gaussian_clip(0.45, 0.12, 0.22, 0.72)
        elif employer_type == "state_owned":
            growth = gaussian_clip(growth_base - 0.05, 0.06, 0.30, 0.88)
            stability = gaussian_clip(0.86, 0.05, 0.65, 0.96)
        else:
            growth = gaussian_clip(growth_base, 0.08, 0.30, 0.95)
            stability = gaussian_clip(0.68, 0.10, 0.35, 0.95)

        rows.append({
            "employer_code": f"EMP{i:05d}",
            "employer_name": f"{industry}_{city_name}_{employer_type}_{i:03d}",
            "employer_type": employer_type,
            "industry": industry,
            "city": city_name,
            "region": region,
            "city_tier": city_tier,
            "base_salary": float(base_salary),
            "growth_factor": growth,
            "major_preference_strength": mp,
            "skill_preference_strength": sp,
            "hire_threshold": ht,
            "cross_major_tolerance": ct,
            "salary_elasticity": gaussian_clip(0.06 if employer_type == "startup" else 0.04, 0.015, 0.02, 0.12),
            "threshold_relax_speed": gaussian_clip(0.03, 0.01, 0.01, 0.06),
            "tolerance_increase_speed": gaussian_clip(0.03, 0.01, 0.01, 0.06),
            "threshold_tighten_speed": gaussian_clip(0.02, 0.008, 0.005, 0.05),
            "tolerance_decrease_speed": gaussian_clip(0.02, 0.008, 0.005, 0.05),
            "stability": stability,
            "size_type": size_type,
            "base_job_count": base_job_count,
        })

    return rows


def generate_jobs(
    n: int,
    employers: List[Dict],
    majors: List[Dict],
    mappings: List[Dict],
):
    """
    生成岗位数据。

    本版逻辑：
    1. 先按目标岗位专业占比选专业
    2. 再按专业-行业映射选行业
    3. 再在该行业优先抽匹配专业模板
    4. 再绑定到某个对应行业企业
    """
    rows = []

    major_name_to_code = build_major_name_to_code(majors)
    industry_major_map = build_industry_major_weight_map(mappings)

    employers_by_industry: Dict[str, List[Dict]] = {}
    for emp in employers:
        employers_by_industry.setdefault(emp["industry"], []).append(emp)

    major_to_industry_weights: Dict[str, Dict[str, float]] = {}
    for industry, major_scores in industry_major_map.items():
        for major_name, score in major_scores.items():
            major_to_industry_weights.setdefault(major_name, {})
            major_to_industry_weights[major_name][industry] = score

    industry_major_templates: Dict[str, Dict[str, List[Tuple]]] = {}
    for industry, tpls in JOB_TEMPLATES.items():
        industry_major_templates.setdefault(industry, {})
        for tpl in tpls:
            job_name, major_code, skill_req, sal_factor, cross_major = tpl
            major_name = next(
                (m["major_name"] for m in majors if m["major_code"] == major_code),
                None
            )
            if major_name is None:
                continue
            industry_major_templates[industry].setdefault(major_name, [])
            industry_major_templates[industry][major_name].append(tpl)

    target_job_share = normalize_weight_dict(SIM_MAJOR_JOB_SHARE)

    for i in range(1, n + 1):
        # 1. 先抽岗位目标专业
        major_name = weighted_choice_from_dict(target_job_share)
        major_code = major_name_to_code[major_name]

        # 2. 再抽与该专业相关的行业
        candidate_industries = major_to_industry_weights.get(major_name, {})
        if not candidate_industries:
            industry = weighted_choice(
                list(DEFAULT_CONSTRAINTS["industry_macro"]["industry_weights_for_employers"].items())
            )
        else:
            industry = weighted_choice_from_dict(candidate_industries)

        # 3. 选企业
        candidate_employers = employers_by_industry.get(industry, [])
        if candidate_employers:
            emp = random.choice(candidate_employers)
        else:
            emp = random.choice(employers)
            industry = emp["industry"]

        # 4. 优先在该行业下挑选与目标专业对应的模板
        tpl_pool = industry_major_templates.get(industry, {}).get(major_name, [])
        if tpl_pool:
            tpl = random.choice(tpl_pool)
        else:
            tpl = random.choice(JOB_TEMPLATES[industry])

        job_name, tpl_major_code, skill_req, sal_factor, cross_major = tpl

        # 最终仍采用目标专业，避免模板把专业带偏
        final_major_code = major_code

        salary_base = round(
            emp["base_salary"] * random.uniform(sal_factor * 0.95, sal_factor * 1.05),
            2
        )
        career_growth = gaussian_clip(
            (emp["growth_factor"] + DEFAULT_CONSTRAINTS["industry_macro"]["salary_anchor"][industry]["heat"]) / 2,
            0.08, 0.30, 0.98
        )
        industry_heat = gaussian_clip(
            DEFAULT_CONSTRAINTS["industry_macro"]["salary_anchor"][industry]["heat"],
            0.05, 0.20, 0.98
        )

        rows.append({
            "job_code": f"JOB{i:06d}",
            "job_name": job_name,
            "industry": industry,
            "major_code": final_major_code,
            "skill_required": skill_req,
            "salary_base": salary_base,
            "city": emp["city"],
            "cross_major_allowed": int(cross_major or emp["cross_major_tolerance"] > 0.55),
            "career_growth": career_growth,
            "city_tier": emp["city_tier"],
            "industry_heat": industry_heat,
        })

    return rows


def generate_students(n: int, majors: List[Dict], schools: List[Dict]):
    """
    生成学生数据。

    本版新增：
    1. home_region：家乡区域
    2. school_city / school_region：毕业学校所在城市与区域
    3. stay_school_city_preference：留在学校城市倾向
    4. go_big_city_preference：进入大城市倾向
    5. return_home_preference：回家乡倾向
    """
    rows = []
    major_by_name = {m["major_name"]: m for m in majors}

    school_type_boost = {
        "research_university": 0.10,
        "general_university": 0.04,
        "applied_university": -0.02,
        "vocational_undergraduate": -0.05,
    }

    target_student_share = normalize_weight_dict(SIM_MAJOR_STUDENT_SHARE)

    for i in range(1, n + 1):
        stu_type = weighted_choice(STUDENT_TYPE_WEIGHTS)

        # -----------------------------
        # 家乡区域：当前先沿用 region 作为家乡区域
        # 后续如果你有更细的省份/城市数据，可以继续细化为 home_city
        # -----------------------------
        province = sample_province()
        home_region = province

        # -----------------------------
        # 学校与学校所在城市
        # -----------------------------
        school = random.choice(schools)
        school_city = school.get("school_name", "").split("_")[0]
        school_region = school.get("region", province)

        # 当前 region 字段仍保留，用于兼容现有系统
        region = home_region

        # -----------------------------
        # 兴趣专业
        # -----------------------------
        major_name = weighted_choice_from_dict(target_student_share)
        major = major_by_name[major_name]

        boost = school_type_boost.get(school["school_type"], 0.0)
        ability_mu = 0.62 + boost
        learning_mu = 0.64 + boost * 0.7

        # -----------------------------
        # 基础行为画像
        # -----------------------------
        if stu_type == "salary_oriented":
            info = gaussian_clip(0.72, 0.10, 0.25, 0.98)
            risk = gaussian_clip(0.60, 0.15, 0.10, 0.95)
            growth_pref = gaussian_clip(0.70, 0.12, 0.20, 0.98)
            city_pref = "一线/超大城市"
            city_tier_pref = gaussian_clip(0.82, 0.10, 0.25, 1.00)

            stay_school_city_preference = gaussian_clip(0.32, 0.12, 0.05, 0.75)
            go_big_city_preference = gaussian_clip(0.82, 0.10, 0.30, 1.00)
            return_home_preference = gaussian_clip(0.20, 0.10, 0.00, 0.55)

        elif stu_type == "interest_oriented":
            info = gaussian_clip(0.56, 0.12, 0.20, 0.95)
            risk = gaussian_clip(0.48, 0.15, 0.10, 0.95)
            growth_pref = gaussian_clip(0.62, 0.14, 0.20, 0.98)
            city_pref = "本地优先"
            city_tier_pref = gaussian_clip(0.48, 0.18, 0.10, 1.00)

            stay_school_city_preference = gaussian_clip(0.56, 0.14, 0.15, 0.95)
            go_big_city_preference = gaussian_clip(0.38, 0.16, 0.05, 0.85)
            return_home_preference = gaussian_clip(0.42, 0.15, 0.05, 0.90)

        elif stu_type == "trend_sensitive":
            info = gaussian_clip(0.82, 0.08, 0.30, 0.99)
            risk = gaussian_clip(0.58, 0.15, 0.10, 0.95)
            growth_pref = gaussian_clip(0.78, 0.10, 0.25, 0.99)
            city_pref = "新一线/特大城市"
            city_tier_pref = gaussian_clip(0.76, 0.12, 0.10, 1.00)

            stay_school_city_preference = gaussian_clip(0.34, 0.12, 0.05, 0.80)
            go_big_city_preference = gaussian_clip(0.80, 0.10, 0.25, 1.00)
            return_home_preference = gaussian_clip(0.18, 0.10, 0.00, 0.50)

        elif stu_type == "prestige_oriented":
            info = gaussian_clip(0.76, 0.10, 0.25, 0.99)
            risk = gaussian_clip(0.42, 0.14, 0.10, 0.95)
            growth_pref = gaussian_clip(0.66, 0.12, 0.20, 0.98)
            city_pref = "一线/超大城市"
            city_tier_pref = gaussian_clip(0.88, 0.08, 0.30, 1.00)

            stay_school_city_preference = gaussian_clip(0.40, 0.12, 0.05, 0.85)
            go_big_city_preference = gaussian_clip(0.84, 0.08, 0.35, 1.00)
            return_home_preference = gaussian_clip(0.16, 0.08, 0.00, 0.45)

        else:
            # employment_oriented
            info = gaussian_clip(0.62, 0.12, 0.20, 0.98)
            risk = gaussian_clip(0.40, 0.15, 0.10, 0.95)
            growth_pref = gaussian_clip(0.58, 0.14, 0.20, 0.98)
            city_pref = "二线/大城市"
            city_tier_pref = gaussian_clip(0.64, 0.14, 0.10, 1.00)

            stay_school_city_preference = gaussian_clip(0.54, 0.14, 0.10, 0.95)
            go_big_city_preference = gaussian_clip(0.48, 0.16, 0.05, 0.90)
            return_home_preference = gaussian_clip(0.46, 0.14, 0.05, 0.90)

        ability = gaussian_clip(ability_mu, 0.12, 0.20, 0.98)
        learning_effort = gaussian_clip(learning_mu, 0.12, 0.20, 0.98)

        salary_base = major["salary_expectation"]
        expected_salary = round(
            salary_base * (
                0.90
                + ability * 0.18
                + city_tier_pref * 0.08
                + (0.05 if stu_type == "salary_oriented" else 0.0)
            ),
            2
        )

        gender = "female" if random.random() < 0.48 else "male"

        rows.append({
            "student_code": f"STU{i:06d}",
            "student_type": stu_type,
            "gender": gender,

            # 兼容现有系统字段
            "region": region,

            # 新增：家乡/学校位置信息
            "home_region": home_region,
            "school_city": school_city,
            "school_region": school_region,

            "ability": ability,
            "interest_major": major["major_name"],
            "city_preference": city_pref,
            "city_tier_preference": city_tier_pref,

            # 新增：三类城市去向偏好
            "stay_school_city_preference": stay_school_city_preference,
            "go_big_city_preference": go_big_city_preference,
            "return_home_preference": return_home_preference,

            "expected_salary": expected_salary,
            "risk_preference": risk,
            "information_level": info,
            "career_growth_preference": growth_pref,
            "learning_effort": learning_effort,
        })
    return rows


# -----------------------------
# 输出
# -----------------------------
TABLE_COLUMNS = {
    "majors": [
        "major_code", "major_name", "category", "skill_direction",
        "heat_init", "mobility", "salary_expectation", "policy_support_weight"
    ],
    "major_industry_mapping": [
        "major_name", "industry", "match_score"
    ],
    "schools": [
        "school_code", "school_name", "school_type", "region", "tier",
        "training_quality", "reputation", "resource_support", "capacity_base", "city_tier"
    ],
    "employers": [
        "employer_code", "employer_name", "employer_type", "industry",
        "city", "region", "city_tier", "base_salary", "growth_factor",
        "major_preference_strength", "skill_preference_strength",
        "hire_threshold", "cross_major_tolerance", "salary_elasticity",
        "threshold_relax_speed", "tolerance_increase_speed",
        "threshold_tighten_speed", "tolerance_decrease_speed",
        "stability", "size_type", "base_job_count"
    ],
    "jobs": [
        "job_code", "job_name", "industry", "major_code", "skill_required",
        "salary_base", "city", "cross_major_allowed", "career_growth",
        "city_tier", "industry_heat"
    ],
    "students": [
        "student_code",
        "student_type",
        "gender",
        "region",
        "home_region",
        "school_city",
        "school_region",
        "ability",
        "interest_major",
        "city_preference",
        "city_tier_preference",
        "stay_school_city_preference",
        "go_big_city_preference",
        "return_home_preference",
        "expected_salary",
        "risk_preference",
        "information_level",
        "career_growth_preference",
        "learning_effort",
    ],
}


def write_csv(path: Path, rows: List[Dict], cols: List[str]):
    """
    输出 CSV 文件。
    """
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k) for k in cols})


def sql_value(v):
    """
    将 Python 值转成 SQL 字面量。
    """
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{s}'"


def write_insert_sql(path: Path, table_name: str, rows: List[Dict], cols: List[str], chunk_size: int = 500):
    """
    输出 INSERT SQL 文件。
    """
    with path.open("w", encoding="utf-8") as f:
        if not rows:
            return

        for i in range(0, len(rows), chunk_size):
            chunk = rows[i:i + chunk_size]
            col_sql = ", ".join(f"`{c}`" for c in cols)
            values_sql = []
            for r in chunk:
                values_sql.append("(" + ", ".join(sql_value(r.get(c)) for c in cols) + ")")

            f.write(f"INSERT INTO `{table_name}` ({col_sql}) VALUES\n")
            f.write(",\n".join(values_sql))
            f.write(";\n\n")
def write_full_import_sql(path: Path, datasets: Dict[str, List[Dict]]):
    """
    生成一个可一次性清空并导入 6 个表的总 SQL 文件。

    文件内容包括：
    1. 关闭外键检查
    2. 清空 6 个表
    3. 依次插入 majors / major_industry_mapping / schools / employers / jobs / students
    4. 恢复外键检查
    """
    table_order = [
        "majors",
        "major_industry_mapping",
        "schools",
        "employers",
        "jobs",
        "students",
    ]

    truncate_order = [
        "jobs",
        "students",
        "employers",
        "schools",
        "major_industry_mapping",
        "majors",
    ]

    with path.open("w", encoding="utf-8") as f:
        f.write("-- ============\n")
        f.write("-- 一次性清空并导入 6 个表\n")
        f.write("-- 自动生成，请勿手工修改\n")
        f.write("-- ============\n\n")

        # 关闭外键检查
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

        # 先清空
        f.write("-- 清空旧数据\n")
        for table in truncate_order:
            f.write(f"TRUNCATE TABLE `{table}`;\n")
        f.write("\n")

        # 再导入
        for table in table_order:
            rows = datasets.get(table, [])
            cols = TABLE_COLUMNS[table]

            if not rows:
                continue

            f.write(f"-- 导入表：{table}\n")

            chunk_size = 500
            for i in range(0, len(rows), chunk_size):
                chunk = rows[i:i + chunk_size]
                col_sql = ", ".join(f"`{c}`" for c in cols)
                values_sql = []

                for r in chunk:
                    values_sql.append(
                        "(" + ", ".join(sql_value(r.get(c)) for c in cols) + ")"
                    )

                f.write(f"INSERT INTO `{table}` ({col_sql}) VALUES\n")
                f.write(",\n".join(values_sql))
                f.write(";\n\n")

        # 恢复外键检查
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

def generate_all(output_dir: Path, students_n: int, schools_n: int, employers_n: int, jobs_n: int):
    ensure_dir(output_dir)

    majors, mappings = generate_majors()
    schools = generate_schools(schools_n)
    employers = generate_employers(employers_n)
    jobs = generate_jobs(jobs_n, employers, majors, mappings)
    students = generate_students(students_n, majors, schools)

    datasets = {
        "majors": majors,
        "major_industry_mapping": mappings,
        "schools": schools,
        "employers": employers,
        "jobs": jobs,
        "students": students,
    }

    for table, rows in datasets.items():
        cols = TABLE_COLUMNS[table]
        write_csv(output_dir / f"{table}.csv", rows, cols)
        write_insert_sql(output_dir / f"{table}.sql", table, rows, cols)

    write_full_import_sql(output_dir / "all_seed.sql", datasets)

    summary = {
        "counts": {k: len(v) for k, v in datasets.items()},
        "files": [f"{k}.csv / {k}.sql" for k in datasets.keys()],
    }

    with (output_dir / "generation_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

def main():
    """
    命令行入口。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default="./seed_output")
    parser.add_argument("--students", type=int, default=10000)
    parser.add_argument("--schools", type=int, default=200)
    parser.add_argument("--employers", type=int, default=1000)
    parser.add_argument("--jobs", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    output_dir = Path(args.output)
    generate_all(output_dir, args.students, args.schools, args.employers, args.jobs)


if __name__ == "__main__":
    main()