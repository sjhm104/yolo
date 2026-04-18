# AI 模块说明（PyTorch / YOLO）

本模块负责数据处理、模型训练、推理与模型导出，独立于后端 API，便于算法迭代。

## 文档同步状态

- 同步日期：2026-04-18
- 当前实现：后端已通过 services 层接入本模块的 YOLO 推理。

## 目录说明

- models/yolo：YOLO 训练、推理、导出脚本
- models/common：通用数据集与预处理逻辑
- configs：模型配置文件
- weights：模型权重文件目录
- notebooks：实验记录与分析草稿

## 依赖安装

可使用本模块依赖文件：

```bash
pip install -r ai/requirements.txt
```

关键依赖：

- ultralytics
- torch
- torchvision
- opencv-python
- numpy

## 当前推理实现

核心文件：models/yolo/infer.py

已实现类：GarbageDetector

- 默认加载模型：yolov8n.pt
- 推理接口：predict(image_path)
- 返回结构：
	- has_waste：是否检测到目标
	- max_confidence：最大置信度
	- bboxes：检测框列表（类别、坐标、置信度）

说明：

- 推理结果已被后端写入 detection_records。
- 当前业务中 has_waste 的判定依据为检测框数量是否大于 0。

## 建议流程

1. 在 configs 中维护实验配置。
2. 使用 models/yolo/train.py 进行训练。
3. 使用 models/yolo/infer.py 进行推理验证。
4. 使用 models/yolo/export.py 导出部署模型。

## 与后端协作

后端建议通过服务层调用本模块推理能力，不直接耦合训练逻辑。

当前对接方式：

- backend/app/services/detector_service.py 在服务启动时单例加载 GarbageDetector。
- 上传接口将图片保存后调用 process_drone_image(image_path)。
- 发生推理异常时后端会返回 500，并回滚业务写入。

说明：AI 模块本身不直接依赖 MySQL，数据库读写由后端完成（当前本地实例位于 D:/pysoft/mysql/instances/campus）。
