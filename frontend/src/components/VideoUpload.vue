<template>
  <el-card class="upload-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span>无人机巡检图片上传</span>
        <el-tag type="info">multipart/form-data</el-tag>
      </div>
    </template>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px" class="upload-form">
      <el-form-item label="无人机ID" prop="drone_id">
        <el-input-number v-model="form.drone_id" :min="1" :step="1" controls-position="right" />
      </el-form-item>

      <el-form-item label="纬度" prop="latitude">
        <el-input v-model="form.latitude" placeholder="例如 31.2304" />
      </el-form-item>

      <el-form-item label="经度" prop="longitude">
        <el-input v-model="form.longitude" placeholder="例如 121.4737" />
      </el-form-item>

      <el-form-item label="巡检图片" prop="file">
        <el-upload
          class="upload-box"
          drag
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          :file-list="fileList"
          accept="image/png,image/jpeg,image/jpg,image/bmp,image/webp"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">拖拽图片到此处，或点击上传</div>
          <template #tip>
            <div class="el-upload__tip">仅支持 jpg/jpeg/png/bmp/webp，单次 1 张</div>
          </template>
        </el-upload>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="submitForm">上传并识别</el-button>
        <el-button :disabled="submitting" @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { UploadFilled } from "@element-plus/icons-vue";

import { uploadDetection } from "../api/detection";

const emit = defineEmits(["uploaded"]);

const formRef = ref();
const submitting = ref(false);
const fileList = ref([]);

const form = reactive({
  drone_id: 1,
  latitude: "31.2304",
  longitude: "121.4737",
  file: null,
});

const validateCoordinate = (_rule, value, callback) => {
  if (value === "" || value === null || value === undefined) {
    callback(new Error("请输入坐标"));
    return;
  }

  if (Number.isNaN(Number(value))) {
    callback(new Error("坐标必须是数字"));
    return;
  }

  callback();
};

const rules = {
  drone_id: [{ required: true, message: "请输入无人机ID", trigger: "change" }],
  latitude: [{ validator: validateCoordinate, trigger: "blur" }],
  longitude: [{ validator: validateCoordinate, trigger: "blur" }],
  file: [{ required: true, message: "请上传图片", trigger: "change" }],
};

const handleFileChange = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles.slice(-1);
  form.file = uploadFile.raw || null;
};

const handleFileRemove = () => {
  fileList.value = [];
  form.file = null;
};

const submitForm = async () => {
  if (!formRef.value) {
    return;
  }

  await formRef.value.validate();

  const payload = new FormData();
  payload.append("file", form.file);
  payload.append("drone_id", String(form.drone_id));
  payload.append("latitude", String(form.latitude));
  payload.append("longitude", String(form.longitude));

  submitting.value = true;
  try {
    const { data } = await uploadDetection(payload);
    ElMessage.success("上传成功，识别已完成");
    emit("uploaded", data);
  } finally {
    submitting.value = false;
  }
};

const resetForm = () => {
  formRef.value?.resetFields();
  form.file = null;
  fileList.value = [];
};
</script>

<style scoped>
.upload-card {
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

.upload-form {
  padding-top: 6px;
}

.upload-box {
  width: 100%;
}
</style>
