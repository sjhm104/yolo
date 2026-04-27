# 前端模块说明（Vue 3）

本模块负责无人机检测结果展示、上传交互与任务状态可视化。

当前已接入 Vue 3 + Vite + Element Plus + Axios，可直接本地运行。

## 文档同步状态

- 同步日期：2026-04-27
- 当前实现：Dashboard 已接入视频上传、云端分析中提示与结果视频回放组件。

## 目录说明

- src/views：页面级视图
- src/components：可复用组件
- src/api：前端 API 调用封装
- src/router：前端路由
- src/stores：状态管理（预留）

## 环境变量

请参考：frontend/.env.example

关键变量：

- VITE_API_BASE_URL：后端 API 基础地址

## 启动说明

在 frontend 目录执行：

```bash
npm install
npm run dev
```

默认访问地址：

```text
http://localhost:5173
```

可用脚本：

- npm run dev：本地开发
- npm run build：生产构建
- npm run preview：构建产物预览

## 联调说明

本地联调前请确保以下服务已启动：

- 后端 FastAPI 服务（http://127.0.0.1:8000）
- MySQL campus 实例（D:/pysoft/mysql/instances/campus）

前端调用后端接口时，建议将 API 前缀统一配置为：

```text
/api/v1
```

检测上传接口路径：

```text
/api/v1/detections/upload-video
```

## 页面闭环能力

Dashboard 页面已接入完整闭环组件：

- VideoUpload.vue：上传 mp4/avi 视频，调用 /detections/upload-video
- DetectionResult.vue：展示分析后视频回放、总检测目标数、处理帧数

上传组件行为：

- el-upload accept 已配置为 video/mp4,video/x-m4v,video/*
- 分析期间显示 Loading：云端视频逐帧分析中，请稍候...
- 分析结束后通过 video 标签展示后端返回的 output_video_url

上传成功后，页面会自动显示最新视频分析结果，并刷新统计卡片。

## 毕设演示建议

1. 进入 Dashboard，先展示统计卡片初始状态。
2. 上传一段巡检视频（mp4/avi），展示分析中 Loading 提示。
3. 分析完成后演示结果视频自动回放。
4. 展示总检测目标数与处理帧数。
5. 在浏览器直接访问 output_video_url，验证静态视频访问。
