from collections import defaultdict
from mesa import Agent


class SchoolAgent(Agent):
    """
    学校主体：
    1. 记录专业层面的反馈历史
    2. 基于长时滞调整专业容量
    3. 基于扩招压力调整培养质量
    """

    def __init__(self, unique_id, model, name, major_capacity, school_type, profile):
        super().__init__(model)
        self.unique_id = unique_id
        self.name = name
        self.major_capacity = major_capacity
        self.school_type = school_type
        self.profile = profile or {}

        # 学校整体培养质量
        self.training_quality = float(
            self.profile.get(
                "training_quality",
                self.model.school_config.get("training_quality", 0.7),
            )
        )

        # 记录每个专业的历史反馈
        self.major_feedback_history = defaultdict(list)

        # 记录基线总容量，用于判断是否过度扩招
        self.baseline_total_capacity = sum(self.major_capacity.values())

    def record_feedback(self):
        """
        记录本轮反馈信号。
        反馈来源包括：
        1. 专业就业率
        2. 专业市场热度
        3. 政策支持强度
        """
        for major in self.model.majors:
            major_stats = self.model.last_round_major_stats.get(major, {})
            employment_rate = major_stats.get("employment_rate", 0.5)
            market_heat = self.model.major_market_heat.get(major, 0.7)
            policy_support = self.model.scenario_config.get("policy_support", 0.5)

            self.major_feedback_history[major].append({
                "employment_rate": employment_rate,
                "market_heat": market_heat,
                "policy_support": policy_support,
            })

    def adjust_major_capacity(self):
        """
        基于长时滞反馈调整专业容量。
        学校反馈慢于企业，因此采用历史窗口平均值。

        同时把本轮各专业的容量调整偏置写回模型，
        供结构分析模块展示。
        """
        lag = int(self.model.school_feedback_lag)
        speed = float(self.model.school_config.get("capacity_adjust_speed", 0.1))
        employment_weight = float(self.model.school_config.get("employment_feedback_weight", 0.6))
        market_weight = float(self.model.school_config.get("market_feedback_weight", 0.4))

        for major in self.model.majors:
            history = self.major_feedback_history.get(major, [])
            if not history:
                continue

            recent_history = history[-lag:]

            avg_employment = sum(x["employment_rate"] for x in recent_history) / len(recent_history)
            avg_market_heat = sum(x["market_heat"] for x in recent_history) / len(recent_history)
            avg_policy_support = sum(x["policy_support"] for x in recent_history) / len(recent_history)

            # 学校综合反馈信号
            signal = (
                employment_weight * avg_employment
                + market_weight * avg_market_heat
                + 0.2 * avg_policy_support
            )

            old_capacity = self.major_capacity.get(major, 20)

            # 以 0.7 作为中性点
            adjustment_factor = 1 + speed * (signal - 0.7)
            new_capacity = max(5, round(old_capacity * adjustment_factor))

            self.major_capacity[major] = new_capacity

            # 记录该学校在该专业上的相对调整偏置
            # 正值表示扩招，负值表示缩招
            bias = 0.0
            if old_capacity > 0:
                bias = (new_capacity - old_capacity) / old_capacity

            if major not in self.model.major_school_adjustment_bias:
                self.model.major_school_adjustment_bias[major] = []

            self.model.major_school_adjustment_bias[major].append(bias)
            print(f"DEBUG school={self.name}, major={major}, old={old_capacity}, new={new_capacity}, bias={bias}")

    def adjust_training_quality(self):
        """
        调整培养质量：
        1. 扩招过快 -> 质量下降
        2. 有资源支持 -> 质量恢复
        """
        current_total_capacity = sum(self.major_capacity.values())
        expansion_ratio = current_total_capacity / max(self.baseline_total_capacity, 1)

        # 扩招惩罚：当总容量超过基线时，培养质量开始下降
        overcrowding_penalty = max(0.0, expansion_ratio - 1.0) * 0.05

        # 资源支持：来自 profile 或默认值
        resource_support = float(self.profile.get("resource_support", 0.03))

        self.training_quality = self.training_quality + resource_support - overcrowding_penalty
        self.training_quality = max(0.4, min(1.0, self.training_quality))

        # 回写 profile，供模型统计平均培养质量
        self.profile["training_quality"] = self.training_quality

    def adjust_capacity(self):
        """
        兼容旧接口。
        """
        self.adjust_major_capacity()