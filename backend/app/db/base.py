from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship


Base = declarative_base()


class CleaningTaskStatus(str, enum.Enum):
	PENDING = "pending"
	COMPLETED = "completed"


def enum_values(enum_cls: type[enum.Enum]) -> list[str]:
	return [item.value for item in enum_cls]


class Worker(Base):
	__tablename__ = "workers"

	id: Mapped[int] = mapped_column(
		INTEGER(unsigned=True),
		primary_key=True,
		autoincrement=True,
	)
	name: Mapped[str] = mapped_column(
		String(50),
		nullable=False,
	)
	phone: Mapped[str] = mapped_column(
		String(20),
		nullable=False,
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
	)

	cleaning_tasks: Mapped[List[CleaningTask]] = relationship(
		"CleaningTask",
		back_populates="worker",
	)


class DetectionRecord(Base):
	__tablename__ = "detection_records"

	id: Mapped[int] = mapped_column(
		INTEGER(unsigned=True),
		primary_key=True,
		autoincrement=True,
	)
	video_source: Mapped[str] = mapped_column(
		String(100),
		nullable=False,
	)
	frame_time: Mapped[str] = mapped_column(
		String(20),
		nullable=False,
	)
	screenshot_url: Mapped[str] = mapped_column(
		String(255),
		nullable=False,
	)
	has_waste: Mapped[bool] = mapped_column(
		Boolean,
		nullable=False,
		default=False,
		server_default=text("0"),
	)
	confidence: Mapped[float] = mapped_column(
		Float,
		nullable=False,
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
	)

	cleaning_tasks: Mapped[List[CleaningTask]] = relationship(
		"CleaningTask",
		back_populates="record",
		cascade="all, delete-orphan",
	)


class CleaningTask(Base):
	__tablename__ = "cleaning_tasks"

	id: Mapped[int] = mapped_column(
		INTEGER(unsigned=True),
		primary_key=True,
		autoincrement=True,
	)
	record_id: Mapped[int] = mapped_column(
		INTEGER(unsigned=True),
		ForeignKey("detection_records.id", ondelete="CASCADE", onupdate="CASCADE"),
		nullable=False,
		index=True,
	)
	worker_id: Mapped[Optional[int]] = mapped_column(
		INTEGER(unsigned=True),
		ForeignKey("workers.id", ondelete="SET NULL", onupdate="CASCADE"),
		nullable=True,
		index=True,
	)
	status: Mapped[CleaningTaskStatus] = mapped_column(
		Enum(
			CleaningTaskStatus,
			name="cleaning_tasks_status_enum",
			values_callable=enum_values,
		),
		nullable=False,
		default=CleaningTaskStatus.PENDING,
		server_default=text("'pending'"),
		index=True,
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
	)
	completed_at: Mapped[Optional[datetime]] = mapped_column(
		DateTime,
		nullable=True,
	)

	record: Mapped[DetectionRecord] = relationship(
		"DetectionRecord",
		back_populates="cleaning_tasks",
	)
	worker: Mapped[Optional[Worker]] = relationship(
		"Worker",
		back_populates="cleaning_tasks",
	)
