from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WorkerResponse(BaseModel):
	id: int
	name: str
	phone: str
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
