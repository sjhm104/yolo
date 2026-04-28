from __future__ import annotations

import os
import time

import cv2
from ultralytics import YOLO


class GarbageVideoDetector:
	"""基于 YOLOv8 的视频流垃圾检测器。"""

	def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.25) -> None:
		self.model_path = model_path
		self.conf_threshold = conf_threshold
		# Ultralytics 会在本地不存在时自动下载预训练权重。
		self.model = YOLO(model_path)

	@staticmethod
	def _format_frame_time(seconds: float) -> str:
		total_seconds = max(0, int(seconds))
		hours = total_seconds // 3600
		minutes = (total_seconds % 3600) // 60
		secs = total_seconds % 60

		if hours > 0:
			return f"{hours:02d}:{minutes:02d}:{secs:02d}"
		return f"{minutes:02d}:{secs:02d}"

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

					if boxes is not None and len(boxes) > 0:
						confidences = boxes.conf.tolist() if boxes.conf is not None else []
						max_confidence = max((float(conf) for conf in confidences), default=0.0)

						frame_time_seconds = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
						if frame_time_seconds <= 0:
							frame_time_seconds = frame_index / fps

						frame_time = self._format_frame_time(frame_time_seconds)
						file_name = (
							f"waste_{frame_time.replace(':', '-')}_{int(time.time() * 1000)}.jpg"
						)
						saved_path = os.path.join(output_dir, file_name)

						annotated_frame = result.plot()
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
