from __future__ import annotations

import os
import time
from pathlib import Path

import cv2
from ultralytics import YOLO


class GarbageVideoDetector:
	"""基于 YOLOv8 的视频流垃圾检测器。"""

	def __init__(
		self,
		model_path: str | None = None,
		conf_threshold: float = 0.25,
		garbage_class_ids: set[int] | None = None,
	) -> None:
		self.model_path = model_path or self._default_model_path()
		self.conf_threshold = conf_threshold
		self.garbage_class_ids = garbage_class_ids or {0}
		# Ultralytics 会在本地不存在时自动下载预训练权重。
		self.model = YOLO(self.model_path)

	@staticmethod
	def _default_model_path() -> str:
		project_root = Path(__file__).resolve().parents[3]
		custom_model = project_root / "runs" / "detect" / "garbage_single" / "weights" / "best.pt"
		if custom_model.exists():
			return str(custom_model)

		bundled_model = project_root / "backend" / "yolov8n.pt"
		if bundled_model.exists():
			return str(bundled_model)

		return "yolov8n.pt"

	@staticmethod
	def _format_frame_time(seconds: float) -> str:
		total_seconds = max(0, int(seconds))
		hours = total_seconds // 3600
		minutes = (total_seconds % 3600) // 60
		secs = total_seconds % 60

		if hours > 0:
			return f"{hours:02d}:{minutes:02d}:{secs:02d}"
		return f"{minutes:02d}:{secs:02d}"

	@staticmethod
	def _annotate_frame(frame, boxes, valid_indices: list[int], names) -> object:
		annotated = frame.copy()
		for idx in valid_indices:
			coords = boxes.xyxy[idx].tolist()
			x1, y1, x2, y2 = [int(value) for value in coords]
			confidence = float(boxes.conf[idx]) if boxes.conf is not None else 0.0
			class_id = int(boxes.cls[idx]) if boxes.cls is not None else 0
			label_name = names[class_id] if isinstance(names, dict) else str(class_id)
			label = f"{label_name} {confidence:.2f}"

			cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
			cv2.putText(
				annotated,
				label,
				(x1, max(20, y1 - 10)),
				cv2.FONT_HERSHEY_SIMPLEX,
				0.6,
				(0, 255, 0),
				2,
				cv2.LINE_AA,
			)
		return annotated

	def process_video_stream(self, video_path: str, output_dir: str):
		os.makedirs(output_dir, exist_ok=True)

		cap = cv2.VideoCapture(video_path)
		if not cap.isOpened():
			raise ValueError(f"无法打开视频文件: {video_path}")

		frame_index = 0
		frame_interval = 30
		fps = cap.get(cv2.CAP_PROP_FPS)
		if not fps or fps <= 0:
			fps = 30.0

		try:
			while True:
				success, frame = cap.read()
				if not success:
					break

				if frame_index % frame_interval != 0:
					frame_index += 1
					continue

				results = self.model.predict(
					source=frame,
					conf=self.conf_threshold,
					verbose=False,
				)

				if results:
					result = results[0]
					boxes = getattr(result, "boxes", None)
					names = getattr(result, "names", {})

					if boxes is not None and len(boxes) > 0:
						valid_indices: list[int] = []
						classes = boxes.cls.tolist() if boxes.cls is not None else []
						for idx, class_id in enumerate(classes):
							if int(class_id) in self.garbage_class_ids:
								valid_indices.append(idx)

						if not valid_indices:
							frame_index += 1
							continue

						confidences = (
							[float(boxes.conf[idx]) for idx in valid_indices]
							if boxes.conf is not None
							else []
						)
						max_confidence = max((float(conf) for conf in confidences), default=0.0)

						frame_time_seconds = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
						if frame_time_seconds <= 0:
							frame_time_seconds = frame_index / fps

						frame_time = self._format_frame_time(frame_time_seconds)
						file_name = (
							f"waste_{frame_time.replace(':', '-')}_{int(time.time() * 1000)}.jpg"
						)
						saved_path = os.path.join(output_dir, file_name)

						annotated_frame = self._annotate_frame(frame, boxes, valid_indices, names)
						cv2.imwrite(saved_path, annotated_frame)

						yield {
							"frame_time": frame_time,
							"screenshot_url": os.path.relpath(saved_path),
							"has_waste": True,
							"confidence": max_confidence,
						}

				frame_index += 1
		finally:
			cap.release()
