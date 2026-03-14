# 基于无人机校园垃圾检测系统设计与实现

本项目采用前后端分离架构，后端使用 FastAPI，AI 算法模块使用 PyTorch/YOLO，前端使用 Vue 3，数据库使用 MySQL。

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

## 数据库初始化

项目数据库初始化脚本位于 [database/schema/init.sql](database/schema/init.sql)。

脚本功能包括：

1. 创建数据库 campus_waste_db（若不存在）
2. 选择并使用 campus_waste_db
3. 创建 users、drones、detection_records、cleaning_tasks 四张核心业务表
4. 初始化索引、外键与中文注释

执行方式（MySQL 客户端）：

```sql
SOURCE database/schema/init.sql;
```

执行方式（命令行）：

```bash
mysql -u root -p < database/schema/init.sql
```

更多数据库说明请查看 [database/README.md](database/README.md)。

## 远程仓库

GitHub: https://github.com/sjhm104/YOLO
