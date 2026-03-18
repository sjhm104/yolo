from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.db.base import CleaningTask, CleaningTaskStatus, User
from app.db.session import get_db
from app.schemas.task import CleaningTaskResponse, CleaningTaskUpdate

router = APIRouter()


@router.get("/", response_model=list[CleaningTaskResponse])
def list_tasks(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    status: Optional[CleaningTaskStatus] = Query(default=None),
    db: Session = Depends(get_db),
) -> list[CleaningTask]:
    query = db.query(CleaningTask).options(joinedload(CleaningTask.record))

    if status is not None:
        query = query.filter(CleaningTask.status == status)

    tasks = (
        query.order_by(CleaningTask.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return tasks


@router.patch("/{task_id}/status", response_model=CleaningTaskResponse)
def update_task_status(
    task_id: int,
    payload: CleaningTaskUpdate,
    db: Session = Depends(get_db),
) -> CleaningTask:
    if payload.status is None and payload.cleaner_id is None:
        raise HTTPException(status_code=400, detail="至少需要提供 status 或 cleaner_id")

    task = (
        db.query(CleaningTask)
        .options(joinedload(CleaningTask.record))
        .filter(CleaningTask.id == task_id)
        .first()
    )
    if task is None:
        raise HTTPException(status_code=404, detail="清理任务不存在")

    if payload.cleaner_id is not None:
        cleaner = db.query(User).filter(User.id == payload.cleaner_id).first()
        if cleaner is None:
            raise HTTPException(status_code=404, detail="环卫人员不存在")
        task.cleaner_id = payload.cleaner_id
        if task.assigned_time is None:
            task.assigned_time = datetime.utcnow()

    if payload.status is not None:
        task.status = payload.status
        if payload.status == CleaningTaskStatus.COMPLETED:
            task.completed_time = datetime.utcnow()
        else:
            task.completed_time = None
            if payload.status == CleaningTaskStatus.ASSIGNED and task.assigned_time is None:
                task.assigned_time = datetime.utcnow()

    try:
        db.commit()
        db.refresh(task)
        return task
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="更新任务状态失败") from exc
