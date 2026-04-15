// 参数说明与结果说明
// 这一版补齐了常用参数的 type / min / max / step / options
// 供 ConfigField.vue 自动渲染，并显示“范围 + 步长”。

export const fieldMeta = {
  // =========================
  // 基础实验参数
  // =========================
  num_students: {
    label: "学生数量",
    tooltip: "本次实验请求的学生数量。若使用 database 模式，最终实际参与数量以数据库实际加载结果为准。",
    type: "number",
    min: 1,
    step: 1,
  },
  num_schools: {
    label: "学校数量",
    tooltip: "本次实验请求的学校数量。若使用 database 模式，最终实际参与数量以数据库实际加载结果为准。",
    type: "number",
    min: 1,
    step: 1,
  },
  num_employers: {
    label: "企业数量",
    tooltip: "本次实验请求的企业数量。若使用 database 模式，最终实际参与数量以数据库实际加载结果为准。",
    type: "number",
    min: 1,
    step: 1,
  },
  steps: {
    label: "仿真轮次",
    tooltip: "系统运行的时间步数量。轮次越多，越适合观察供需错配和反馈演化过程。",
    type: "number",
    min: 1,
    step: 1,
  },
  random_seed: {
    label: "随机种子",
    tooltip: "用于控制随机过程的初始值。相同参数和相同种子通常会得到可复现的结果。",
    type: "number",
    min: 0,
    step: 1,
  },

  // =========================
  // 数据配置参数
  // =========================
  data_mode: {
    label: "数据模式",
    tooltip: "database 表示从数据库读取，synthetic 表示按规则生成，hybrid 表示数据库与生成数据混合。",
    type: "select",
    options: ["database", "synthetic", "hybrid"],
  },
  use_census_distribution: {
    label: "按人口分布生成",
    tooltip: "是否按人口普查或预设分布规则生成模拟主体。",
    type: "checkbox",
  },
  auto_generate_missing_data: {
    label: "自动补齐缺失数据",
    tooltip: "当数据库主体数量不足时，是否自动按规则补齐主体。",
    type: "checkbox",
  },
  student_data_path: {
    label: "学生数据路径",
    tooltip: "外部学生数据文件路径。当前阶段可留空，后续支持导入。",
    type: "text",
  },
  school_data_path: {
    label: "学校数据路径",
    tooltip: "外部学校数据文件路径。当前阶段可留空，后续支持导入。",
    type: "text",
  },
  employer_data_path: {
    label: "企业数据路径",
    tooltip: "外部企业数据文件路径。当前阶段可留空，后续支持导入。",
    type: "text",
  },

  // =========================
  // 学生决策参数
  // =========================
  interest_weight: {
    label: "兴趣权重",
    tooltip: "学生在选择专业和岗位时，对个人兴趣偏好的重视程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  salary_weight: {
    label: "薪资权重",
    tooltip: "学生在决策中对薪资水平的重视程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  major_weight: {
    label: "专业匹配权重",
    tooltip: "学生在求职时对专业对口程度的重视程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  city_weight: {
    label: "城市偏好权重",
    tooltip: "学生在择业时对城市吸引力和地域偏好的重视程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  market_signal_weight: {
    label: "市场信号权重",
    tooltip: "学生在决策时受市场热度、就业率和薪资趋势等外部信号影响的程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  cross_major_acceptance: {
    label: "跨专业接受度",
    tooltip: "学生接受跨专业学习或就业的倾向。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  information_transparency: {
    label: "信息透明度",
    tooltip: "学生获取市场信息的充分程度。越高表示越接近真实市场信号。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  max_applications_per_step: {
    label: "每轮最大投递数",
    tooltip: "学生在每一轮仿真中最多投递的岗位数量。",
    type: "number",
    min: 1,
    step: 1,
  },

  // =========================
  // 企业反馈参数
  // =========================
  major_preference_strength: {
    label: "专业偏好强度",
    tooltip: "企业招聘时对专业对口程度的重视程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  skill_preference_strength: {
    label: "技能偏好强度",
    tooltip: "企业招聘时对技能匹配程度的重视程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  hire_threshold: {
    label: "招聘阈值",
    tooltip: "企业录用候选人的最低评分要求。越高表示招聘更严格。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  cross_major_tolerance: {
    label: "跨专业容忍度",
    tooltip: "企业接受非本专业候选人的程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  salary_elasticity: {
    label: "薪资弹性",
    tooltip: "当岗位空缺较高时，企业提高薪资的幅度。",
    type: "number",
    min: 0,
    step: 0.01,
  },
  threshold_relax_speed: {
    label: "阈值放宽速度",
    tooltip: "当岗位招不满时，企业降低招聘阈值的速度。值越大，企业越快放宽标准。",
    type: "number",
    min: 0,
    step: 0.01,
  },
  tolerance_increase_speed: {
    label: "跨专业放宽速度",
    tooltip: "当岗位招不满时，企业提高跨专业容忍度的速度。",
    type: "number",
    min: 0,
    step: 0.01,
  },

  // =========================
  // 学校反馈参数
  // =========================
  training_quality: {
    label: "培养质量",
    tooltip: "学校对学生能力提升的支持程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  capacity_adjust_speed: {
    label: "容量调整速度",
    tooltip: "学校根据反馈调整专业容量的速度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  employment_feedback_weight: {
    label: "就业反馈权重",
    tooltip: "学校在调整专业规模时，对就业结果的重视程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  market_feedback_weight: {
    label: "市场反馈权重",
    tooltip: "学校在调整专业规模时，对市场热度与岗位需求信号的重视程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  adjustment_lag: {
    label: "调整滞后",
    tooltip: "学校内部机制响应市场变化的滞后期。",
    type: "number",
    min: 0,
    step: 1,
  },
  resource_support: {
    label: "资源支持强度",
    tooltip: "学校在扩招或培养压力下维持教学质量的资源支撑能力。",
    type: "number",
    min: 0,
    step: 0.01,
  },

  // =========================
  // 场景参数
  // =========================
  macro_economy: {
    label: "宏观景气度",
    tooltip: "宏观经济环境对岗位总需求的影响系数。",
    type: "number",
    min: 0,
    step: 0.01,
  },
  policy_support: {
    label: "政策支持强度",
    tooltip: "政策对人才培养、就业引导和产业支持的影响程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  industry_boom_factor: {
    label: "产业繁荣因子",
    tooltip: "产业景气程度对企业岗位需求增长的放大作用。",
    type: "number",
    min: 0,
    step: 0.01,
  },
  market_heat_amplification: {
    label: "热门专业放大系数",
    tooltip: "市场热度对学生选择的放大程度。",
    type: "number",
    min: 0,
    step: 0.01,
  },
  city_attractiveness_gap: {
    label: "城市吸引力差异",
    tooltip: "不同城市在岗位机会、收入和生活条件上的差异程度。",
    type: "number",
    min: 0,
    step: 0.01,
  },
  technology_change_rate: {
    label: "技术变迁速度",
    tooltip: "产业技能需求变化的速度。",
    type: "number",
    min: 0,
    step: 0.01,
  },
  information_shock: {
    label: "信息冲击强度",
    tooltip: "突发信息、舆论热点或市场消息对学生决策的短期影响程度。",
    type: "number",
    min: 0,
    step: 0.01,
  },
  enterprise_feedback_lag: {
    label: "企业反馈时滞",
    tooltip: "企业每隔多少轮才根据招聘结果调整一次策略。值越小反馈越快。",
    type: "number",
    min: 1,
    step: 1,
  },
  school_feedback_lag: {
    label: "学校反馈时滞",
    tooltip: "学校每隔多少轮才根据就业与市场反馈调整容量和培养质量。值越大反馈越慢。",
    type: "number",
    min: 1,
    step: 1,
  },

  // =========================
  // LLM 参数
  // =========================
  enabled: {
    label: "启用大模型",
    tooltip: "是否启用大模型增强模块。",
    type: "checkbox",
  },
  use_for_scenario_generation: {
    label: "用于场景生成",
    tooltip: "是否允许大模型根据自然语言描述生成场景参数建议。",
    type: "checkbox",
  },
  use_for_result_explanation: {
    label: "用于结果解释",
    tooltip: "是否允许大模型根据实验结果生成解释文本。",
    type: "checkbox",
  },
  use_for_report_generation: {
    label: "用于报告生成",
    tooltip: "是否允许大模型生成实验分析报告。",
    type: "checkbox",
  },
  model_name: {
    label: "模型名称",
    tooltip: "调用大模型时使用的模型名称。",
    type: "text",
  },
  temperature: {
    label: "temperature",
    tooltip: "控制大模型输出的随机性，越高越发散。",
    type: "number",
    min: 0,
    max: 2,
    step: 0.1,
  },
  max_tokens: {
    label: "max_tokens",
    tooltip: "大模型一次输出允许的最大 token 数量。",
    type: "number",
    min: 1,
    step: 1,
  },
};

export const resultMeta = {
  employment_rate: {
    label: "累计就业率",
    tooltip: "截至当前轮，已就业学生占全部学生的比例。",
  },
  matching_rate: {
    label: "累计对口率",
    tooltip: "截至当前轮，已就业学生中专业与岗位对口的比例。",
  },
  cross_major_rate: {
    label: "累计跨专业率",
    tooltip: "截至当前轮，已就业学生中从事非本专业岗位的比例。",
  },
  avg_salary: {
    label: "累计平均薪资",
    tooltip: "截至当前轮，已就业学生岗位薪资的平均值。",
  },
  avg_satisfaction: {
    label: "累计满意度",
    tooltip: "截至当前轮，已就业学生对岗位结果的平均满意度。",
  },
  round_new_employment_rate: {
    label: "本轮新增就业率",
    tooltip: "本轮新就业学生占全部学生的比例。",
  },
  round_job_count: {
    label: "本轮岗位数",
    tooltip: "本轮企业发布的岗位总数。",
  },
  round_filled_jobs: {
    label: "本轮已填岗位",
    tooltip: "本轮成功完成招聘的岗位数量。",
  },
  round_vacancy_rate: {
    label: "本轮空缺率",
    tooltip: "本轮岗位中未被填补的比例。",
  },
  active_job_seekers: {
    label: "活跃求职人数",
    tooltip: "当前轮结束后仍未就业、仍处于求职状态的学生数量。",
  },
  mismatch_index: {
    label: "结构错配指数",
    tooltip: "学生专业供给结构与岗位需求结构之间的偏差程度。",
  },
  herding_index: {
    label: "扎堆指数",
    tooltip: "学生集中选择热门专业的程度，越大表示越扎堆。",
  },
  avg_hire_threshold: {
    label: "平均招聘阈值",
    tooltip: "当前企业整体平均招聘门槛。",
  },
  avg_cross_major_tolerance: {
    label: "平均跨专业容忍度",
    tooltip: "当前企业整体平均跨专业接受程度。",
  },
  avg_training_quality: {
    label: "平均培养质量",
    tooltip: "当前学校整体平均培养质量水平。",
  },
};