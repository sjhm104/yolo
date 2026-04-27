<template>
  <el-card class="result-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span>视频分析结果</span>
        <el-tag :type="record?.has_campus_waste ? 'danger' : 'success'">
          {{ record?.has_campus_waste ? "发现校园垃圾" : "未发现校园垃圾" }}
        </el-tag>
      </div>
    </template>

    <div v-if="!record" class="empty-state">
      <el-empty description="暂无分析结果，请先上传巡检视频" />
    </div>

    <div v-else class="result-layout">
      <div class="video-wrap">
        <video
          class="preview-video"
          controls
          autoplay
          playsinline
          :key="videoUrl"
          :src="videoUrl"
          @error="onVideoError"
          @loadeddata="onVideoLoaded"
        ></video>
        <div v-if="videoLoadFailed" class="video-fallback">
          当前浏览器无法直接播放该编码视频。可点击下方链接打开：
          <a :href="videoUrl" target="_blank" rel="noreferrer">{{ videoUrl }}</a>
        </div>
      </div>

      <div class="info-wrap">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="校园垃圾结论">
            <el-tag :type="record.has_campus_waste ? 'danger' : 'success'" effect="dark">
              {{ record.has_campus_waste ? "检测到校园垃圾" : "未检测到校园垃圾" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="垃圾目标数量">
            {{ record.garbage_count ?? 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="结果视频地址">
            {{ record.output_video_url || "-" }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="class-summary" v-if="garbageSummary.length">
          <p class="summary-title">垃圾类别统计</p>
          <div class="summary-tags">
            <el-tag
              v-for="item in garbageSummary"
              :key="item.class_name"
              type="danger"
              effect="light"
            >
              {{ item.class_name }}: {{ item.count }}
            </el-tag>
          </div>
        </div>

        <div class="class-summary" v-else>
          <p class="summary-title">垃圾类别统计</p>
          <el-tag type="success" effect="plain">未识别到垃圾类别</el-tag>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed, ref, watch } from "vue";

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

const videoLoadFailed = ref(false);

watch(videoUrl, () => {
  videoLoadFailed.value = false;
});

const onVideoError = () => {
  videoLoadFailed.value = true;
};

const onVideoLoaded = () => {
  videoLoadFailed.value = false;
};

const garbageSummary = computed(() => {
  const summary = props.record?.garbage_summary;
  return Array.isArray(summary) ? summary : [];
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

.video-fallback {
  padding: 10px 12px;
  font-size: 13px;
  color: #fde68a;
  background: #1f2937;
  border-top: 1px solid rgba(255, 255, 255, 0.16);
}

.video-fallback a {
  color: #93c5fd;
  word-break: break-all;
}

.class-summary {
  margin-top: 14px;
}

.summary-title {
  margin: 0 0 8px;
  color: #374151;
  font-size: 14px;
  font-weight: 600;
}

.summary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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
