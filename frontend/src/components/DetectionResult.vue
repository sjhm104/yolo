<template>
  <el-card class="result-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span>AI 识别结果</span>
        <el-tag :type="taskCreated ? 'warning' : 'success'">
          {{ taskCreated ? "已生成清理任务" : "未生成清理任务" }}
        </el-tag>
      </div>
    </template>

    <div v-if="!record" class="empty-state">
      <el-empty description="暂无识别结果，请先上传巡检图片" />
    </div>

    <div v-else class="result-layout">
      <div class="preview-wrap">
        <el-image class="preview-image" :src="imageUrl" fit="cover" :preview-src-list="[imageUrl]" />
      </div>

      <div class="info-wrap">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="记录ID">{{ record.id }}</el-descriptions-item>
          <el-descriptions-item label="无人机ID">{{ record.drone_id ?? "-" }}</el-descriptions-item>
          <el-descriptions-item label="检测结果">
            <el-tag :type="record.has_waste ? 'danger' : 'success'">
              {{ record.has_waste ? "检测到垃圾" : "未检测到垃圾" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="置信度">
            {{ confidenceText }}
          </el-descriptions-item>
          <el-descriptions-item label="经纬度">
            {{ record.latitude }}, {{ record.longitude }}
          </el-descriptions-item>
          <el-descriptions-item label="图片路径">{{ record.image_url }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  record: {
    type: Object,
    default: null,
  },
});

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";
const apiOrigin = (() => {
  try {
    return new URL(apiBaseUrl, window.location.origin).origin;
  } catch {
    return window.location.origin;
  }
})();

const taskCreated = computed(() => Boolean(props.record?.has_waste));

const confidenceText = computed(() => {
  const value = props.record?.confidence;
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "-";
  }
  return `${(Number(value) * 100).toFixed(2)}%`;
});

const imageUrl = computed(() => {
  if (!props.record?.image_url) {
    return "";
  }

  if (/^https?:\/\//i.test(props.record.image_url)) {
    return props.record.image_url;
  }

  const relativePath = props.record.image_url.replace(/^\/+/, "");
  return `${apiOrigin}/${relativePath}`;
});
</script>

<style scoped>
.result-card {
  border: none;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-weight: 600;
  color: #111827;
}

.empty-state {
  padding: 10px 0;
}

.result-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.preview-wrap {
  border-radius: 12px;
  overflow: hidden;
  background: #f3f4f6;
}

.preview-image {
  width: 100%;
  height: 280px;
}

@media (min-width: 992px) {
  .result-layout {
    grid-template-columns: 1.05fr 1fr;
  }

  .preview-image {
    height: 100%;
    min-height: 320px;
  }
}
</style>
