# 后端模块说明（FastAPI）

本模块负责 API 服务、业务编排、数据库写入与 AI 推理调用。

## 文档同步状态

- 同步日期：2026-04-18
- 当前实现：已支持“图片上传 -> YOLO 推理 -> 记录入库 -> 自动建任务 -> 前端展示”闭环。

## 目录说明

- app/main.py：FastAPI 启动入口、CORS 配置、/uploads 静态挂载
- app/api/v1/router.py：v1 路由聚合
- app/api/v1/endpoints/detection.py：检测上传接口
- app/api/v1/endpoints/tasks.py：任务列表与状态更新
- app/api/v1/endpoints/dashboard.py：统计数据接口
- app/services/detector_service.py：AI 推理服务层（单例模型加载）
- app/db：数据库会话与 ORM 模型
- app/schemas：Pydantic 请求响应模型

## 依赖安装

在项目根目录执行：

```bash
python -m pip install -r backend/requirements.txt
```

关键依赖：

- fastapi
- uvicorn[standard]
- sqlalchemy
- pymysql
- python-multipart

## 启动方式

```bash
cd backend
python -m uvicorn app.main:app --reload
```

默认地址：

- 服务入口：http://127.0.0.1:8000/
- Swagger：http://127.0.0.1:8000/docs
- OpenAPI：http://127.0.0.1:8000/openapi.json

## 路由概览

- POST /api/v1/detections/upload：上传图片并触发识别
- GET /api/v1/dashboard/stats：大屏统计
- GET /api/v1/tasks/：任务列表
- PATCH /api/v1/tasks/{task_id}/status：更新任务状态

## 检测上传接口（对齐实现）

- 请求类型：multipart/form-data
- 字段：
	- file：图片文件（jpg/jpeg/png/bmp/webp）
	- drone_id：无人机 ID
	- latitude：纬度
	- longitude：经度
- 处理流程：
	- 保存图片到 backend/uploads
	- 调用 YOLO 推理
	- 写入 detection_records
	- 当 has_waste=true 自动创建 cleaning_tasks（PENDING）

示例：

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/detections/upload" \
	-F "file=@./tests/assets/drone_demo.jpg" \
	-F "drone_id=1" \
	-F "latitude=31.2304" \
	-F "longitude=121.4737"
```

## 上传图片静态访问

后端已自动创建并挂载目录：

- 物理目录：backend/uploads
- 访问前缀：/uploads

例如数据库中 image_url 为 uploads/abc.jpg，则可通过 http://127.0.0.1:8000/uploads/abc.jpg 访问。

## 快速验收

1. 启动后端并打开 Swagger。
2. 调用 POST /api/v1/detections/upload 上传图片。
3. 查看返回 DetectionRecord（has_waste、confidence）。
4. 若 has_waste=true，验证 cleaning_tasks 自动新增。
5. 访问 /uploads/xxx.jpg 验证图片静态可访问。

## 常见问题

- ModuleNotFoundError: No module named app
	- 原因：未在 backend 目录启动。
	- 处理：先执行 cd backend 再启动。

- 422 Unprocessable Entity（上传接口）
	- 原因：请求未使用 multipart/form-data 或字段缺失。
	- 处理：检查 file、drone_id、latitude、longitude 是否都已提交。

- 上传成功但图片无法预览
	- 原因：image_url 未拼接到服务域名，或 /uploads 未挂载成功。
	- 处理：检查 app/main.py 的静态挂载与前端 URL 处理逻辑。
