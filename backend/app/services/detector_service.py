from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

from ai.models.yolo.infer import GarbageDetector


detector = GarbageDetector()


def process_drone_image(image_path: str) -> dict[str, Any]:
	"""接收无人机图像路径，调用 YOLO 推理并返回结构化结果。"""
	return detector.predict(image_path)
