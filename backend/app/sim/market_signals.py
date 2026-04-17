# backend/app/sim/market_signals.py
# 市场信号模块 - 处理需求侧变化，生成学生可感知的市场信号
# 信息延迟感知、信号噪声、社会影响等因素共同作用，形成学生的市场热度感知

import random

def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, float(value)))

def get_delayed_market_heat(model, major):
    """
    Return the market heat visible to agents after optional information delay.
    """
    delay_enabled = bool(model.type_config.get("enable_information_delay", True))
    delay_steps = int(model.type_config.get("info_delay_steps", 1)) if delay_enabled else 0

    history = getattr(model, "major_market_heat_history", []) or []
    if delay_steps > 0 and len(history) > delay_steps:
        return float(history[-1 - delay_steps].get(major, model.major_market_heat.get(major, 1.0)))

    return float(model.major_market_heat.get(major, 1.0))


def perceive_market_heat(model, major, rng=None, information_level=None, transparency=None):
    """
    Convert true market heat into an agent's perceived signal.

    information_level and information_transparency jointly reduce noise.
    information_shock shifts perceived heat without changing true demand.
    """
    rng = rng or random

    base_transparency = (
        float(transparency)
        if transparency is not None
        else float(model.student_config.get("information_transparency", 0.8))
    )
    if information_level is not None:
        base_transparency = 0.5 * base_transparency + 0.5 * float(information_level)

    signal_transparency = clamp(base_transparency)

    true_heat = get_delayed_market_heat(model, major)
    information_shock = float(model.scenario_config.get("information_shock", 0.0))
    shocked_heat = max(0.1, true_heat * (1.0 + information_shock))

    noisy_signal = shocked_heat * rng.uniform(0.7, 1.3)
    return signal_transparency * shocked_heat + (1.0 - signal_transparency) * noisy_signal


def get_social_major_score(model, major):
    """
    Return a 0-1 popularity score from the previous cohort distribution.
    """
    if not bool(model.type_config.get("enable_social_influence", True)):
        return 0.0

    distribution = getattr(model, "previous_major_distribution", {}) or {}
    if not distribution:
        return 0.0

    max_share = max(distribution.values()) if distribution else 0.0
    if max_share <= 0:
        return 0.0

    return clamp(distribution.get(major, 0.0) / max_share)

