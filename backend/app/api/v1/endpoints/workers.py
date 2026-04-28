from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.base import Worker
from app.db.session import get_db
from app.schemas.worker import WorkerResponse


router = APIRouter()


@router.get("/", response_model=list[WorkerResponse])
def list_workers(db: Session = Depends(get_db)) -> list[Worker]:
	return db.query(Worker).order_by(Worker.id.asc()).all()
