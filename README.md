# 基于无人机校园垃圾检测系统设计与实现

本项目采用前后端分离架构，后端使用 FastAPI，AI 算法模块使用 PyTorch/YOLO，前端使用 Vue 3，数据库使用 MySQL。

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
- 完成检测上传接口：POST /api/v1/detections/upload。
- 完成业务规则：当 has_waste=true 时自动创建清理任务。
- 完成 FastAPI 主入口、v1 路由聚合与跨域配置。

## 快速体验

1. 初始化数据库：执行 database/schema/init.sql。
2. 启动后端服务：在 backend 目录运行 uvicorn app.main:app --reload。
3. 打开接口文档：访问 http://127.0.0.1:8000/docs。
4. 调用检测上传接口：验证检测记录与清理任务自动生成。

## 模块文档索引

- 后端模块说明：[backend/README.md](backend/README.md)
- 前端模块说明：[frontend/README.md](frontend/README.md)
- AI 模块说明：[ai/README.md](ai/README.md)
- 数据库模块说明：[database/README.md](database/README.md)

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
2. 再启动后端服务，参考 [backend/README.md](backend/README.md)。
3. 最后联调前端页面，参考 [frontend/README.md](frontend/README.md)。

## 远程仓库

GitHub: https://github.com/sjhm104/YOLO
