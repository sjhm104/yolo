# 基于无人机校园垃圾检测系统设计与实现

本项目采用前后端分离架构，后端使用 FastAPI，AI 算法模块使用 PyTorch/YOLO，前端使用 Vue 3，数据库使用 MySQL。

## 文档同步状态

- 同步日期：2026-04-27
- 已同步范围：README、backend/README、frontend/README、ai/README、database/README。
- 当前闭环状态：无人机巡检视频 -> 视频上传 -> 逐帧 AI 识别 -> 输出分析视频 -> 前端展示 已联通。

## 项目简介

本项目面向校园场景，利用无人机巡航采集图像，通过目标检测模型识别垃圾目标，并自动生成清理任务，形成“巡检-识别-派单-处置”的闭环流程。

## 系统架构

- 前端（Vue 3）：展示检测结果、任务状态与管理页面。
- 后端（FastAPI）：提供 REST API、业务逻辑编排与数据持久化。
- AI 模块（PyTorch/YOLO）：负责训练、推理与模型导出。
- 数据库（MySQL）：存储用户、无人机、检测记录与清理任务。

## 当前已实现

- 完成 MySQL 初始化脚本与核心表结构设计。
- 完成 SQLAlchemy ORM 模型（users、drones、detection_records、cleaning_tasks）。
- 完成视频上传接口：POST /api/v1/detections/upload-video（multipart/form-data）。
- 完成视频逐帧推理：上传视频保存到 backend/uploads/videos，逐帧 YOLO 推理并画框。
- 完成结果视频导出：分析后视频保存到 backend/outputs/videos，并返回可访问 URL。
- 完成检测服务层单例化模型加载，避免重复加载模型权重。
- 完成任务调度模块：每 30 秒扫描待分配任务并自动分配给 cleaner。
- 完成 FastAPI 主入口、v1 路由聚合与跨域配置。
- 完成本地 MySQL 程序与实例分离部署（程序位于 D 盘，实例位于 instances/campus）。
- 完成前端视频交互页面（视频上传、分析中加载提示、结果视频回放）。
- 完成前端 Vite 启动基座（dev/build/preview 脚本可用）。

## 本地 MySQL 部署约定

- 程序目录：D:/pysoft/mysql/mysql-8.4.8/mysql-8.4.8-winx64
- 实例目录：D:/pysoft/mysql/instances/campus
- 实例配置：D:/pysoft/mysql/instances/campus/conf/my.ini
- 实例数据：D:/pysoft/mysql/instances/campus/data

## 快速体验

1. 初始化数据库：执行 database/schema/init.sql。
2. 启动后端服务：在 backend 目录运行 uvicorn app.main:app --reload。
3. 启动前端服务：在 frontend 目录依次运行 npm install 与 npm run dev。
4. 打开接口文档：访问 http://127.0.0.1:8000/docs。
5. 打开前端页面：访问 http://localhost:5173。
6. 以 multipart/form-data 调用视频分析接口。
7. 通过返回的 output_video_url 访问分析后视频。

## 视频上传测试

使用 curl 可直接测试视频分析接口：

示例：

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/detections/upload-video" \
	-F "file=@./tests/assets/demo.mp4"
```

返回字段：

- output_video_url：分析结果视频访问路径
- total_detections：全视频检测目标总数
- processed_frames：处理帧数

## 检测上传接口（最新）

- 请求方法：POST
- 接口路径：/api/v1/detections/upload-video
- Content-Type：multipart/form-data
- 表单字段：
	- file（必填，视频文件，支持 .mp4/.avi）
- 返回结果：视频分析摘要（output_video_url、total_detections、processed_frames）。

示例请求：

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/detections/upload-video" \
	-F "file=@./tests/assets/demo.mp4"
```

说明：

- 上传视频保存路径：backend/uploads/videos。
- 分析后视频输出路径：backend/outputs/videos。
- 可通过 /outputs 前缀静态访问分析视频。

## 毕设演示脚本（建议流程）

1. 展示系统架构：前端 Vue 3、后端 FastAPI、AI YOLO、MySQL。
2. 启动后端与前端，打开 Dashboard 页面。
3. 在 Dashboard 的“无人机巡检视频上传”卡片中上传 mp4/avi 视频。
4. 等待“云端视频逐帧分析中，请稍候...”提示结束。
5. 展示“视频分析结果”卡片：回放分析视频、总检测数、处理帧数。
6. 访问 output_video_url，验证结果视频可单独播放。
7. 总结闭环：无人机巡检视频 -> 视频上传 -> 逐帧 AI 识别 -> 输出视频 -> 前端回放。

## 模块文档索引

- 后端模块说明：[backend/README.md](backend/README.md)
- 前端模块说明：[frontend/README.md](frontend/README.md)
- AI 模块说明：[ai/README.md](ai/README.md)
- 数据库模块说明：[database/README.md](database/README.md)

建议阅读顺序：

1. database/README.md（初始化数据库）
2. backend/README.md（启动接口与上传链路）
3. frontend/README.md（上传展示与任务页面）
4. ai/README.md（推理模块与后端接入方式）

## 项目目录结构（Tree）

```text
pyyolo
|-- ai  # AI算法模块（独立于后端，便于训练/推理解耦）
|   |-- configs  # 模型与推理配置
|   |   |-- yolo.yaml
|   |-- models  # PyTorch/YOLO相关代码
|   |   |-- common  # 通用数据处理模块
|   |   |   |-- dataset.py
|   |   |   |-- transforms.py
|   |   |-- yolo  # YOLO任务脚本（训练/推理/导出）
|   |       |-- train.py
|   |       |-- infer.py
|   |       |-- export.py
|   |-- notebooks  # 实验笔记或分析草稿
|   |   |-- .gitkeep
|   |-- weights  # 模型权重存放目录（建议大文件不入库）
|   |   |-- .gitkeep
|   |-- README.md
|   |-- requirements.txt
|
|-- backend  # FastAPI后端服务（API网关与业务编排）
|   |-- app
|   |   |-- api
|   |   |   |-- v1
|   |   |       |-- endpoints  # 接口实现（检测接口等）
|   |   |       |   |-- detection.py
|   |   |       |-- router.py  # v1路由聚合
|   |   |-- core  # 配置、常量、启动参数
|   |   |   |-- config.py
|   |   |-- db  # 数据库连接与ORM基础
|   |   |   |-- session.py
|   |   |   |-- base.py
|   |   |-- schemas  # Pydantic请求/响应模型
|   |   |   |-- detection.py
|   |   |-- services  # 业务服务层（调用AI推理等）
|   |   |   |-- detector_service.py
|   |   |-- utils
|   |   |   |-- .gitkeep
|   |   |-- main.py  # FastAPI应用入口
|   |-- scripts  # 启动和运维辅助脚本
|   |   |-- run_dev.ps1
|   |-- README.md
|   |-- requirements.txt
|
|-- frontend  # Vue 3前端（与后端API完全分离）
|   |-- public
|   |   |-- .gitkeep
|   |-- src
|   |   |-- api  # 前端API调用封装
|   |   |   |-- http.js
|   |   |   |-- detection.js
|   |   |-- assets
|   |   |   |-- .gitkeep
|   |   |-- components  # 可复用组件
|   |   |   |-- VideoUpload.vue
|   |   |   |-- DetectionResult.vue
|   |   |-- router
|   |   |   |-- index.js
|   |   |-- stores
|   |   |   |-- .gitkeep
|   |   |-- views  # 页面级视图
|   |   |   |-- DashboardView.vue
|   |   |-- App.vue
|   |   |-- main.js
|   |-- .env.example
|   |-- package.json
|   |-- README.md
|
|-- database  # MySQL脚本与迁移
|   |-- migrations  # 迁移脚本目录
|   |   |-- .gitkeep
|   |-- schema  # 建表初始化脚本
|   |   |-- init.sql
|   |-- seeds  # 测试/演示数据
|   |   |-- seed_demo.sql
|   |-- README.md
|
|-- deploy  # 部署相关（容器与网关）
|   |-- docker
|   |   |-- backend.Dockerfile
|   |   |-- frontend.Dockerfile
|   |   |-- ai.Dockerfile
|   |   |-- docker-compose.yml
|   |-- nginx
|       |-- nginx.conf
|
|-- tests  # 测试目录（后端/AI/集成）
|   |-- backend
|   |   |-- test_health.py
|   |-- ai
|   |   |-- test_infer.py
|   |-- integration
|       |-- test_api_model_integration.py
|
|-- tools  # 测试或模拟脚本（无人机流、假数据）
|   |-- simulate_uav_stream.py
|   |-- mock_data_generator.py
|
|-- docs  # 文档目录（架构与接口）
|   |-- architecture.md
|   |-- api.md
|
|-- .env.example
|-- .gitattributes
|-- .gitignore
|-- README.md
```

## 快速开始

1. 先完成数据库初始化，参考 [database/README.md](database/README.md)。
2. 启动本地 MySQL 实例，参考 [database/README.md](database/README.md)。
3. 再启动后端服务，参考 [backend/README.md](backend/README.md)。
4. 最后联调前端页面，参考 [frontend/README.md](frontend/README.md)。

## 远程仓库

GitHub: https://github.com/sjhm104/YOLO
