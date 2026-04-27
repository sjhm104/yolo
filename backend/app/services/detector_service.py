from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

from ai.models.yolo.infer import GarbageDetector


detector = GarbageDetector()

# COCO 中可近似视为校园垃圾相关的类别（按项目口径可继续扩展）
GARBAGE_CLASS_NAMES = {
	"bottle",
	"cup",
	"bowl",
	"banana",
	"apple",
	"orange",
	"sandwich",
	"hot dog",
	"pizza",
	"donut",
	"cake",
}


UPLOAD_VIDEOS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "videos"
OUTPUT_VIDEOS_DIR = Path(__file__).resolve().parents[2] / "outputs" / "videos"


def ensure_video_dirs() -> None:
	UPLOAD_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
	OUTPUT_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def _build_output_path(input_video_path: Path) -> Path:
	return OUTPUT_VIDEOS_DIR / f"{input_video_path.stem}_{uuid4().hex}.mp4"


def _create_video_writer(output_path: Path, fps: float, width: int, height: int) -> cv2.VideoWriter:
	# 浏览器兼容优先：H.264(avc1/H264) -> mp4v 回退
	for codec in ("avc1", "H264", "mp4v"):
		writer = cv2.VideoWriter(
			str(output_path),
			cv2.VideoWriter_fourcc(*codec),
			fps,
			(width, height),
		)
		if writer.isOpened():
			return writer
		del writer

	raise ValueError("无法创建输出视频编码器")


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
	writer = _create_video_writer(output_path, fps, width, height)

	total_detections = 0
	processed_frames = 0
	class_counter: Counter[str] = Counter()

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
					cls_values = [int(cls_id) for cls_id in boxes.cls.tolist()] if boxes.cls is not None else []
					total_detections += len(cls_values)
					for class_id in cls_values:
						class_name = detector._resolve_class_name(result.names, class_id)
						class_counter[class_name] += 1
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

	if not output_path.exists() or output_path.stat().st_size == 0:
		raise ValueError("输出视频生成失败")

	garbage_counter = Counter(
		{
			name: count
			for name, count in class_counter.items()
			if name in GARBAGE_CLASS_NAMES
		}
	)
	garbage_count = int(sum(garbage_counter.values()))
	has_campus_waste = garbage_count > 0

	return {
		"output_video_relpath": f"outputs/videos/{output_path.name}",
		"total_detections": total_detections,
		"processed_frames": processed_frames,
		"has_campus_waste": has_campus_waste,
		"garbage_count": garbage_count,
		"garbage_summary": [
			{"class_name": class_name, "count": count}
			for class_name, count in garbage_counter.most_common()
		],
		"class_summary": [
			{"class_name": class_name, "count": count}
			for class_name, count in class_counter.most_common()
		],
	}


def get_allowed_video_extensions() -> set[str]:
	return {".mp4", ".avi"}


def _resolve_video_suffix(video_url: str, content_type: str | None) -> str:
	path_suffix = Path(urlparse(video_url).path).suffix.lower()
	if path_suffix in get_allowed_video_extensions():
		return path_suffix

	content_type = (content_type or "").lower()
	if "mp4" in content_type:
		return ".mp4"
	if "avi" in content_type or "x-msvideo" in content_type:
		return ".avi"

	raise ValueError("云端视频仅支持 mp4/avi")


def download_video_from_url(video_url: str) -> Path:
	ensure_video_dirs()
	headers = {
		"User-Agent": "CampusWasteDetector/1.0",
	}
	req = Request(video_url, headers=headers)

	with urlopen(req, timeout=60) as resp:
		content_type = resp.headers.get("Content-Type", "")
		suffix = _resolve_video_suffix(video_url, content_type)
		saved_path = UPLOAD_VIDEOS_DIR / f"{uuid4().hex}{suffix}"
		with saved_path.open("wb") as out_file:
			while True:
				chunk = resp.read(1024 * 1024)
				if not chunk:
					break
				out_file.write(chunk)

	if not saved_path.exists() or saved_path.stat().st_size == 0:
		raise ValueError("云端视频下载失败")

	return saved_path


def process_video_from_url(video_url: str) -> dict[str, object]:
	downloaded_video = download_video_from_url(video_url)
	return process_uploaded_video(str(downloaded_video))
