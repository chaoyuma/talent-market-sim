import axios from "axios";

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 30000,
});

export function generateComparisonReport(experimentIds) {
  return request.post("/api/report/generate-comparison", {
    experiment_ids: experimentIds,
  });
}

export function generateComparisonReportAsync(experimentIds) {
  return request.post("/api/report/generate-comparison-async", {
    experiment_ids: experimentIds,
  });
}

export function getComparisonReportTask(taskId) {
  return request.get(`/api/report/tasks/${taskId}`);
}

export function downloadComparisonReport(taskId) {
  return request.get(`/api/report/download/${taskId}`, {
    responseType: "blob",
    timeout: 0,
  });
}
export function getReportHistoryList() {
  return request.get("/api/report/history");
}

export function getReportHistoryDetail(reportId) {
  return request.get(`/api/report/history/${reportId}`);
}

export function downloadReportHistoryFile(reportId) {
  return request.get(`/api/report/history/${reportId}/download`, {
    responseType: "blob",
    timeout: 0,
  });
}

export function deleteReportHistoryItem(reportId) {
  return request.delete(`/api/report/history/${reportId}`);
}