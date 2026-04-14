// 结果处理工具函数
// 负责从后端返回结果中提取常用信息，避免页面里写太多计算逻辑。

/**
 * 获取最后一步结果
 * @param {object|null} result 后端返回的完整结果对象
 * @returns {object|null}
 */
export function getLatestResult(result) {
  const list = result?.results || [];
  return list.length ? list[list.length - 1] : null;
}

/**
 * 百分比格式化
 * @param {number|undefined|null} value 0~1 之间的小数
 * @returns {string}
 */
export function formatPercent(value) {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return "-";
  }
  return (value * 100).toFixed(2) + "%";
}

/**
 * 数值格式化
 * @param {number|undefined|null} value 数字
 * @param {number} digits 保留小数位
 * @returns {string}
 */
export function formatNumber(value, digits = 2) {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return "-";
  }
  return Number(value).toFixed(digits);
}

/**
 * 生成结果卡片数组
 * @param {object|null} latest 最新一步结果
 * @returns {Array}
 */
export function buildStatCards(latest) {
  if (!latest) return [];

  return [
    {
      key: "final_employment_rate",
      label: "最终就业率",
      value: formatPercent(latest.employment_rate),
    },
    {
      key: "final_matching_rate",
      label: "最终对口率",
      value: formatPercent(latest.matching_rate),
    },
    {
      key: "final_cross_major_rate",
      label: "跨专业率",
      value: formatPercent(latest.cross_major_rate),
    },
    {
      key: "final_vacancy_rate",
      label: "岗位空缺率",
      value: formatPercent(latest.vacancy_rate),
    },
    {
      key: "final_filled_jobs",
      label: "已填岗位数",
      value:
        latest.filled_jobs !== undefined && latest.filled_jobs !== null
          ? String(latest.filled_jobs)
          : "-",
    },
    {
      key: "final_avg_salary",
      label: "平均薪资",
      value: formatNumber(latest.avg_salary, 2),
    },
  ];
}