from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import AnyHttpUrl, BaseModel

from app.services.detector_service import (
	get_allowed_video_extensions,
	process_video_from_url,
	process_uploaded_video,
)

router = APIRouter()

UPLOAD_VIDEO_DIR = Path(__file__).resolve().parents[4] / "uploads" / "videos"
ALLOWED_VIDEO_EXTENSIONS = get_allowed_video_extensions()


class VideoDetectionResponse(BaseModel):
	output_video_url: str
	has_campus_waste: bool
	garbage_count: int
	garbage_summary: list[dict[str, object]]
	class_summary: list[dict[str, object]]


class VideoUrlAnalyzeRequest(BaseModel):
	video_url: AnyHttpUrl


def _validate_video_upload(file: UploadFile) -> str:
	suffix = Path(file.filename or "").suffix.lower()
	if suffix not in ALLOWED_VIDEO_EXTENSIONS:
		raise HTTPException(status_code=400, detail="仅支持 .mp4 或 .avi 视频")

	content_type = (file.content_type or "").lower()
	if content_type and not content_type.startswith("video/"):
		raise HTTPException(status_code=400, detail="上传文件必须是视频")

	return suffix


async def _save_uploaded_video(file: UploadFile, suffix: str) -> Path:
	UPLOAD_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

	filename = f"{uuid4().hex}{suffix}"
	saved_path = UPLOAD_VIDEO_DIR / filename

	try:
		with saved_path.open("wb") as out_file:
			while True:
				chunk = await file.read(1024 * 1024)
				if not chunk:
					break
				out_file.write(chunk)
	except OSError as exc:
		raise HTTPException(status_code=500, detail="视频保存失败") from exc
	finally:
		await file.close()

	return saved_path


@router.post("/upload-video", response_model=VideoDetectionResponse, status_code=201)
async def upload_and_detect_video(file: UploadFile = File(...)) -> VideoDetectionResponse:
	suffix = _validate_video_upload(file)
	saved_path = await _save_uploaded_video(file, suffix)

	try:
		result = await run_in_threadpool(process_uploaded_video, str(saved_path))
	except Exception as exc:
		if saved_path.exists():
			saved_path.unlink()
		raise HTTPException(status_code=500, detail="视频推理失败") from exc

	output_video_relpath = str(result["output_video_relpath"])
	return VideoDetectionResponse(
		output_video_url=f"/{output_video_relpath}",
		has_campus_waste=bool(result.get("has_campus_waste", False)),
		garbage_count=int(result.get("garbage_count", 0)),
		garbage_summary=list(result.get("garbage_summary", [])),
		class_summary=list(result.get("class_summary", [])),
	)


@router.post("/analyze-video-url", response_model=VideoDetectionResponse, status_code=201)
async def analyze_cloud_video(payload: VideoUrlAnalyzeRequest) -> VideoDetectionResponse:
	try:
		result = await run_in_threadpool(process_video_from_url, str(payload.video_url))
	except Exception as exc:
		raise HTTPException(status_code=500, detail="云端视频推理失败") from exc

	output_video_relpath = str(result["output_video_relpath"])
	return VideoDetectionResponse(
		output_video_url=f"/{output_video_relpath}",
		has_campus_waste=bool(result.get("has_campus_waste", False)),
		garbage_count=int(result.get("garbage_count", 0)),
		garbage_summary=list(result.get("garbage_summary", [])),
		class_summary=list(result.get("class_summary", [])),
	)
