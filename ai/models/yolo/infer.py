from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
from ultralytics import YOLO

class GarbageVideoDetector:
	"""基于 YOLOv8 的视频流垃圾检测器。"""

	def __init__(
		self,
		model_path: str | None = None,
		conf_threshold: float = 0.6,
		garbage_class_ids: set[int] | None = None,
		frame_interval: int = 30,
		min_report_interval_seconds: float = 8.0,
		duplicate_iou_threshold: float = 0.5,
		frame_similarity_threshold: float = 0.96,
	) -> None:
		self.model_path = model_path or self._default_model_path()
		self.conf_threshold = conf_threshold
		self.garbage_class_ids = garbage_class_ids or {0}
		self.frame_interval = max(1, frame_interval)
		self.min_report_interval_seconds = max(0.0, min_report_interval_seconds)
		self.duplicate_iou_threshold = duplicate_iou_threshold
		self.frame_similarity_threshold = frame_similarity_threshold
		self._last_report_signature: np.ndarray | None = None
		self._last_report_boxes: list[tuple[float, float, float, float]] = []
		self._last_report_time_seconds: float | None = None
		self.model = YOLO(self.model_path)

	@staticmethod
	def _default_model_path() -> str:
		project_root = Path(__file__).resolve().parents[3]
		runs_dir = project_root / "runs" / "detect"
		patterns = [
			"uav_waste_p2_eiou*/weights/best.pt",
			"garbage_single*/weights/best.pt",
			"combined_garbage_finetune*/weights/best.pt",
			"combined_garbage*/weights/best.pt",
			"uav_waste_single*/weights/best.pt",
		]
		for pattern in patterns:
			custom_candidates = sorted(
				runs_dir.glob(pattern),
				key=lambda path: path.stat().st_mtime,
				reverse=True,
			)
			for custom_model in custom_candidates:
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

	@staticmethod
	def _frame_signature(frame: np.ndarray) -> np.ndarray:
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		thumb = cv2.resize(gray, (16, 16), interpolation=cv2.INTER_AREA)
		return (thumb >= float(thumb.mean())).astype(np.uint8)

	@staticmethod
	def _signature_similarity(left: np.ndarray | None, right: np.ndarray | None) -> float:
		if left is None or right is None:
			return 0.0
		return float((left == right).mean())

	@staticmethod
	def _box_iou(
		left: tuple[float, float, float, float],
		right: tuple[float, float, float, float],
	) -> float:
		x1 = max(left[0], right[0])
		y1 = max(left[1], right[1])
		x2 = min(left[2], right[2])
		y2 = min(left[3], right[3])
		inter_w = max(0.0, x2 - x1)
		inter_h = max(0.0, y2 - y1)
		intersection = inter_w * inter_h
		if intersection <= 0:
			return 0.0

		left_area = max(0.0, left[2] - left[0]) * max(0.0, left[3] - left[1])
		right_area = max(0.0, right[2] - right[0]) * max(0.0, right[3] - right[1])
		union = left_area + right_area - intersection
		if union <= 0:
			return 0.0
		return intersection / union

	@staticmethod
	def _normalized_boxes(
		boxes,
		valid_indices: Iterable[int],
		frame_width: int,
		frame_height: int,
	) -> list[tuple[float, float, float, float]]:
		normalized: list[tuple[float, float, float, float]] = []
		for idx in valid_indices:
			x1, y1, x2, y2 = boxes.xyxy[idx].tolist()
			normalized.append(
				(
					float(x1) / max(1, frame_width),
					float(y1) / max(1, frame_height),
					float(x2) / max(1, frame_width),
					float(y2) / max(1, frame_height),
				)
			)
		return normalized

	def _is_duplicate_detection(
		self,
		frame_time_seconds: float,
		frame: np.ndarray,
		current_boxes: list[tuple[float, float, float, float]],
	) -> bool:
		if not current_boxes:
			return False
		if self._last_report_time_seconds is None:
			return False

		time_gap = frame_time_seconds - self._last_report_time_seconds
		frame_similarity = self._signature_similarity(
			self._last_report_signature,
			self._frame_signature(frame),
		)

		max_iou = 0.0
		for current_box in current_boxes:
			for last_box in self._last_report_boxes:
				max_iou = max(max_iou, self._box_iou(current_box, last_box))

		if time_gap < self.min_report_interval_seconds and max_iou >= 0.25:
			return True

		return (
			frame_similarity >= self.frame_similarity_threshold
			and max_iou >= self.duplicate_iou_threshold
		)

	def _remember_detection(
		self,
		frame_time_seconds: float,
		frame: np.ndarray,
		current_boxes: list[tuple[float, float, float, float]],
	) -> None:
		self._last_report_time_seconds = frame_time_seconds
		self._last_report_signature = self._frame_signature(frame)
		self._last_report_boxes = current_boxes

	def process_video_stream(
		self,
		video_path: str,
		output_dir: str,
		output_video_path: str | None = None,
	):
		os.makedirs(output_dir, exist_ok=True)
		if output_video_path:
			Path(output_video_path).parent.mkdir(parents=True, exist_ok=True)

		cap = cv2.VideoCapture(video_path)
		if not cap.isOpened():
			raise ValueError(f"无法打开视频文件: {video_path}")

		self._last_report_signature = None
		self._last_report_boxes = []
		self._last_report_time_seconds = None

		frame_index = 0
		fps = cap.get(cv2.CAP_PROP_FPS)
		if not fps or fps <= 0:
			fps = 30.0
		frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 0
		frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 0
		video_writer = None
		if output_video_path and frame_width > 0 and frame_height > 0:
			fourcc = cv2.VideoWriter_fourcc(*"mp4v")
			video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

		try:
			while True:
				success, frame = cap.read()
				if not success:
					break

				annotated_for_video = frame
				if frame_index % self.frame_interval != 0:
					if video_writer is not None:
						video_writer.write(annotated_for_video)
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
							confidence = float(boxes.conf[idx]) if boxes.conf is not None else 0.0
							if int(class_id) in self.garbage_class_ids and confidence >= self.conf_threshold:
								valid_indices.append(idx)

						if not valid_indices:
							if video_writer is not None:
								video_writer.write(annotated_for_video)
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

						normalized_boxes = self._normalized_boxes(
							boxes,
							valid_indices,
							frame.shape[1],
							frame.shape[0],
						)
						annotated_frame = self._annotate_frame(frame, boxes, valid_indices, names)
						annotated_for_video = annotated_frame

						if self._is_duplicate_detection(
							frame_time_seconds,
							frame,
							normalized_boxes,
						):
							if video_writer is not None:
								video_writer.write(annotated_for_video)
							frame_index += 1
							continue

						frame_time = self._format_frame_time(frame_time_seconds)
						file_name = (
							f"waste_{frame_time.replace(':', '-')}_{int(time.time() * 1000)}.jpg"
						)
						saved_path = os.path.join(output_dir, file_name)

						cv2.imwrite(saved_path, annotated_frame)
						self._remember_detection(frame_time_seconds, frame, normalized_boxes)

						yield {
							"frame_time": frame_time,
							"screenshot_url": os.path.relpath(saved_path),
							"has_waste": True,
							"confidence": max_confidence,
						}

				if video_writer is not None:
					video_writer.write(annotated_for_video)
				frame_index += 1
		finally:
			cap.release()
			if video_writer is not None:
				video_writer.release()
