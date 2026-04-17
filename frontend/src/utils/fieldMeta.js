// 参数说明与结果说明
// 这一版补齐了常用参数的 type / min / max / step / options
// 供 ConfigField.vue 自动渲染，并显示“中文（英文）+ 范围 + 步长”。

export const fieldMeta = {
  // 
  // 基础实验参数
  // 
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
  num_majors: {
    label: "专业数量",
    tooltip: "实验中涉及的专业类别数量。",
    type: "number",
    min: 1,
    step: 1,
  },
  num_job_types: {
    label: "岗位类型数量",
    tooltip: "实验中涉及的岗位类别数量。",
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
    tooltip: "用于控制随机过程的初始值。相同参数和相同种子通常会得到可复现结果。",
    type: "number",
    min: 0,
    step: 1,
  },
  seed_runs: {
    label: "随机种子重复次数",
    tooltip: "同一场景连续运行的随机种子数量。大于 1 时，系统返回聚合结果并保留每个种子的单独结果。",
    type: "number",
    min: 1,
    step: 1,
  },

  // 
  // 数据配置参数
  // 
  data_mode: {
    label: "数据模式",
    tooltip: "database 表示从数据库读取，synthetic 表示按规则生成，hybrid 表示数据库与生成数据混合。",
    type: "select",
    options: ["database", "synthetic", "hybrid"],
  },
  use_mock_data: {
    label: "使用模拟数据",
    tooltip: "是否优先使用模拟数据作为实验输入。",
    type: "checkbox",
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
  generate_if_missing: {
    label: "自动生成缺失数据",
    tooltip: "当外部数据不存在或不足时，是否自动生成补充数据。",
    type: "checkbox",
  },
  distribution_type: {
    label: "分布类型",
    tooltip: "生成模拟数据时采用的分布类型。",
    type: "select",
    options: ["normal", "uniform", "custom"],
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
  major_data_path: {
    label: "专业数据路径",
    tooltip: "外部专业数据文件路径。",
    type: "text",
  },
  job_data_path: {
    label: "岗位数据路径",
    tooltip: "外部岗位数据文件路径。",
    type: "text",
  },
  enable_unemployed_carryover: {
  label: "启用未就业滞留",
  tooltip: "开启后，上一轮未就业学生可按设定比例继续进入下一轮求职，用于模拟真实人才市场中的持续搜索行为。",
  type: "checkbox",
},

  // 
  // 学生决策参数
  // 
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
    tooltip: "学生在择业时对城市吸引力和城市层级的重视程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  region_weight: {
    label: "地区权重",
    tooltip: "学生在岗位选择中对地区偏好的重视程度。",
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
    tooltip: "学生接受跨专业学习或跨专业就业的倾向。",
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
  reservation_utility: {
    label: "最低接受效用阈值",
    tooltip: "学生接受岗位前的最低效用要求，低于该值时更可能继续求职。",
    type: "number",
    step: 0.01,
  },
  max_carryover_steps: {
    label: "最长滞留轮次",
    tooltip: "未就业学生最多可延续参与后续求职的轮次数。",
    type: "number",
    min: 0,
    step: 1,
  },
  carryover_fraction: {
    label: "滞留保留比例",
    tooltip: "上一轮未就业学生延续到下一轮继续求职的比例。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  carryover_skill_gain: {
    label: "滞留技能提升",
    tooltip: "学生在滞留求职期间因学习、训练或适应获得的技能增益。",
    type: "number",
    min: 0,
    step: 0.01,
  },
  max_carryover_steps: {
  label: "最大延续轮次",
  tooltip: "未就业学生最多允许连续进入后续多少轮求职。值越大，越接近现实中的持续求职过程。",
  type: "number",
  min: 0,
  step: 1,
},

carryover_fraction: {
  label: "延续比例",
  tooltip: "上一轮未就业学生中，有多少比例会继续进入下一轮求职。0表示不延续，1表示全部延续。",
  type: "number",
  min: 0,
  max: 1,
  step: 0.05,
},

  // 
  // 企业反馈参数
  // 
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
    tooltip: "当岗位招不满时，企业降低招聘阈值的速度。值越大，放宽标准越快。",
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
  threshold_tighten_speed: {
    label: "阈值收紧速度",
    tooltip: "企业在招聘顺利或市场变化下提高招聘阈值的速度。",
    type: "number",
    min: 0,
    step: 0.01,
  },
  tolerance_decrease_speed: {
    label: "跨专业容忍回调速度",
    tooltip: "企业在策略调整中降低跨专业容忍度的速度。",
    type: "number",
    min: 0,
    step: 0.01,
  },

  // 
  // 学校反馈参数
  // 
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

  // 
  // 场景参数
  // 
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
    label: "市场热度放大系数",
    tooltip: "市场热度对学生选择行为的放大程度。",
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
  migration_cost_weight: {
    label: "迁移成本权重",
    tooltip: "学生在跨地区、跨城市流动时对迁移成本的敏感程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  matching_rounds_per_step: {
    label: "每轮撮合轮数",
    tooltip: "每个仿真步内执行岗位撮合的轮次数。",
    type: "number",
    min: 1,
    step: 1,
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
  satisfaction_threshold: {
    label: "低满意度阈值",
    tooltip: "用于判断学生就业结果是否属于低满意状态的阈值。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },

  // 
  // 机制开关 / 类型参数
  // 
  enable_social_influence: {
    label: "启用社会影响",
    tooltip: "是否考虑学生之间的同伴影响与扎堆效应。",
    type: "checkbox",
  },
  enable_information_delay: {
    label: "启用信息延迟",
    tooltip: "是否考虑市场信息传播存在时间延迟。",
    type: "checkbox",
  },
  enable_feedback_adjustment: {
    label: "启用反馈调节",
    tooltip: "是否允许学校和企业根据结果动态调整策略。",
    type: "checkbox",
  },
  enable_unemployed_carryover: {
    label: "启用未就业滞留",
    tooltip: "是否允许未就业学生延续到下一轮继续求职。",
    type: "checkbox",
  },
  enable_regional_preference: {
    label: "启用地区偏好",
    tooltip: "是否在学生决策中考虑地区偏好与迁移成本。",
    type: "checkbox",
  },
  herd_strength: {
    label: "扎堆强度",
    tooltip: "学生受到热门专业或热门岗位吸引而集中选择的程度。",
    type: "number",
    min: 0,
    step: 0.01,
  },
  social_network_density: {
    label: "社交网络密度",
    tooltip: "学生之间信息传播与相互影响的连接程度。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  info_delay_steps: {
    label: "信息延迟步数",
    tooltip: "市场信息传递到学生决策端所延迟的步数。",
    type: "number",
    min: 0,
    step: 1,
  },
  employment_oriented_ratio: {
    label: "就业导向学生占比",
    tooltip: "以就业结果优先为主的学生群体占比。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  interest_oriented_ratio: {
    label: "兴趣导向学生占比",
    tooltip: "以个人兴趣偏好优先为主的学生群体占比。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  prestige_oriented_ratio: {
    label: "声望导向学生占比",
    tooltip: "以学校、专业或岗位声望为优先的学生群体占比。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  trend_sensitive_ratio: {
    label: "趋势敏感学生占比",
    tooltip: "容易受市场热度和趋势波动影响的学生群体占比。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  research_university_ratio: {
    label: "研究型大学占比",
    tooltip: "研究型高校在学校总体中的占比。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  applied_university_ratio: {
    label: "应用型大学占比",
    tooltip: "应用型高校在学校总体中的占比。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  vocational_college_ratio: {
    label: "职业院校占比",
    tooltip: "职业院校在学校总体中的占比。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  tech_strict_ratio: {
    label: "技术严格企业占比",
    tooltip: "对技能和专业要求更严格的企业占比。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  growth_firm_ratio: {
    label: "成长型企业占比",
    tooltip: "成长型企业在企业总体中的占比。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  traditional_firm_ratio: {
    label: "传统企业占比",
    tooltip: "传统稳定型企业在总体中的占比。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },
  cost_sensitive_ratio: {
    label: "成本敏感企业占比",
    tooltip: "对薪资成本更敏感的企业占比。",
    type: "number",
    min: 0,
    max: 1,
    step: 0.01,
  },

  // 
  // LLM 参数
  // 
  enabled: {
    label: "启用大模型",
    tooltip: "是否启用大模型增强模块。",
    type: "checkbox",
  },
  provider: {
    label: "模型服务商",
    tooltip: "大模型服务提供方，例如 OpenAI、阿里云等。",
    type: "text",
  },
  model_name: {
    label: "模型名称",
    tooltip: "调用大模型时使用的模型名称。",
    type: "text",
  },
  use_for_agent_decision: {
    label: "用于主体决策",
    tooltip: "是否允许大模型直接参与学生、学校或企业主体的决策过程。",
    type: "checkbox",
  },
  use_for_analysis: {
    label: "用于结果分析",
    tooltip: "是否允许大模型参与实验结果分析与诊断。",
    type: "checkbox",
  },
  use_for_scenario_generation: {
    label: "用于场景生成",
    tooltip: "是否允许大模型根据自然语言描述生成场景参数建议。",
    type: "checkbox",
  },
  use_for_profile_generation: {
    label: "用于画像生成",
    tooltip: "是否允许大模型生成主体画像或类型特征。",
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
  temperature: {
    label: "温度参数",
    tooltip: "控制大模型输出的随机性，越高越发散。",
    type: "number",
    min: 0,
    max: 2,
    step: 0.1,
  },
  max_tokens: {
    label: "最大输出长度",
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