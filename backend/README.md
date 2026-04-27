# 后端模块说明（FastAPI）

本模块负责 API 服务、业务编排、数据库写入与 AI 推理调用。

## 文档同步状态

- 同步日期：2026-04-27
- 当前实现：已支持“视频上传 -> 逐帧 YOLO 推理 -> 输出视频 -> 前端回放”闭环。

## 目录说明

- app/main.py：FastAPI 启动入口、CORS 配置、/uploads 静态挂载
- app/api/v1/router.py：v1 路由聚合
- app/api/v1/endpoints/detection.py：视频上传与分析接口
- app/api/v1/endpoints/tasks.py：任务列表与状态更新
- app/api/v1/endpoints/dashboard.py：统计数据接口
- app/services/detector_service.py：AI 推理服务层（单例模型加载）
- app/services/task_scheduler.py：任务调度服务（APScheduler 定时分配）
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
- apscheduler

## 启动方式

```bash
cd backend
python -m uvicorn app.main:app --reload
```

默认地址：

- 服务入口：http://127.0.0.1:8000/
- Swagger：http://127.0.0.1:8000/docs
- OpenAPI：http://127.0.0.1:8000/openapi.json

启动行为：

- 应用 startup 时自动启动任务调度器
- 应用 shutdown 时自动停止任务调度器

## 路由概览

- POST /api/v1/detections/upload-video：上传视频并触发逐帧分析
- GET /api/v1/dashboard/stats：大屏统计
- GET /api/v1/tasks/：任务列表
- PATCH /api/v1/tasks/{task_id}/status：更新任务状态

## 任务调度模块（新增）

调度策略：

- 扫描频率：每 30 秒
- 目标任务：cleaning_tasks 中 status=pending 且 cleaner_id 为空
- 分配策略：选择 role=cleaner 的第一个用户（按 id 升序）

分配后更新字段：

- cleaner_id
- status -> assigned
- assigned_time

健壮性设计：

- max_instances=1，避免同一任务重入执行
- 条件更新（status+cleaner_id）避免并发重复分配
- 异常捕获、事务回滚与日志输出
- 预留 CleanerSelectionStrategy，后续可扩展按距离/负载策略

## 视频分析接口（对齐实现）

- 请求类型：multipart/form-data
- 字段：
	- file：视频文件（.mp4/.avi）
- 处理流程：
	- 保存视频到 backend/uploads/videos
	- 使用 OpenCV 逐帧读取
	- 每帧调用 YOLO 推理并绘制检测框
	- 导出结果视频到 backend/outputs/videos
	- 返回 output_video_url 与 total_detections 汇总
	- 使用 run_in_threadpool 执行阻塞推理，避免阻塞事件循环

示例：

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/detections/upload-video" \
	-F "file=@./tests/assets/demo.mp4"
```

## 上传与输出静态访问

后端已自动创建并挂载目录：

- 上传目录：backend/uploads（视频文件位于 uploads/videos）
- 输出目录：backend/outputs（结果视频位于 outputs/videos）
- 访问前缀：/uploads、/outputs

例如返回 output_video_url 为 /outputs/videos/demo_result.mp4，可通过 http://127.0.0.1:8000/outputs/videos/demo_result.mp4 访问。

## 快速验收

1. 启动后端并打开 Swagger。
2. 调用 POST /api/v1/detections/upload-video 上传视频。
3. 查看返回 output_video_url、total_detections、processed_frames。
4. 访问 /outputs/videos/xxx.mp4 验证输出视频可访问。

## 常见问题

- ModuleNotFoundError: No module named app
	- 原因：未在 backend 目录启动。
	- 处理：先执行 cd backend 再启动。

- 422 Unprocessable Entity（上传接口）
	- 原因：请求未使用 multipart/form-data 或字段缺失。
	- 处理：检查 file 字段是否已提交。

- 400 Bad Request（仅支持 .mp4 或 .avi 视频）
	- 原因：上传文件后缀不符合接口限制。
	- 处理：将上传文件转换为 mp4/avi 后重试。

- 上传成功但结果视频无法播放
	- 原因：output_video_url 未拼接到服务域名，或 /outputs 未挂载成功。
	- 处理：检查 app/main.py 的静态挂载与前端 URL 处理逻辑。
