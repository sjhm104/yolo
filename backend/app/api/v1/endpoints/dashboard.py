from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import CleaningTask, CleaningTaskStatus, DetectionRecord
from app.db.session import get_db
from app.schemas.dashboard import DashboardStatsResponse


router = APIRouter()
OUTPUT_DIR = Path(__file__).resolve().parents[3] / "outputs"
UPLOAD_VIDEOS_DIR = Path(__file__).resolve().parents[3] / "uploads" / "videos"


def _build_dashboard_stats(db: Session) -> DashboardStatsResponse:
	total_detections = db.query(DetectionRecord).count()
	waste_found_count = (
		db.query(DetectionRecord)
		.filter(DetectionRecord.has_waste.is_(True))
		.count()
	)
	pending_tasks = (
		db.query(CleaningTask)
		.filter(CleaningTask.status == CleaningTaskStatus.PENDING)
		.count()
	)
	unassigned_tasks = (
		db.query(CleaningTask)
		.filter(
			CleaningTask.status == CleaningTaskStatus.PENDING,
			CleaningTask.worker_id.is_(None),
		)
		.count()
	)
	assigned_tasks = (
		db.query(CleaningTask)
		.filter(
			CleaningTask.status == CleaningTaskStatus.PENDING,
			CleaningTask.worker_id.is_not(None),
		)
		.count()
	)
	completed_tasks = (
		db.query(CleaningTask)
		.filter(CleaningTask.status == CleaningTaskStatus.COMPLETED)
		.count()
	)

	return DashboardStatsResponse(
		total_detections=total_detections,
		waste_found_count=waste_found_count,
		pending_tasks=pending_tasks,
		unassigned_tasks=unassigned_tasks,
		assigned_tasks=assigned_tasks,
		completed_tasks=completed_tasks,
	)


def _clear_directory_files(directory: Path) -> None:
	if not directory.exists():
		return
	for path in directory.rglob("*"):
		if path.is_file():
			path.unlink()


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)) -> DashboardStatsResponse:
	return _build_dashboard_stats(db)


@router.post("/reset", response_model=DashboardStatsResponse)
def reset_dashboard_data(db: Session = Depends(get_db)) -> DashboardStatsResponse:
	db.query(CleaningTask).delete(synchronize_session=False)
	db.query(DetectionRecord).delete(synchronize_session=False)
	db.commit()

	_clear_directory_files(OUTPUT_DIR / "screenshots")
	_clear_directory_files(OUTPUT_DIR / "videos")
	_clear_directory_files(UPLOAD_VIDEOS_DIR)

	return _build_dashboard_stats(db)
