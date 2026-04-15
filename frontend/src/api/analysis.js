import axios from "axios";

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 60000,
});

export function generateResultExplanation(payload) {
  return request.post("/api/analysis/explain-result", payload);
}