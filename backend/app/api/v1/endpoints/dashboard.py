from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import CleaningTask, CleaningTaskStatus, DetectionRecord
from app.db.session import get_db
from app.schemas.dashboard import DashboardStatsResponse

router = APIRouter()


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)) -> DashboardStatsResponse:
    total_detections = db.query(DetectionRecord).count()
    waste_found_count = db.query(DetectionRecord).filter(DetectionRecord.has_waste.is_(True)).count()
    pending_tasks = db.query(CleaningTask).filter(CleaningTask.status == CleaningTaskStatus.PENDING).count()
    completed_tasks = db.query(CleaningTask).filter(CleaningTask.status == CleaningTaskStatus.COMPLETED).count()

    return DashboardStatsResponse(
        total_detections=total_detections,
        waste_found_count=waste_found_count,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
    )
