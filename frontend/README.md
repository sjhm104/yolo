# 前端模块说明（Vue 3）

本模块负责无人机检测结果展示、上传交互与任务状态可视化。

当前已接入 Vue 3 + Vite + Element Plus + Axios，可直接本地运行。

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
