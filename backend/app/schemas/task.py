from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.db.base import CleaningTaskStatus
from app.schemas.detection import DetectionRecordResponse
from app.schemas.worker import WorkerResponse


class CleaningTaskAssignRequest(BaseModel):
	worker_id: int


class CleaningTaskResponse(BaseModel):
	id: int
	record_id: int
	worker_id: Optional[int] = None
	status: CleaningTaskStatus
	created_at: datetime
	completed_at: Optional[datetime] = None
	record: DetectionRecordResponse
	worker: Optional[WorkerResponse] = None

	model_config = ConfigDict(from_attributes=True)
