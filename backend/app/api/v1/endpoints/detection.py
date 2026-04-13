import shutil
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.base import CleaningTask, CleaningTaskStatus, DetectionRecord
from app.db.session import get_db
from app.schemas.detection import DetectionRecordResponse
from app.services.detector_service import process_drone_image

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[4] / "uploads"
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _save_uploaded_file(file: UploadFile) -> tuple[Path, str]:
	if not file.content_type or not file.content_type.startswith("image/"):
		raise HTTPException(status_code=400, detail="仅支持图片文件上传")

	UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

	suffix = Path(file.filename or "").suffix.lower()
	if suffix and suffix not in ALLOWED_IMAGE_EXTENSIONS:
		raise HTTPException(status_code=400, detail="图片格式不支持")
	if not suffix:
		suffix = ".jpg"

	filename = f"{uuid4().hex}{suffix}"
	saved_path = UPLOAD_DIR / filename

	try:
		with saved_path.open("wb") as out_file:
			shutil.copyfileobj(file.file, out_file)
	except OSError as exc:
		raise HTTPException(status_code=500, detail="图片保存失败") from exc
	finally:
		file.file.close()

	return saved_path, f"uploads/{filename}"


@router.post("/upload", response_model=DetectionRecordResponse, status_code=201)
def upload_detection_result(
	file: UploadFile = File(...),
	drone_id: int = Form(...),
	latitude: Decimal = Form(...),
	longitude: Decimal = Form(...),
	db: Session = Depends(get_db),
) -> DetectionRecord:
	saved_path, image_url = _save_uploaded_file(file)

	try:
		ai_result = process_drone_image(str(saved_path))
	except Exception as exc:
		if saved_path.exists():
			saved_path.unlink()
		raise HTTPException(status_code=500, detail="AI 推理失败") from exc

	has_waste = bool(ai_result.get("has_waste", False))
	max_confidence = float(ai_result.get("max_confidence", 0.0))

	try:
		detection_record = DetectionRecord(
			drone_id=drone_id,
			image_url=image_url,
			latitude=latitude,
			longitude=longitude,
			has_waste=has_waste,
			confidence=max_confidence,
		)

		db.add(detection_record)
		db.flush()

		if has_waste:
			cleaning_task = CleaningTask(
				record_id=detection_record.id,
				status=CleaningTaskStatus.PENDING,
			)
			db.add(cleaning_task)

		db.commit()
		db.refresh(detection_record)
		return detection_record
	except SQLAlchemyError as exc:
		db.rollback()
		raise HTTPException(status_code=500, detail="检测记录写入失败") from exc
