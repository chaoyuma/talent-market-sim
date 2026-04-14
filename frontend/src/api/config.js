import axios from "axios";

// 参数模板接口
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
});

/**
 * 获取参数模板列表
 * @returns {Promise}
 */
export function getConfigTemplateList() {
  return request.get("/api/config/list");
}

/**
 * 获取某个参数模板详情
 * @param {string} configId 模板ID
 * @returns {Promise}
 */
export function getConfigTemplateDetail(configId) {
  return request.get(`/api/config/${configId}`);
}

/**
 * 保存参数模板
 * @param {object} payload 模板数据
 * @returns {Promise}
 */
export function saveConfigTemplate(payload) {
  return request.post("/api/config/save", payload);
}