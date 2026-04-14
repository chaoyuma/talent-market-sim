// 图表 option 构建工具

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
        name: "就业率",
        type: "line",
        data: results.map((x) => x.employment_rate),
        smooth: true,
      },
    ],
  };
}

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
      name: "空缺率",
    },
    series: [
      {
        name: "空缺率",
        type: "line",
        data: results.map((x) => x.vacancy_rate),
        smooth: true,
      },
    ],
  };
}