from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
	total_detections: int
	waste_found_count: int
	pending_tasks: int
	completed_tasks: int
