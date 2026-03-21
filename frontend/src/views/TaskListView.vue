<template>
  <section class="task-page">
    <header class="task-header">
      <h2>清理任务管理</h2>
      <el-button type="primary" @click="fetchTasks" :loading="loading">刷新任务</el-button>
    </header>

    <el-card shadow="never">
      <el-table :data="tasks" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="任务ID" width="90" />

        <el-table-column label="无人机图片" width="130">
          <template #default="{ row }">
            <el-image
              class="thumb"
              :src="resolveImageUrl(row?.detection_record?.image_url)"
              :preview-src-list="[resolveImageUrl(row?.detection_record?.image_url)]"
              preview-teleported
              fit="cover"
            >
              <template #error>
                <div class="image-error">暂无图片</div>
              </template>
            </el-image>
          </template>
        </el-table-column>

        <el-table-column label="经纬度" min-width="190">
          <template #default="{ row }">
            <div>纬度: {{ row?.detection_record?.latitude }}</div>
            <div>经度: {{ row?.detection_record?.longitude }}</div>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" min-width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== 'completed'"
              type="success"
              size="small"
              @click="markCompleted(row.id)"
            >
              标记为已完成
            </el-button>
            <span v-else class="done-text">已完成</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";

import { getTaskList, updateTaskStatus } from "../api";

const loading = ref(false);
const tasks = ref([]);

const resolveImageUrl = (path) => {
  if (!path) return "";
  if (path.startsWith("http://") || path.startsWith("https://")) return path;

  const base = import.meta.env.VITE_API_BASE_URL || "";
  const origin = base.replace(/\/api\/v1\/?$/, "");
  return origin + "/" + path.replace(/^\/+/, "");
};

const statusType = (status) => {
  if (status === "completed") return "success";
  if (status === "assigned") return "danger";
  return "warning";
};

const statusText = (status) => {
  if (status === "completed") return "已完成";
  if (status === "assigned") return "处理中";
  return "待处理";
};

const formatTime = (value) => {
  if (!value) return "-";
  return new Date(value).toLocaleString();
};

const fetchTasks = async () => {
  loading.value = true;
  try {
    const { data } = await getTaskList({ skip: 0, limit: 100 });
    tasks.value = data;
  } finally {
    loading.value = false;
  }
};

const markCompleted = async (taskId) => {
  await updateTaskStatus(taskId, "completed");
  ElMessage.success("任务已更新为完成");
  await fetchTasks();
};

onMounted(fetchTasks);
</script>

<style scoped>
.task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.task-header h2 {
  margin: 0;
  color: #1f2937;
}

.thumb {
  width: 92px;
  height: 62px;
  border-radius: 8px;
  overflow: hidden;
  background: #f3f4f6;
}

.image-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 12px;
}

.done-text {
  color: #16a34a;
  font-size: 13px;
}
</style>
