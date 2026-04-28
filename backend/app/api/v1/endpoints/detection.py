from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.db.session import SessionLocal
from app.schemas.detection import VideoAnalyzeRequest, VideoAnalyzeResponse
from app.services.detector_service import (
	UPLOAD_VIDEOS_DIR,
	analyze_cloud_video_background,
	analyze_video_background,
	ensure_video_dirs,
)


router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parents[5]
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}


def _resolve_video_path(video_path: str) -> Path:
	candidate = Path(video_path)
	if not candidate.is_absolute():
		candidate = PROJECT_ROOT / candidate
	return candidate.resolve()


def _validate_video_upload(file: UploadFile) -> str:
	suffix = Path(file.filename or "").suffix.lower()
	if suffix not in ALLOWED_VIDEO_EXTENSIONS:
		raise HTTPException(status_code=400, detail="仅支持 mp4/avi/mov/mkv 视频")

	content_type = (file.content_type or "").lower()
	if content_type and not content_type.startswith("video/"):
		raise HTTPException(status_code=400, detail="上传文件必须是视频")

	return suffix


async def _save_uploaded_video(file: UploadFile, suffix: str) -> Path:
	ensure_video_dirs()
	filename = f"{uuid4().hex}{suffix}"
	saved_path = UPLOAD_VIDEOS_DIR / filename

	try:
		with saved_path.open("wb") as out_file:
			while True:
				chunk = await file.read(1024 * 1024)
				if not chunk:
					break
				out_file.write(chunk)
	finally:
		await file.close()

	return saved_path


@router.post("/analyze", response_model=VideoAnalyzeResponse)
async def analyze_video(
	payload: VideoAnalyzeRequest,
	background_tasks: BackgroundTasks,
) -> VideoAnalyzeResponse:
	if payload.video_path:
		resolved_path = _resolve_video_path(payload.video_path)
		if not resolved_path.exists() or not resolved_path.is_file():
			raise HTTPException(status_code=404, detail="视频文件不存在")

		background_tasks.add_task(
			analyze_video_background,
			str(resolved_path),
			SessionLocal,
			str(payload.video_path),
		)
		return VideoAnalyzeResponse(message="本地视频分析已在后台启动")

	background_tasks.add_task(
		analyze_cloud_video_background,
		str(payload.video_url),
		SessionLocal,
		payload.download_headers,
		payload.download_timeout,
		payload.download_retries,
	)
	return VideoAnalyzeResponse(message="云端视频分析已在后台启动")


@router.post("/upload-video", response_model=VideoAnalyzeResponse, status_code=201)
async def upload_video(
	background_tasks: BackgroundTasks,
	file: UploadFile = File(...),
) -> VideoAnalyzeResponse:
	suffix = _validate_video_upload(file)
	saved_path = await _save_uploaded_video(file, suffix)

	background_tasks.add_task(
		analyze_video_background,
		str(saved_path),
		SessionLocal,
		file.filename or saved_path.name,
	)
	return VideoAnalyzeResponse(message="本地上传视频分析已在后台启动")


@router.post("/analyze-video-url", response_model=VideoAnalyzeResponse)
async def analyze_video_url(
	payload: VideoAnalyzeRequest,
	background_tasks: BackgroundTasks,
) -> VideoAnalyzeResponse:
	if not payload.video_url:
		raise HTTPException(status_code=400, detail="请提供 video_url")

	background_tasks.add_task(
		analyze_cloud_video_background,
		str(payload.video_url),
		SessionLocal,
		payload.download_headers,
		payload.download_timeout,
		payload.download_retries,
	)
	return VideoAnalyzeResponse(message="云端视频分析已在后台启动")
