<template>
  <el-card class="result-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span>视频分析结果</span>
        <el-tag type="success">分析完成</el-tag>
      </div>
    </template>

    <div v-if="!record" class="empty-state">
      <el-empty description="暂无分析结果，请先上传巡检视频" />
    </div>

    <div v-else class="result-layout">
      <div class="video-wrap">
        <video class="preview-video" controls autoplay :src="videoUrl"></video>
      </div>

      <div class="info-wrap">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="总检测目标数">
            {{ record.total_detections ?? 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="处理帧数">
            {{ record.processed_frames ?? 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="输出视频地址">
            {{ record.output_video_url || "-" }}
          </el-descriptions-item>
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

const videoUrl = computed(() => {
  if (!props.record?.output_video_url) {
    return "";
  }

  if (/^https?:\/\//i.test(props.record.output_video_url)) {
    return props.record.output_video_url;
  }

  const relativePath = props.record.output_video_url.replace(/^\/+/, "");
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

.video-wrap {
  border-radius: 12px;
  overflow: hidden;
  background: #111827;
}

.preview-video {
  width: 100%;
  height: 300px;
  display: block;
}

@media (min-width: 992px) {
  .result-layout {
    grid-template-columns: 1.05fr 1fr;
  }

  .preview-video {
    height: 100%;
    min-height: 320px;
  }
}
</style>
