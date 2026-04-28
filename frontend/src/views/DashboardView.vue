<template>
  <section class="dashboard-page">
    <header class="page-header">
      <h2>校园垃圾检测综合看板</h2>
      <p>左侧检测画面，右侧数据统计与实时任务</p>
    </header>

    <el-row :gutter="16" class="layout-row">
      <el-col :xs="24" :lg="12" class="left-panel">
        <VideoUpload @uploaded="handleUploaded" />
        <DetectionResult
          :status="analysisStatus"
          :latest-task="latestTask"
          class="result-panel"
        />
      </el-col>

      <el-col :xs="24" :lg="12" class="right-panel">
        <el-row :gutter="12">
          <el-col :xs="12" :sm="12" :lg="12" v-for="card in statCards" :key="card.key">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="icon-box" :class="card.theme">
                  <el-icon :size="24"><component :is="card.icon" /></el-icon>
                </div>
                <div class="meta">
                  <p class="label">{{ card.label }}</p>
                  <p class="value">{{ card.value }}</p>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-card class="task-card" shadow="hover">
          <template #header>
            <div class="section-header">
              <span>实时任务</span>
              <el-button text type="primary" :loading="tasksLoading" @click="fetchTasks">刷新</el-button>
            </div>
          </template>

          <div v-loading="tasksLoading" class="task-stream">
            <el-empty v-if="!tasks.length && !tasksLoading" description="暂无实时任务" />

            <el-card v-for="task in tasks" :key="task.id" class="task-item" shadow="never">
              <div class="task-item-head">
                <div>
                  <span class="task-id">任务 #{{ task.id }}</span>
                  <el-tag :type="statusType(task.status)" class="task-status">{{ statusText(task.status) }}</el-tag>
                </div>
                <span class="task-time">{{ formatTime(task.created_at) }}</span>
              </div>

              <div class="task-item-body">
                <div class="task-field">
                  <span class="field-label">视频时间戳</span>
                  <span class="field-value">{{ task?.record?.frame_time || "-" }}</span>
                </div>
                <div class="task-field">
                  <span class="field-label">视频来源</span>
                  <span class="field-value ellipsis">{{ task?.record?.video_source || "-" }}</span>
                </div>
                <div class="task-field">
                  <span class="field-label">抓拍图片</span>
                  <span class="field-value ellipsis">{{ task?.record?.screenshot_url || "-" }}</span>
                </div>
              </div>
            </el-card>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </section>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from "vue";
import { Aim, CircleCheck, Clock, DataLine } from "@element-plus/icons-vue";

import { getStats, getTaskList } from "../api";
import DetectionResult from "../components/DetectionResult.vue";
import VideoUpload from "../components/VideoUpload.vue";

const stats = ref({
  total_detections: 0,
  waste_found_count: 0,
  pending_tasks: 0,
  completed_tasks: 0,
});
const tasks = ref([]);
const tasksLoading = ref(false);
const analysisStatus = ref("idle");
const analysisStartedAt = ref(null);
const baselineTaskCount = ref(0);
let refreshTimer = null;

const latestTask = computed(() => (tasks.value.length ? tasks.value[0] : null));

const statCards = computed(() => [
  {
    key: "total_detections",
    label: "总检测次数",
    value: stats.value.total_detections,
    icon: DataLine,
    theme: "theme-blue",
  },
  {
    key: "waste_found_count",
    label: "发现垃圾次数",
    value: stats.value.waste_found_count,
    icon: Aim,
    theme: "theme-orange",
  },
  {
    key: "pending_tasks",
    label: "待处理任务",
    value: stats.value.pending_tasks,
    icon: Clock,
    theme: "theme-red",
  },
  {
    key: "completed_tasks",
    label: "已完成任务",
    value: stats.value.completed_tasks,
    icon: CircleCheck,
    theme: "theme-green",
  },
]);

const fetchStats = async () => {
  try {
    const { data } = await getStats();
    stats.value = data;
  } catch {
    // 后端短暂不可用时静默容错，避免频繁打断用户
  }
};

const fetchTasks = async () => {
  tasksLoading.value = true;
  try {
    const { data } = await getTaskList({ skip: 0, limit: 20 });
    tasks.value = data;
    updateAnalysisStatus();
  } catch {
    // 后端短暂不可用时静默容错，避免频繁打断用户
  } finally {
    tasksLoading.value = false;
  }
};

const updateAnalysisStatus = () => {
  if (analysisStatus.value !== "analyzing") {
    return;
  }

  if (tasks.value.length > baselineTaskCount.value) {
    analysisStatus.value = "done";
    return;
  }

  if (analysisStartedAt.value && Date.now() - analysisStartedAt.value >= 60000) {
    analysisStatus.value = "empty";
  }
};

const statusType = (status) => {
  if (status === "completed") return "success";
  return "warning";
};

const statusText = (status) => {
  if (status === "completed") return "已完成";
  return "待处理";
};

const formatTime = (value) => {
  if (!value) return "-";
  return new Date(value).toLocaleString();
};

const handleUploaded = (result) => {
  analysisStatus.value = "analyzing";
  analysisStartedAt.value = Date.now();
  baselineTaskCount.value = tasks.value.length;
  fetchStats();
  fetchTasks();
};

onMounted(fetchStats);
onMounted(fetchTasks);
onMounted(() => {
  refreshTimer = window.setInterval(() => {
    fetchStats();
    fetchTasks();
  }, 3000);
});

onBeforeUnmount(() => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer);
  }
});
</script>

<style scoped>
.dashboard-page {
  min-height: 100%;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  color: #1f2937;
}

.page-header p {
  margin: 6px 0 0;
  color: #6b7280;
}

.layout-row {
  align-items: stretch;
}

.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.left-panel {
  position: relative;
}

.left-panel :deep(.upload-wrapper),
.left-panel :deep(.result-card) {
  flex: 1;
}

.result-panel {
  margin-top: 0;
}

.stat-card {
  border: none;
}

.task-card {
  border: none;
}

.task-card {
  flex: 1;
}

.task-stream {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 420px;
}

.task-item {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.task-item-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.task-id {
  font-weight: 700;
  color: #111827;
}

.task-status {
  margin-left: 8px;
}

.task-time {
  color: #6b7280;
  font-size: 12px;
  white-space: nowrap;
}

.task-item-body {
  display: grid;
  gap: 10px;
}

.task-field {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.field-label {
  color: #6b7280;
  font-size: 13px;
}

.field-value {
  color: #111827;
  font-size: 13px;
  font-weight: 600;
}

.ellipsis {
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  color: #111827;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 14px;
}

.icon-box {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.theme-blue {
  background: linear-gradient(145deg, #3b82f6, #2563eb);
}

.theme-orange {
  background: linear-gradient(145deg, #fb923c, #f97316);
}

.theme-red {
  background: linear-gradient(145deg, #ef4444, #dc2626);
}

.theme-green {
  background: linear-gradient(145deg, #22c55e, #16a34a);
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.label {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
}

.value {
  margin: 0;
  font-size: 30px;
  font-weight: 700;
  color: #111827;
}

@media (max-width: 992px) {
  .right-panel {
    margin-top: 16px;
  }

  .ellipsis {
    max-width: 180px;
  }
}
</style>
