# AI 模块说明（PyTorch / YOLO）

本模块负责数据处理、模型训练、推理与模型导出，独立于后端 API，便于算法迭代。

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

## 建议流程

1. 在 configs 中维护实验配置。
2. 使用 models/yolo/train.py 进行训练。
3. 使用 models/yolo/infer.py 进行推理验证。
4. 使用 models/yolo/export.py 导出部署模型。

## 与后端协作

后端建议通过服务层调用本模块推理能力，不直接耦合训练逻辑。
