from __future__ import annotations

import socket
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

from ai.models.yolo.infer import GarbageVideoDetector

from app.db.base import CleaningTask, CleaningTaskStatus, DetectionRecord


detector = GarbageVideoDetector()
UPLOAD_VIDEOS_DIR = Path(__file__).resolve().parents[2] / "uploads" / "videos"
OUTPUT_SCREENSHOTS_DIR = Path(__file__).resolve().parents[2] / "outputs" / "screenshots"
OUTPUT_VIDEOS_DIR = Path(__file__).resolve().parents[2] / "outputs" / "videos"
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
DEFAULT_DOWNLOAD_HEADERS = {
	"User-Agent": "CampusWasteDetector/1.0",
	"Accept": "*/*",
	"Connection": "keep-alive",
}
DEFAULT_DOWNLOAD_TIMEOUT = 60
DEFAULT_DOWNLOAD_RETRIES = 3
DEFAULT_CHUNK_SIZE = 1024 * 1024
MAX_DOWNLOAD_SIZE_BYTES = 1024 * 1024 * 1024


def ensure_video_dirs() -> None:
	UPLOAD_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
	OUTPUT_SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
	OUTPUT_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def _build_screenshot_url(raw_path: str) -> str:
	file_name = Path(raw_path).name
	return f"/outputs/screenshots/{file_name}"


def _resolve_video_suffix(video_url: str, content_type: str | None) -> str:
	path_suffix = Path(urlparse(video_url).path).suffix.lower()
	if path_suffix in ALLOWED_VIDEO_EXTENSIONS:
		return path_suffix

	content_type = (content_type or "").lower()
	if "mp4" in content_type:
		return ".mp4"
	if "avi" in content_type or "x-msvideo" in content_type:
		return ".avi"
	if "quicktime" in content_type:
		return ".mov"
	if "matroska" in content_type:
		return ".mkv"

	return ".mp4"


def _build_output_video_path(video_path: str, video_source: str | None = None) -> Path:
	source_name = video_source or Path(video_path).stem
	safe_stem = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in source_name)
	safe_stem = safe_stem.strip("_") or Path(video_path).stem or "analysis"
	return OUTPUT_VIDEOS_DIR / f"{safe_stem}_{uuid4().hex[:8]}_result.mp4"


def _sanitize_headers(headers: dict[str, str] | None) -> dict[str, str]:
	safe_headers = dict(DEFAULT_DOWNLOAD_HEADERS)
	for key, value in (headers or {}).items():
		header_key = str(key).strip()
		header_value = str(value).strip()
		if not header_key or not header_value:
			continue
		safe_headers[header_key] = header_value
	return safe_headers


def download_video_from_url(
	video_url: str,
	headers: dict[str, str] | None = None,
	timeout: int = DEFAULT_DOWNLOAD_TIMEOUT,
	retries: int = DEFAULT_DOWNLOAD_RETRIES,
) -> Path:
	ensure_video_dirs()
	request_headers = _sanitize_headers(headers)
	last_error: Exception | None = None

	for attempt in range(1, max(1, retries) + 1):
		saved_path: Path | None = None
		try:
			req = Request(video_url, headers=request_headers)

			with urlopen(req, timeout=timeout) as resp:
				content_type = resp.headers.get("Content-Type", "")
				content_length = resp.headers.get("Content-Length")
				if content_length and int(content_length) > MAX_DOWNLOAD_SIZE_BYTES:
					raise ValueError("云端视频文件过大，超过 1GB 限制")

				suffix = _resolve_video_suffix(video_url, content_type)
				saved_path = UPLOAD_VIDEOS_DIR / f"{uuid4().hex}{suffix}"

				total_bytes = 0
				with saved_path.open("wb") as out_file:
					while True:
						chunk = resp.read(DEFAULT_CHUNK_SIZE)
						if not chunk:
							break
						total_bytes += len(chunk)
						if total_bytes > MAX_DOWNLOAD_SIZE_BYTES:
							raise ValueError("云端视频下载中止：文件超过 1GB 限制")
						out_file.write(chunk)

			if not saved_path.exists() or saved_path.stat().st_size == 0:
				raise ValueError("云端视频下载失败：文件为空")

			return saved_path
		except (HTTPError, URLError, TimeoutError, socket.timeout, ValueError) as exc:
			last_error = exc
			if saved_path and saved_path.exists():
				saved_path.unlink()
			if attempt < max(1, retries):
				time.sleep(min(attempt, 3))
				continue
			break

	assert last_error is not None
	raise ValueError(f"云端视频下载失败: {last_error}") from last_error


def _analyze_video_background_sync(video_path: str, db_session: Any, video_source: str | None = None) -> None:
	ensure_video_dirs()

	session: Session
	owns_session = callable(db_session)
	session = db_session() if owns_session else db_session

	try:
		source_name = video_source or Path(video_path).name
		output_video_path = _build_output_video_path(video_path, video_source)

		for detection in detector.process_video_stream(
			video_path,
			str(OUTPUT_SCREENSHOTS_DIR),
			output_video_path=str(output_video_path),
		):
			record = DetectionRecord(
				video_source=source_name,
				frame_time=str(detection["frame_time"]),
				screenshot_url=_build_screenshot_url(str(detection["screenshot_url"])),
				has_waste=bool(detection["has_waste"]),
				confidence=float(detection["confidence"]),
			)
			session.add(record)
			session.flush()

			task = CleaningTask(
				record_id=record.id,
				status=CleaningTaskStatus.PENDING,
			)
			session.add(task)
			session.commit()
	except Exception:
		session.rollback()
		raise
	finally:
		if owns_session:
			session.close()


def _analyze_cloud_video_background_sync(
	video_url: str,
	db_session: Any,
	download_headers: dict[str, str] | None = None,
	download_timeout: int = DEFAULT_DOWNLOAD_TIMEOUT,
	download_retries: int = DEFAULT_DOWNLOAD_RETRIES,
) -> None:
	downloaded_video = download_video_from_url(
		video_url,
		headers=download_headers,
		timeout=download_timeout,
		retries=download_retries,
	)
	_analyze_video_background_sync(
		str(downloaded_video),
		db_session,
		video_source=video_url,
	)


async def analyze_video_background(
	video_path: str,
	db_session: Any,
	video_source: str | None = None,
) -> None:
	await run_in_threadpool(
		_analyze_video_background_sync,
		video_path,
		db_session,
		video_source,
	)


async def analyze_cloud_video_background(
	video_url: str,
	db_session: Any,
	download_headers: dict[str, str] | None = None,
	download_timeout: int = DEFAULT_DOWNLOAD_TIMEOUT,
	download_retries: int = DEFAULT_DOWNLOAD_RETRIES,
) -> None:
	await run_in_threadpool(
		_analyze_cloud_video_background_sync,
		video_url,
		db_session,
		download_headers,
		download_timeout,
		download_retries,
	)
