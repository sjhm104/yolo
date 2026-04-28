<template>
  <section class="task-page">
    <header class="task-header">
      <h2>清理任务管理</h2>
      <el-button type="primary" @click="fetchTasks" :loading="loading">刷新任务</el-button>
    </header>

    <el-card shadow="never">
      <el-table :data="tasks" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="任务ID" width="90" />

        <el-table-column label="抓拍图片" width="130">
          <template #default="{ row }">
            <el-image
              class="thumb"
              :src="resolveImageUrl(row?.record?.screenshot_url)"
              :preview-src-list="[resolveImageUrl(row?.record?.screenshot_url)]"
              preview-teleported
              fit="cover"
            >
              <template #error>
                <div class="image-error">暂无图片</div>
              </template>
            </el-image>
          </template>
        </el-table-column>

        <el-table-column prop="record.frame_time" label="视频时间戳" width="140">
          <template #default="{ row }">
            {{ row?.record?.frame_time || "-" }}
          </template>
        </el-table-column>

        <el-table-column prop="record.video_source" label="视频源" min-width="180">
          <template #default="{ row }">
            {{ row?.record?.video_source || "-" }}
          </template>
        </el-table-column>

        <el-table-column prop="worker.name" label="指派给" min-width="180">
          <template #default="{ row }">
            <el-select
              :model-value="row.worker_id"
              placeholder="选择环卫工人"
              clearable
              filterable
              @change="(value) => handleAssign(row.id, value)"
            >
              <el-option
                v-for="worker in workers"
                :key="worker.id"
                :label="`${worker.name} (${worker.phone})`"
                :value="worker.id"
              />
            </el-select>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row)">{{ statusText(row) }}</el-tag>
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
              标记完成
            </el-button>
            <span v-else class="done-text">已完成</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </section>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from "vue";
import { ElMessage } from "element-plus";

import { assignTaskWorker, completeTask, getTaskList, getWorkerList } from "../api";

const loading = ref(false);
const tasks = ref([]);
const workers = ref([]);
let refreshTimer = null;

const resolveImageUrl = (path) => {
  if (!path) return "";
  if (path.startsWith("http://") || path.startsWith("https://")) return path;

  const base = import.meta.env.VITE_API_BASE_URL || "";
  const origin = base.replace(/\/api\/v1\/?$/, "");
  return origin + "/" + path.replace(/^\/+/, "");
};

const statusType = (task) => {
  if (task?.status === "completed") return "success";
  if (task?.worker_id || task?.worker?.id) return "warning";
  return "info";
};

const statusText = (task) => {
  if (task?.status === "completed") return "已完成";
  if (task?.worker_id || task?.worker?.id) return "处理中";
  return "待分配";
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
  } catch {
    // 后端短暂不可用时静默容错，避免频繁打断用户
  } finally {
    loading.value = false;
  }
};

const fetchWorkers = async () => {
  try {
    const { data } = await getWorkerList();
    workers.value = data;
  } catch {
    // 后端短暂不可用时静默容错，避免频繁打断用户
  }
};

const handleAssign = async (taskId, workerId) => {
  if (!workerId) return;
  await assignTaskWorker(taskId, workerId);
  ElMessage.success("任务指派已更新");
  await fetchTasks();
};

const markCompleted = async (taskId) => {
  await completeTask(taskId);
  ElMessage.success("任务已更新为完成");
  await fetchTasks();
};

onMounted(fetchWorkers);
onMounted(fetchTasks);
onMounted(() => {
  refreshTimer = window.setInterval(() => {
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
