from fastapi import APIRouter

from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.detection import router as detection_router
from app.api.v1.endpoints.tasks import router as tasks_router

api_router = APIRouter()

api_router.include_router(
	detection_router,
	prefix="/detections",
	tags=["无人机检测"],
)

api_router.include_router(
	tasks_router,
	prefix="/tasks",
	tags=["清理任务管理"],
)

api_router.include_router(
	dashboard_router,
	prefix="/dashboard",
	tags=["大屏统计"],
)
