import http from "./http";
export { uploadDetectionVideo } from "./detection";

export const getStats = () => http.get("/dashboard/stats");

export const getTaskList = (params = {}) => http.get("/tasks/", { params });

export const updateTaskStatus = (taskId, status) =>
  http.patch("/tasks/" + taskId + "/status", { status });
