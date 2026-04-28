from datetime import datetime
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, model_validator


class VideoAnalyzeRequest(BaseModel):
	video_path: Optional[str] = None
	video_url: Optional[AnyHttpUrl] = None
	download_headers: Optional[dict[str, str]] = None
	download_timeout: int = Field(default=60, ge=5, le=300)
	download_retries: int = Field(default=3, ge=1, le=5)

	@model_validator(mode="after")
	def validate_source(self) -> "VideoAnalyzeRequest":
		if bool(self.video_path) == bool(self.video_url):
			raise ValueError("必须提供 video_path 或 video_url，且两者只能传一个")
		return self


class VideoAnalyzeResponse(BaseModel):
	message: str


class DetectionRecordResponse(BaseModel):
	id: int
	video_source: str
	frame_time: str
	screenshot_url: str
	has_waste: bool
	confidence: float
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
