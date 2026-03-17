from fastapi import APIRouter

from app.api.v1.endpoints.detection import router as detection_router

api_router = APIRouter()

api_router.include_router(
	detection_router,
	prefix="/detections",
	tags=["无人机检测"],
)
