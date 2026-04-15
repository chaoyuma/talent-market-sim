// 图表 option 构建工具

/**
 * 就业相关图表：
 * 同时展示累计就业率与本轮新增就业率
 * @param {Array} results
 * @returns {Object}
 */
export function buildEmploymentChartOption(results = []) {
  return {
    tooltip: {
      trigger: "axis",
    },
    legend: {
      show: true,
    },
    grid: {
      left: 50,
      right: 20,
      top: 40,
      bottom: 40,
    },
    xAxis: {
      type: "category",
      data: results.map((x) => x.step),
      name: "step",
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 1,
      name: "就业率",
    },
    series: [
      {
        name: "累计就业率",
        type: "line",
        data: results.map((x) => x.employment_rate),
        smooth: true,
      },
      {
        name: "本轮新增就业率",
        type: "line",
        data: results.map((x) => x.round_new_employment_rate),
        smooth: true,
      },
    ],
  };
}

/**
 * 岗位市场图表：
 * 同时展示本轮岗位空缺率与本轮已填岗位数
 * @param {Array} results
 * @returns {Object}
 */
export function buildVacancyChartOption(results = []) {
  return {
    tooltip: {
      trigger: "axis",
    },
    legend: {
      show: true,
    },
    grid: {
      left: 50,
      right: 50,
      top: 40,
      bottom: 40,
    },
    xAxis: {
      type: "category",
      data: results.map((x) => x.step),
      name: "step",
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
        data: results.map((x) => x.round_vacancy_rate),
        smooth: true,
        yAxisIndex: 0,
      },
      {
        name: "本轮已填岗位",
        type: "bar",
        data: results.map((x) => x.round_filled_jobs),
        yAxisIndex: 1,
      },
    ],
  };
}