import axios from "axios";

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 30000,
});

export function getMetadataTableList() {
  return request.get("/api/metadata/");
}

export function getMetadataByTableName(tableName) {
  return request.get(`/api/metadata/${tableName}`);
}