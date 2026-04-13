from __future__ import annotations

from pathlib import Path
from typing import Any

from ultralytics import YOLO


class GarbageDetector:
	"""基于 Ultralytics YOLO 的垃圾目标检测器。"""

	def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.25) -> None:
		self.model_path = model_path
		self.conf_threshold = conf_threshold
		self.model = YOLO(model_path)

	@staticmethod
	def _resolve_class_name(names: Any, class_id: int) -> str:
		if isinstance(names, dict):
			return str(names.get(class_id, class_id))
		if isinstance(names, (list, tuple)) and 0 <= class_id < len(names):
			return str(names[class_id])
		return str(class_id)

	def predict(self, image_path: str) -> dict[str, Any]:
		image = Path(image_path)
		if not image.exists():
			raise FileNotFoundError(f"图片不存在: {image_path}")

		results = self.model.predict(
			source=str(image),
			conf=self.conf_threshold,
			verbose=False,
		)
		if not results:
			return {
				"has_waste": False,
				"max_confidence": 0.0,
				"bboxes": [],
			}

		result = results[0]
		boxes = getattr(result, "boxes", None)
		names = getattr(result, "names", {})

		bboxes: list[dict[str, Any]] = []
		max_confidence = 0.0

		if boxes is not None:
			for box in boxes:
				coords = box.xyxy[0].tolist()
				confidence = float(box.conf.item()) if box.conf is not None else 0.0
				class_id = int(box.cls.item()) if box.cls is not None else -1
				class_name = self._resolve_class_name(names, class_id)

				max_confidence = max(max_confidence, confidence)
				bboxes.append(
					{
						"class_id": class_id,
						"class_name": class_name,
						"confidence": confidence,
						"x1": float(coords[0]),
						"y1": float(coords[1]),
						"x2": float(coords[2]),
						"y2": float(coords[3]),
					}
				)

		return {
			"has_waste": len(bboxes) > 0,
			"max_confidence": max_confidence,
			"bboxes": bboxes,
		}
