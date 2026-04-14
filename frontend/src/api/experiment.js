import axios from "axios";

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
});

export function getExperimentList() {
  return request.get("/api/experiment/list");
}

export function getExperimentDetail(experimentId) {
  return request.get(`/api/experiment/${experimentId}`);
}