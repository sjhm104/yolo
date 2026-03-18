from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Numeric, String, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship


Base = declarative_base()


class UserRole(str, enum.Enum):
	ADMIN = "admin"
	CLEANER = "cleaner"


class DroneStatus(str, enum.Enum):
	IDLE = "idle"
	FLYING = "flying"
	OFFLINE = "offline"


class CleaningTaskStatus(str, enum.Enum):
	PENDING = "pending"
	ASSIGNED = "assigned"
	COMPLETED = "completed"


def enum_values(enum_cls: type[enum.Enum]) -> list[str]:
	return [item.value for item in enum_cls]


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(
		INTEGER(unsigned=True),
		primary_key=True,
		autoincrement=True,
		comment="用户主键ID，系统内用户的唯一标识，自增生成，供其他业务表进行关联引用",
	)
	username: Mapped[str] = mapped_column(
		String(50),
		nullable=False,
		unique=True,
		index=True,
		comment="用户登录账号，要求全局唯一，用于身份认证与后台登录",
	)
	password_hash: Mapped[str] = mapped_column(
		String(255),
		nullable=False,
		comment="用户密码哈希值，存储加密后的密码摘要，不保存明文密码，保障账户安全",
	)
	real_name: Mapped[str] = mapped_column(
		String(50),
		nullable=False,
		comment="用户真实姓名，用于任务分配、人员管理与报表展示",
	)
	role: Mapped[UserRole] = mapped_column(
		Enum(UserRole, name="users_role_enum", values_callable=enum_values),
		nullable=False,
		default=UserRole.CLEANER,
		index=True,
		comment="用户角色类型：admin表示系统管理员，cleaner表示环卫执行人员，默认cleaner",
	)
	phone: Mapped[Optional[str]] = mapped_column(
		String(20),
		nullable=True,
		comment="用户联系电话，便于紧急联络、任务通知与现场沟通",
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
		comment="记录创建时间，表示该用户数据首次写入数据库的时间戳",
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
		server_onupdate=text("CURRENT_TIMESTAMP"),
		comment="记录更新时间，表示该用户数据最近一次被修改的时间戳",
	)

	cleaning_tasks: Mapped[List[CleaningTask]] = relationship(
		"CleaningTask",
		back_populates="cleaner",
	)


class Drone(Base):
	__tablename__ = "drones"

	id: Mapped[int] = mapped_column(
		INTEGER(unsigned=True),
		primary_key=True,
		autoincrement=True,
		comment="无人机主键ID，系统内无人机设备的唯一标识，自增生成",
	)
	drone_code: Mapped[str] = mapped_column(
		String(50),
		nullable=False,
		unique=True,
		comment="无人机唯一编号，对应设备铭牌编号或系统编码，用于设备唯一识别",
	)
	status: Mapped[DroneStatus] = mapped_column(
		Enum(DroneStatus, name="drones_status_enum", values_callable=enum_values),
		nullable=False,
		default=DroneStatus.OFFLINE,
		comment="无人机运行状态：idle空闲待命，flying飞行作业中，offline离线不可用，默认offline",
	)
	current_lat: Mapped[Optional[Decimal]] = mapped_column(
		Numeric(10, 7),
		nullable=True,
		comment="无人机当前纬度坐标，单位为度，采用WGS84坐标系，允许为空表示暂未上报",
	)
	current_lng: Mapped[Optional[Decimal]] = mapped_column(
		Numeric(10, 7),
		nullable=True,
		comment="无人机当前经度坐标，单位为度，采用WGS84坐标系，允许为空表示暂未上报",
	)
	last_active_time: Mapped[Optional[datetime]] = mapped_column(
		DateTime,
		nullable=True,
		comment="无人机最后活跃时间，表示设备最近一次心跳或数据上传时间",
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
		comment="记录创建时间，表示该无人机设备信息首次入库时间",
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
		server_onupdate=text("CURRENT_TIMESTAMP"),
		comment="记录更新时间，表示该无人机设备信息最近一次更新的时间戳",
	)

	detection_records: Mapped[List[DetectionRecord]] = relationship(
		"DetectionRecord",
		back_populates="drone",
	)


class DetectionRecord(Base):
	__tablename__ = "detection_records"

	id: Mapped[int] = mapped_column(
		INTEGER(unsigned=True),
		primary_key=True,
		autoincrement=True,
		comment="检测记录主键ID，系统每次图像识别结果的唯一标识，自增生成",
	)
	drone_id: Mapped[Optional[int]] = mapped_column(
		INTEGER(unsigned=True),
		ForeignKey("drones.id", ondelete="SET NULL", onupdate="CASCADE"),
		nullable=True,
		index=True,
		comment="拍摄无人机ID，外键关联drones.id，允许为空以兼容设备记录被删除后的历史数据保留",
	)
	image_url: Mapped[str] = mapped_column(
		String(255),
		nullable=False,
		comment="无人机回传图像的相对路径或资源地址，用于结果回显与后续复核",
	)
	latitude: Mapped[Decimal] = mapped_column(
		Numeric(10, 7),
		nullable=False,
		comment="拍摄点纬度坐标，单位为度，采用WGS84坐标系",
	)
	longitude: Mapped[Decimal] = mapped_column(
		Numeric(10, 7),
		nullable=False,
		comment="拍摄点经度坐标，单位为度，采用WGS84坐标系",
	)
	has_waste: Mapped[bool] = mapped_column(
		Boolean,
		nullable=False,
		default=False,
		index=True,
		comment="是否检测出垃圾，TRUE表示检测到垃圾目标，FALSE表示未检测到",
	)
	confidence: Mapped[Optional[float]] = mapped_column(
		Float,
		nullable=True,
		comment="AI识别置信度，取值通常在0到1之间，例如0.95表示95%的识别置信水平",
	)
	detected_time: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
		comment="检测识别时间，表示算法完成当前记录识别的业务时间点",
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
		comment="记录创建时间，表示该检测记录写入数据库的时间戳",
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
		server_onupdate=text("CURRENT_TIMESTAMP"),
		comment="记录更新时间，表示该检测记录最近一次被修订的时间戳",
	)

	drone: Mapped[Optional[Drone]] = relationship(
		"Drone",
		back_populates="detection_records",
	)
	cleaning_task: Mapped[Optional[CleaningTask]] = relationship(
		"CleaningTask",
		back_populates="record",
		uselist=False,
	)


class CleaningTask(Base):
	__tablename__ = "cleaning_tasks"

	id: Mapped[int] = mapped_column(
		INTEGER(unsigned=True),
		primary_key=True,
		autoincrement=True,
		comment="清理任务主键ID，系统内每条清理任务的唯一标识，自增生成",
	)
	record_id: Mapped[int] = mapped_column(
		INTEGER(unsigned=True),
		ForeignKey("detection_records.id", ondelete="CASCADE", onupdate="CASCADE"),
		nullable=False,
		index=True,
		comment="关联检测记录ID，外键关联detection_records.id，标识该任务来源于哪条检测结果",
	)
	cleaner_id: Mapped[Optional[int]] = mapped_column(
		INTEGER(unsigned=True),
		ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"),
		nullable=True,
		index=True,
		comment="分配的环卫人员ID，外键关联users.id，允许为空表示任务尚未分配具体执行人",
	)
	status: Mapped[CleaningTaskStatus] = mapped_column(
		Enum(
			CleaningTaskStatus,
			name="cleaning_tasks_status_enum",
			values_callable=enum_values,
		),
		nullable=False,
		default=CleaningTaskStatus.PENDING,
		index=True,
		comment="任务状态：pending待处理，assigned已分配，completed已完成，默认pending",
	)
	assigned_time: Mapped[Optional[datetime]] = mapped_column(
		DateTime,
		nullable=True,
		comment="任务分配时间，记录任务指派给环卫人员的业务时间点",
	)
	completed_time: Mapped[Optional[datetime]] = mapped_column(
		DateTime,
		nullable=True,
		comment="任务完成时间，记录现场清理完成并回传确认的业务时间点",
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
		comment="记录创建时间，表示该清理任务首次生成入库的时间戳",
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		server_default=text("CURRENT_TIMESTAMP"),
		server_onupdate=text("CURRENT_TIMESTAMP"),
		comment="记录更新时间，表示该清理任务最近一次状态或信息变更时间戳",
	)

	record: Mapped[DetectionRecord] = relationship(
		"DetectionRecord",
		back_populates="cleaning_task",
	)
	cleaner: Mapped[Optional[User]] = relationship(
		"User",
		back_populates="cleaning_tasks",
	)
