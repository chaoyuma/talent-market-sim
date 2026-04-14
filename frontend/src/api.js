import axios from "axios";

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
});

export function runSimulation(data) {
  return request.post("/api/simulation/run", data);
}