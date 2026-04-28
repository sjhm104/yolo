from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.db.base import CleaningTask, CleaningTaskStatus, Worker
from app.db.session import get_db
from app.schemas.task import CleaningTaskAssignRequest, CleaningTaskResponse


router = APIRouter()


@router.get("/", response_model=list[CleaningTaskResponse])
def list_tasks(
	skip: int = Query(default=0, ge=0),
	limit: int = Query(default=20, ge=1, le=100),
	status: Optional[CleaningTaskStatus] = Query(default=None),
	db: Session = Depends(get_db),
) -> list[CleaningTask]:
	query = db.query(CleaningTask).options(
		joinedload(CleaningTask.record),
		joinedload(CleaningTask.worker),
	)

	if status is not None:
		query = query.filter(CleaningTask.status == status)

	return (
		query.order_by(CleaningTask.created_at.desc())
		.offset(skip)
		.limit(limit)
		.all()
	)


@router.patch("/{task_id}/assign", response_model=CleaningTaskResponse)
def assign_task(
	task_id: int,
	payload: CleaningTaskAssignRequest,
	db: Session = Depends(get_db),
) -> CleaningTask:
	task = (
		db.query(CleaningTask)
		.options(joinedload(CleaningTask.record), joinedload(CleaningTask.worker))
		.filter(CleaningTask.id == task_id)
		.first()
	)
	if task is None:
		raise HTTPException(status_code=404, detail="清理任务不存在")

	worker = db.query(Worker).filter(Worker.id == payload.worker_id).first()
	if worker is None:
		raise HTTPException(status_code=404, detail="环卫工人不存在")

	task.worker_id = worker.id
	db.commit()
	db.refresh(task)
	return task


@router.patch("/{task_id}/complete", response_model=CleaningTaskResponse)
def complete_task(
	task_id: int,
	db: Session = Depends(get_db),
) -> CleaningTask:
	task = (
		db.query(CleaningTask)
		.options(joinedload(CleaningTask.record), joinedload(CleaningTask.worker))
		.filter(CleaningTask.id == task_id)
		.first()
	)
	if task is None:
		raise HTTPException(status_code=404, detail="清理任务不存在")

	task.status = CleaningTaskStatus.COMPLETED
	task.completed_at = datetime.utcnow()
	db.commit()
	db.refresh(task)
	return task
