# 前端模块说明（Vue 3）

本模块负责无人机检测结果展示、上传交互与任务状态可视化。

当前已接入 Vue 3 + Vite + Element Plus + Axios，可直接本地运行。

## 文档同步状态

- 同步日期：2026-04-18
- 当前实现：Dashboard 已接入上传与识别结果展示组件，任务页支持状态更新。

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
/api/v1/detections/upload
```

## 页面闭环能力

Dashboard 页面已接入完整闭环组件：

- VideoUpload.vue：上传图片 + 填写 drone_id/latitude/longitude，调用 /detections/upload
- DetectionResult.vue：展示识别图片、是否检测到垃圾、置信度、是否生成任务

说明：后端返回 DetectionRecord 不含独立任务字段，页面根据 has_waste 展示“已生成/未生成任务”状态。

上传成功后，页面会自动显示最新 detection_record，并刷新统计卡片。

## 毕设演示建议

1. 进入 Dashboard，先展示统计卡片初始状态。
2. 上传一张无垃圾图片，展示“未检测到垃圾/未生成任务”。
3. 上传一张有垃圾图片，展示“检测到垃圾/已生成任务”。
4. 结合后端数据库结果说明自动派单规则（has_waste=true 自动创建 cleaning_task）。
5. 可配合 tools/simulate_uav_stream.py 做连续上传演示，体现实时性。
