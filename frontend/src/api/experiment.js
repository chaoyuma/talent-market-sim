import axios from "axios";

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
});

/**
 * 获取历史实验列表
 * @returns {Promise}
 */
export function getExperimentList() {
  return request.get("/api/experiment/list");
}

/**
 * 获取某次实验详情
 * @param {string} experimentId 实验ID
 * @returns {Promise}
 */
export function getExperimentDetail(experimentId) {
  return request.get(`/api/experiment/${experimentId}`);
}