<template>
  <el-card class="result-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span>视频分析反馈</span>
        <el-tag :type="statusTagType">{{ statusTagText }}</el-tag>
      </div>
    </template>

    <div v-if="status === 'idle'" class="empty-state">
      <el-empty description="暂无分析任务，请先上传巡检视频" />
    </div>

    <div v-else-if="status === 'analyzing'" class="state-panel">
      <el-icon class="state-icon is-loading"><Loading /></el-icon>
      <p class="state-title">视频已提交，正在后台分析</p>
      <p class="state-desc">系统会自动轮询检测结果，识别到垃圾后会在右侧实时任务中显示。</p>
    </div>

    <div v-else-if="latestTask" class="result-layout">
      <div class="image-wrap">
        <el-image
          class="preview-image"
          :src="imageUrl"
          :preview-src-list="imageUrl ? [imageUrl] : []"
          preview-teleported
          fit="cover"
        >
          <template #error>
            <div class="image-fallback">抓拍图片加载失败</div>
          </template>
        </el-image>
      </div>

      <div class="info-wrap">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="视频来源">
            {{ latestTask.record?.video_source || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="视频时间戳">
            {{ latestTask.record?.frame_time || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="识别置信度">
            {{ formatConfidence(latestTask.record?.confidence) }}
          </el-descriptions-item>
          <el-descriptions-item label="任务状态">
            <el-tag :type="latestTask.status === 'completed' ? 'success' : 'warning'" effect="dark">
              {{ latestTask.status === "completed" ? "已完成" : "待处理" }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>

    <div v-else class="state-panel">
      <el-icon class="state-icon"><InfoFilled /></el-icon>
      <p class="state-title">本次分析暂未发现垃圾任务</p>
      <p class="state-desc">如果后台后续识别到垃圾，任务区会自动刷新显示。</p>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from "vue";
import { InfoFilled, Loading } from "@element-plus/icons-vue";

const props = defineProps({
  status: {
    type: String,
    default: "idle",
  },
  latestTask: {
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

const imageUrl = computed(() => {
  const path = props.latestTask?.record?.screenshot_url;
  if (!path) return "";
  if (/^https?:\/\//i.test(path)) return path;
  return `${apiOrigin}/${path.replace(/^\/+/, "")}`;
});

const statusTagType = computed(() => {
  if (props.status === "analyzing") return "warning";
  if (props.status === "done") return "danger";
  if (props.status === "empty") return "info";
  return "info";
});

const statusTagText = computed(() => {
  if (props.status === "analyzing") return "分析中";
  if (props.status === "done") return "已识别";
  if (props.status === "empty") return "暂无命中";
  return "待开始";
});

const formatConfidence = (value) => {
  if (value === null || value === undefined) return "-";
  return `${(Number(value) * 100).toFixed(1)}%`;
};
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

.state-panel {
  min-height: 280px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 10px;
  color: #4b5563;
}

.state-icon {
  font-size: 34px;
  color: #3b82f6;
}

.state-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.state-desc {
  margin: 0;
  max-width: 420px;
  line-height: 1.7;
}

.result-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.image-wrap {
  border-radius: 12px;
  overflow: hidden;
  background: #f3f4f6;
}

.preview-image {
  width: 100%;
  height: 300px;
  display: block;
}

.image-fallback {
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  background: #f3f4f6;
}

@media (min-width: 992px) {
  .result-layout {
    grid-template-columns: 1.1fr 1fr;
  }

  .preview-image,
  .image-fallback {
    height: 320px;
  }
}
</style>
