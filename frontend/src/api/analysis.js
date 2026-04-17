import axios from "axios";


const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 180000,
});

export function generateParameterSuggestions(payload) {
  return request.post("/api/analysis/generate-parameter-suggestions", {
    payload,
  });
}


export function generateResultExplanation(payload) {
  return request.post("/api/analysis/explain-result", payload);
}