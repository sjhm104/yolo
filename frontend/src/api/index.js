import http from "./http";
export { uploadDetectionVideo } from "./detection";

export const getStats = () => http.get("/dashboard/stats", { skipGlobalError: true });

export const startVideoAnalysis = (videoPath) =>
  http.post("/detections/analyze", { video_path: videoPath });

export const getTaskList = (params = {}) =>
  http.get("/tasks/", { params, skipGlobalError: true });

export const assignTaskWorker = (taskId, workerId) =>
  http.patch("/tasks/" + taskId + "/assign", { worker_id: workerId });

export const completeTask = (taskId) => http.patch("/tasks/" + taskId + "/complete");

export const getWorkerList = () => http.get("/workers/", { skipGlobalError: true });
