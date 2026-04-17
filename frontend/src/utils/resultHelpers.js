// 结果处理工具

/**
 * 获取最新一步结果
 * @param {object|null} result 完整结果对象
 * @returns {object|null}
 */
export function getLatestResult(result) {
  if (!result || !Array.isArray(result.results) || result.results.length === 0) {
    return null;
  }
  return result.results[result.results.length - 1];
}

/**
 * 构造分组结果卡片
 * @param {object|null} latest 最新一步结果
 * @returns {Array}
 */
export function buildGroupedStatCards(latest) {
  if (!latest) {
    return [];
  }

  return [
    {
      groupKey: "cumulative",
      groupTitle: "累计结果指标",
      cards: [
        {
          key: "employment_rate",
          title: "累计就业率",
          value: formatPercent(latest.employment_rate),
          tooltip: "截至当前轮，已就业学生占全部学生的比例。",
        },
        {
          key: "matching_rate",
          title: "累计对口率",
          value: formatPercent(latest.matching_rate),
          tooltip: "截至当前轮，已就业学生中专业与岗位对口的比例。",
        },
        {
          key: "cross_major_rate",
          title: "累计跨专业率",
          value: formatPercent(latest.cross_major_rate),
          tooltip: "截至当前轮，已就业学生中从事非本专业岗位的比例。",
        },
        {
          key: "avg_salary",
          title: "累计平均薪资",
          value: formatNumber(latest.avg_salary),
          tooltip: "截至当前轮，已就业学生岗位薪资的平均值。",
        },
        {
          key: "avg_satisfaction",
          title: "累计满意度",
          value: formatNumber(latest.avg_satisfaction),
          tooltip: "截至当前轮，已就业学生对岗位结果的平均满意度。",
        },
        {
          key: "low_satisfaction_employment_rate",
          title: "低满意就业率",
          value: formatPercent(latest.low_satisfaction_employment_rate),
          tooltip: "已就业学生中满意度低于阈值的比例。",
        },
        {
          key: "same_region_employment_rate",
          title: "同区域就业率",
          value: formatPercent(latest.same_region_employment_rate),
          tooltip: "已就业学生中岗位区域与学生来源区域一致的比例。",
        },
        {
          key: "new_cohort_employment_rate",
          title: "新生就业率",
          value: formatPercent(latest.new_cohort_employment_rate),
          tooltip: "本轮新进入市场学生中的就业比例，用于区分新增供给与滞留求职者。",
        },
        {
          key: "carryover_employment_rate",
          title: "滞留就业率",
          value: formatPercent(latest.carryover_employment_rate),
          tooltip: "由上一轮延续进入市场的未就业学生在本轮结束时的就业比例。",
        },
        {
          key: "carryover_pool_share",
          title: "滞留池占比",
          value: formatPercent(latest.carryover_pool_share),
          tooltip: "当前市场中滞留求职者占全部学生的比例。",
        },
      ],
    },
    {
      groupKey: "flow",
      groupTitle: "本轮流量指标",
      cards: [
        {
          key: "round_new_employment_rate",
          title: "本轮新增就业率",
          value: formatPercent(latest.round_new_employment_rate),
          tooltip: "本轮新就业学生占全部学生的比例。",
        },
        {
          key: "round_job_count",
          title: "本轮岗位数",
          value: formatInteger(latest.round_job_count),
          tooltip: "本轮企业实际发布的岗位总数。",
        },
        {
          key: "round_filled_jobs",
          title: "本轮已填岗位",
          value: formatInteger(latest.round_filled_jobs),
          tooltip: "本轮成功完成招聘的岗位数量。",
        },
        {
          key: "round_vacancy_rate",
          title: "本轮空缺率",
          value: formatPercent(latest.round_vacancy_rate),
          tooltip: "本轮发布岗位中未被填补的比例。",
        },
        {
          key: "active_job_seekers",
          title: "活跃求职人数",
          value: formatInteger(latest.active_job_seekers),
          tooltip: "当前轮结束后仍未就业、仍属于求职状态的学生数量。",
        },
        {
          key: "round_application_count",
          title: "本轮申请数",
          value: formatInteger(latest.round_application_count),
          tooltip: "本轮学生向企业岗位提交的申请总量。",
        },
        {
          key: "round_offer_count",
          title: "本轮Offer数",
          value: formatInteger(latest.round_offer_count),
          tooltip: "本轮企业向学生发出的 offer 数量。",
        },
        {
          key: "avg_applications_per_job",
          title: "岗位竞争度",
          value: formatNumber(latest.avg_applications_per_job),
          tooltip: "平均每个岗位收到的申请数量。",
        },
        {
          key: "carryover_student_count",
          title: "滞留求职人数",
          value: formatInteger(latest.carryover_student_count),
          tooltip: "由上一轮未就业学生延续进入本轮市场的人数。",
        },
      ],
    },
    {
      groupKey: "structure",
      groupTitle: "结构与反馈指标",
      cards: [
        {
          key: "mismatch_index",
          title: "结构错配指数",
          value: formatNumber(latest.mismatch_index),
          tooltip: "学生专业供给结构与岗位需求结构之间的偏差程度。",
        },
        {
          key: "herding_index",
          title: "扎堆指数",
          value: formatNumber(latest.herding_index),
          tooltip: "学生集中选择热门专业的程度，越大表示越扎堆。",
        },
        {
          key: "avg_hire_threshold",
          title: "平均招聘阈值",
          value: formatNumber(latest.avg_hire_threshold),
          tooltip: "当前企业整体平均招聘门槛。",
        },
        {
          key: "avg_cross_major_tolerance",
          title: "平均跨专业容忍度",
          value: formatNumber(latest.avg_cross_major_tolerance),
          tooltip: "当前企业整体平均跨专业接受程度。",
        },
        {
          key: "avg_training_quality",
          title: "平均培养质量",
          value: formatNumber(latest.avg_training_quality),
          tooltip: "当前学校整体平均培养质量水平。",
        },
      ],
    },
  ];
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return `${(value * 100).toFixed(1)}%`;
}

function formatNumber(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return Number(value).toFixed(3);
}

function formatInteger(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return String(Math.round(value));
}
