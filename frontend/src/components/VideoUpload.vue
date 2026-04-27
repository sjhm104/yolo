<template>
  <section
    v-loading="processing"
    element-loading-text="云端视频逐帧分析中，请稍候..."
    class="upload-wrapper"
  >
    <el-card class="upload-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>无人机巡检视频分析</span>
          <el-tag type="info">video/mp4, video/avi</el-tag>
        </div>
      </template>

      <el-radio-group v-model="mode" class="mode-switch">
        <el-radio-button label="upload">本地上传</el-radio-button>
        <el-radio-button label="cloud">云端视频URL</el-radio-button>
      </el-radio-group>

      <el-form ref="formRef" :model="form" label-width="90px" class="upload-form">
        <el-form-item v-if="mode === 'upload'" label="巡检视频" prop="file">
          <el-upload
            class="upload-box"
            drag
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :file-list="fileList"
            accept="video/mp4,video/x-m4v,video/*"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖拽视频到此处，或点击上传</div>
            <template #tip>
              <div class="el-upload__tip">仅支持 mp4/avi，单次 1 个视频文件</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item v-else label="视频地址" prop="video_url">
          <el-input v-model="form.video_url" placeholder="请输入可公网访问的 mp4/avi 视频 URL" clearable />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="processing" @click="submitForm">开始分析</el-button>
          <el-button :disabled="processing" @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { UploadFilled } from "@element-plus/icons-vue";

import { analyzeDetectionVideoUrl, uploadDetectionVideo } from "../api/detection";

const emit = defineEmits(["uploaded"]);

const formRef = ref();
const processing = ref(false);
const fileList = ref([]);
const mode = ref("upload");

const form = reactive({
  file: null,
  video_url: "",
});

const handleFileChange = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles.slice(-1);
  form.file = uploadFile.raw || null;
};

const handleFileRemove = () => {
  fileList.value = [];
  form.file = null;
};

const submitForm = async () => {
  processing.value = true;
  try {
    let data;

    if (mode.value === "upload") {
      if (!form.file) {
        ElMessage.warning("请先上传视频文件");
        return;
      }
      const payload = new FormData();
      payload.append("file", form.file);
      const resp = await uploadDetectionVideo(payload);
      data = resp.data;
    } else {
      if (!form.video_url?.trim()) {
        ElMessage.warning("请输入云端视频 URL");
        return;
      }
      const resp = await analyzeDetectionVideoUrl(form.video_url.trim());
      data = resp.data;
    }

    ElMessage.success("视频分析完成");
    emit("uploaded", data);
  } finally {
    processing.value = false;
  }
};

const resetForm = () => {
  formRef.value?.resetFields();
  form.file = null;
  form.video_url = "";
  fileList.value = [];
};
</script>

<style scoped>
.upload-card {
  border: none;
}

.upload-wrapper {
  min-height: 260px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-weight: 600;
  color: #111827;
}

.upload-form {
  padding-top: 6px;
}

.mode-switch {
  margin-bottom: 12px;
}

.upload-box {
  width: 100%;
}
</style>
