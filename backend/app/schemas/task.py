from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.db.base import CleaningTaskStatus


class CleaningTaskUpdate(BaseModel):
    status: Optional[CleaningTaskStatus] = None
    cleaner_id: Optional[int] = None


class DetectionRecordBrief(BaseModel):
    image_url: str
    latitude: Decimal
    longitude: Decimal
    detected_time: datetime

    model_config = ConfigDict(from_attributes=True)


class CleaningTaskResponse(BaseModel):
    id: int
    record_id: int
    cleaner_id: Optional[int] = None
    status: CleaningTaskStatus
    assigned_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    detection_record: DetectionRecordBrief = Field(validation_alias="record")

    model_config = ConfigDict(from_attributes=True)
