from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DetectionRecordCreate(BaseModel):
	drone_id: Optional[int] = None
	image_url: str
	latitude: Decimal
	longitude: Decimal
	has_waste: bool
	confidence: Optional[float] = None


class DetectionRecordResponse(BaseModel):
	id: int
	drone_id: Optional[int] = None
	image_url: str
	latitude: Decimal
	longitude: Decimal
	has_waste: bool
	confidence: Optional[float] = None
	detected_time: datetime
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)
