import http from "./http";

export const getStats = () => http.get("/dashboard/stats");

export const getTaskList = (params = {}) => http.get("/tasks/", { params });

export const updateTaskStatus = (taskId, status) =>
  http.patch("/tasks/" + taskId + "/status", { status });
