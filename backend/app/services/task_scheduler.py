from __future__ import annotations

import logging
from typing import Optional, Protocol

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.base import CleaningTask, CleaningTaskStatus, Worker
from app.db.session import SessionLocal


logger = logging.getLogger(__name__)

SCHEDULER_JOB_ID = "assign_pending_cleaning_tasks"
SCHEDULER_INTERVAL_SECONDS = 30


class WorkerSelectionStrategy(Protocol):
	"""环卫工人选择策略接口，后续可扩展为距离/负载等复杂策略。"""

	def select_worker(self, db: Session) -> Optional[Worker]:
		...


class FirstAvailableWorkerStrategy:
	"""简单策略：选择第一个可用环卫工人。"""

	def select_worker(self, db: Session) -> Optional[Worker]:
		return db.query(Worker).order_by(Worker.id.asc()).first()


class TaskSchedulerService:
	"""定时扫描待分配任务并自动指派环卫工人。"""

	def __init__(self, strategy: WorkerSelectionStrategy | None = None) -> None:
		self.strategy = strategy or FirstAvailableWorkerStrategy()
		self.scheduler = BackgroundScheduler()

	def start(self) -> None:
		if self.scheduler.running:
			logger.info("任务调度器已在运行，跳过重复启动")
			return

		self.scheduler.add_job(
			self.assign_pending_tasks,
			trigger="interval",
			seconds=SCHEDULER_INTERVAL_SECONDS,
			id=SCHEDULER_JOB_ID,
			replace_existing=True,
			max_instances=1,
			coalesce=True,
		)
		self.scheduler.start()
		logger.info("任务调度器已启动，扫描间隔 %s 秒", SCHEDULER_INTERVAL_SECONDS)

	def stop(self) -> None:
		if not self.scheduler.running:
			return

		self.scheduler.shutdown(wait=False)
		logger.info("任务调度器已停止")

	def assign_pending_tasks(self) -> None:
		db = SessionLocal()
		try:
			worker = self.strategy.select_worker(db)
			if worker is None:
				logger.warning("未找到可分配的环卫工人，任务分配跳过")
				return

			pending_task_ids = [
				task_id
				for (task_id,) in (
					db.query(CleaningTask.id)
					.filter(
						CleaningTask.status == CleaningTaskStatus.PENDING,
						CleaningTask.worker_id.is_(None),
					)
					.order_by(CleaningTask.created_at.asc())
					.all()
				)
			]

			if not pending_task_ids:
				logger.debug("当前无待分配任务")
				return

			assigned_count = 0

			for task_id in pending_task_ids:
				updated_rows = (
					db.query(CleaningTask)
					.filter(
						CleaningTask.id == task_id,
						CleaningTask.status == CleaningTaskStatus.PENDING,
						CleaningTask.worker_id.is_(None),
					)
					.update(
						{
							CleaningTask.worker_id: worker.id,
						},
						synchronize_session=False,
					)
				)
				if updated_rows:
					assigned_count += 1

			db.commit()
			if assigned_count:
				logger.info(
					"任务调度完成：worker_id=%s，本轮分配 %s 条任务",
					worker.id,
					assigned_count,
				)
		except SQLAlchemyError:
			db.rollback()
			logger.exception("任务调度数据库操作失败，已回滚")
		except Exception:
			db.rollback()
			logger.exception("任务调度执行异常")
		finally:
			db.close()


task_scheduler_service = TaskSchedulerService()


def start_task_scheduler() -> None:
	task_scheduler_service.start()


def stop_task_scheduler() -> None:
	task_scheduler_service.stop()
