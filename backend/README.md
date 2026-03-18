# 后端模块说明（FastAPI）

本模块负责 API 服务、业务逻辑编排、数据库访问与模型调用接口。

## 目录说明

- app/main.py：FastAPI 启动入口
- app/api/v1：接口路由层
- app/schemas：Pydantic 数据校验模型
- app/db：数据库连接、会话与 ORM 模型
- app/services：业务服务层

## 依赖安装

建议使用解释器：

```text
D:\pysoft\anaconda\envs\myenv\python.exe
```

在项目根目录执行：

```bash
"D:\pysoft\anaconda\envs\myenv\python.exe" -m pip install -r backend/requirements.txt
```

## 启动方式

启动后端前，请先确保 MySQL 已启动（实例目录见 database 模块文档）。

必须先进入 backend 目录：

```bash
cd backend
"D:\pysoft\anaconda\envs\myenv\python.exe" -m uvicorn app.main:app --reload
```

## 运行依赖（本地）

- MySQL 程序目录：D:/pysoft/mysql/mysql-8.4.8/mysql-8.4.8-winx64
- MySQL 实例配置：D:/pysoft/mysql/instances/campus/conf/my.ini
- 数据库连接默认值：mysql+pymysql://root:123456@localhost:3306/campus_waste_db

## 接口入口

- 服务地址：http://127.0.0.1:8000/
- Swagger 文档：http://127.0.0.1:8000/docs
- 检测上传接口：POST /api/v1/detections/upload

## 快速验收

1. 访问根接口，确认返回 Welcome 文案。
2. 在 Swagger 调用 POST /api/v1/detections/upload。
3. 当 has_waste=true 时，确认数据库自动新增 cleaning_tasks 任务。

## 常见问题

- ModuleNotFoundError: No module named app
	- 原因：未在 backend 目录启动。
	- 处理：先执行 cd backend，再运行 uvicorn。

- 无法解析 fastapi 导入
	- 原因：当前解释器未安装依赖。
	- 处理：使用同一解释器重新安装 backend/requirements.txt。
