from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.services.task_scheduler import start_task_scheduler, stop_task_scheduler

app = FastAPI(title="基于无人机校园垃圾检测系统 API")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.on_event("startup")
def on_startup() -> None:
	start_task_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
	stop_task_scheduler()


@app.get("/")
def root() -> dict[str, str]:
	return {"message": "Welcome to Campus Waste Detection API"}
