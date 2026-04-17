function baseGrid(overrides = {}) {
  return {
    left: 60,
    right: 24,
    top: 78,
    bottom: 48,
    containLabel: true,
    ...overrides,
  };
}

function baseLegend(overrides = {}) {
  return {
    top: 6,
    left: 8,
    right: 8,
    type: "scroll",
    ...overrides,
  };
}

export function buildEmploymentChartOption(results = []) {
  return {
    tooltip: { trigger: "axis" },
    legend: baseLegend(),
    grid: baseGrid(),
    xAxis: {
      type: "category",
      data: results.map((x) => x.step),
      name: "轮次",
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 1,
      name: "比例",
    },
    series: [
      {
        name: "累计就业率",
        type: "line",
        smooth: true,
        data: results.map((x) => x.employment_rate),
      },
      {
        name: "本轮新增就业率",
        type: "line",
        smooth: true,
        data: results.map((x) => x.round_new_employment_rate),
      },
      {
        name: "本轮新生就业率",
        type: "line",
        smooth: true,
        data: results.map((x) => x.new_cohort_employment_rate ?? 0),
      },
    ],
  };
}

export function buildVacancyChartOption(results = []) {
  return {
    tooltip: { trigger: "axis" },
    legend: baseLegend(),
    grid: baseGrid({ right: 48 }),
    xAxis: {
      type: "category",
      data: results.map((x) => x.step),
      name: "轮次",
    },
    yAxis: [
      {
        type: "value",
        min: 0,
        max: 1,
        name: "空缺率",
      },
      {
        type: "value",
        min: 0,
        name: "岗位数",
      },
    ],
    series: [
      {
        name: "本轮空缺率",
        type: "line",
        smooth: true,
        data: results.map((x) => x.round_vacancy_rate),
        yAxisIndex: 0,
      },
      {
        name: "本轮已填岗位数",
        type: "bar",
        data: results.map((x) => x.round_filled_jobs),
        yAxisIndex: 1,
      },
      {
        name: "本轮岗位数",
        type: "bar",
        data: results.map((x) => x.round_job_count),
        yAxisIndex: 1,
      },
    ],
  };
}

export function buildOfferFunnelChartOption(results = []) {
  const latest = results.length ? results[results.length - 1] : {};
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: baseGrid({ top: 40 }),
    xAxis: {
      type: "category",
      data: ["申请", "Offer", "接受", "拒绝"],
    },
    yAxis: {
      type: "value",
      min: 0,
      name: "数量",
    },
    series: [
      {
        name: "最后一轮",
        type: "bar",
        data: [
          latest.round_application_count || 0,
          latest.round_offer_count || 0,
          latest.round_accepted_offer_count || 0,
          latest.round_rejected_offer_count || 0,
        ],
      },
    ],
  };
}

export function buildCarryoverTrendChartOption(results = []) {
  return {
    tooltip: { trigger: "axis" },
    legend: baseLegend(),
    grid: baseGrid({ right: 56 }),
    xAxis: {
      type: "category",
      data: results.map((x) => x.step),
      name: "轮次",
    },
    yAxis: [
      {
        type: "value",
        min: 0,
        name: "人数",
      },
      {
        type: "value",
        min: 0,
        max: 1,
        name: "比例",
      },
    ],
    series: [
      {
        name: "滞留求职人数",
        type: "bar",
        data: results.map((x) => x.carryover_student_count || 0),
        yAxisIndex: 0,
      },
      {
        name: "滞留就业率",
        type: "line",
        data: results.map((x) => x.carryover_employment_rate || 0),
        smooth: true,
        yAxisIndex: 1,
      },
      {
        name: "本轮新生就业率",
        type: "line",
        data: results.map((x) => x.new_cohort_employment_rate || 0),
        smooth: true,
        yAxisIndex: 1,
      },
    ],
  };
}

export function buildRegionalGapChartOption(structureAnalysis = {}) {
  const rows = structureAnalysis?.regional_flow_metrics?.rows || [];
  return {
    tooltip: { trigger: "axis" },
    legend: baseLegend(),
    grid: baseGrid(),
    xAxis: {
      type: "category",
      data: rows.map((x) => x.region),
      axisLabel: { interval: 0 },
    },
    yAxis: {
      type: "value",
      name: "数量",
    },
    series: [
      {
        name: "学生供给",
        type: "bar",
        data: rows.map((x) => x.student_count || 0),
      },
      {
        name: "岗位需求",
        type: "bar",
        data: rows.map((x) => x.job_count || 0),
      },
      {
        name: "就业吸纳",
        type: "bar",
        data: rows.map((x) => x.employed_job_count || 0),
      },
    ],
  };
}

export function buildMajorHeatChartOption(structureAnalysis = {}) {
  const rows = structureAnalysis?.major_market_signals || [];
  return {
    tooltip: { trigger: "axis" },
    legend: baseLegend(),
    grid: baseGrid({ bottom: 60 }),
    xAxis: {
      type: "category",
      data: rows.map((x) => x.major),
      axisLabel: { interval: 0, rotate: 18 },
    },
    yAxis: {
      type: "value",
      min: 0,
      name: "强度",
    },
    series: [
      {
        name: "市场热度",
        type: "bar",
        data: rows.map((x) => x.market_heat || 0),
      },
      {
        name: "薪资信号",
        type: "bar",
        data: rows.map((x) => x.salary_signal || 0),
      },
      {
        name: "空缺率",
        type: "line",
        smooth: true,
        data: rows.map((x) => x.vacancy_rate || 0),
      },
    ],
  };
}
