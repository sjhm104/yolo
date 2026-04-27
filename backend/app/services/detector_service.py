from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

from ai.models.yolo.infer import GarbageDetector


detector = GarbageDetector()


UPLOAD_VIDEOS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "videos"
OUTPUT_VIDEOS_DIR = Path(__file__).resolve().parents[2] / "outputs" / "videos"


def ensure_video_dirs() -> None:
	UPLOAD_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
	OUTPUT_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def _build_output_path(input_video_path: Path) -> Path:
	return OUTPUT_VIDEOS_DIR / f"{input_video_path.stem}_{uuid4().hex}.mp4"


def process_uploaded_video(input_video_path: str) -> dict[str, object]:
	"""逐帧处理上传视频并输出带框结果视频。"""
	ensure_video_dirs()

	source = Path(input_video_path)
	if not source.exists():
		raise FileNotFoundError(f"视频不存在: {input_video_path}")

	cap = cv2.VideoCapture(str(source))
	if not cap.isOpened():
		raise ValueError("无法读取视频文件")

	fps = cap.get(cv2.CAP_PROP_FPS)
	if not fps or fps <= 0:
		fps = 25.0

	width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
	if width <= 0 or height <= 0:
		cap.release()
		raise ValueError("视频分辨率异常")

	output_path = _build_output_path(source)
	fourcc = cv2.VideoWriter_fourcc(*"mp4v")
	writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
	if not writer.isOpened():
		cap.release()
		raise ValueError("无法写入输出视频")

	total_detections = 0
	processed_frames = 0

	try:
		while True:
			success, frame = cap.read()
			if not success:
				break

			results = detector.model.predict(
				source=frame,
				conf=detector.conf_threshold,
				verbose=False,
			)
			if results:
				result = results[0]
				boxes = getattr(result, "boxes", None)
				if boxes is not None:
					total_detections += len(boxes)
				annotated_frame = result.plot()
			else:
				annotated_frame = frame

			writer.write(annotated_frame)
			processed_frames += 1
	finally:
		cap.release()
		writer.release()

	if processed_frames == 0:
		if output_path.exists():
			output_path.unlink()
		raise ValueError("视频没有可处理的帧")

	return {
		"output_video_relpath": f"outputs/videos/{output_path.name}",
		"total_detections": total_detections,
		"processed_frames": processed_frames,
	}


def get_allowed_video_extensions() -> set[str]:
	return {".mp4", ".avi"}
