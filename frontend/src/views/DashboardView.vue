<template>
  <section class="dashboard-page">
    <header class="page-header">
      <h2>校园垃圾检测数据大屏</h2>
      <p>实时掌握巡检视频分析与处置任务进展</p>
    </header>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :lg="6" v-for="card in statCards" :key="card.key">
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

    <el-row :gutter="16" class="loop-row">
      <el-col :xs="24" :lg="11">
        <VideoUpload @uploaded="handleUploaded" />
      </el-col>
      <el-col :xs="24" :lg="13">
        <DetectionResult :record="latestVideoResult" />
      </el-col>
    </el-row>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { Aim, CircleCheck, Clock, DataLine } from "@element-plus/icons-vue";

import { getStats } from "../api";
import DetectionResult from "../components/DetectionResult.vue";
import VideoUpload from "../components/VideoUpload.vue";

const stats = ref({
  total_detections: 0,
  waste_found_count: 0,
  pending_tasks: 0,
  completed_tasks: 0,
});
const latestVideoResult = ref(null);

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

const handleUploaded = (result) => {
  latestVideoResult.value = result;
  fetchStats();
};

onMounted(fetchStats);
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

.stat-card {
  margin-bottom: 16px;
  border: none;
}

.loop-row {
  margin-top: 4px;
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
</style>
