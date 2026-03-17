from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.base import CleaningTask, CleaningTaskStatus, DetectionRecord
from app.db.session import get_db
from app.schemas.detection import DetectionRecordCreate, DetectionRecordResponse

router = APIRouter()


@router.post("/upload", response_model=DetectionRecordResponse, status_code=201)
def upload_detection_result(
	payload: DetectionRecordCreate,
	db: Session = Depends(get_db),
) -> DetectionRecord:
	try:
		detection_record = DetectionRecord(
			drone_id=payload.drone_id,
			image_url=payload.image_url,
			latitude=payload.latitude,
			longitude=payload.longitude,
			has_waste=payload.has_waste,
			confidence=payload.confidence,
		)

		db.add(detection_record)
		db.flush()

		if payload.has_waste:
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
