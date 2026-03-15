from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


engine = create_engine(
	settings.SQLALCHEMY_DATABASE_URI,
	pool_pre_ping=True,
)

SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine,
	class_=Session,
)


def get_db() -> Generator[Session, None, None]:
	"""FastAPI 依赖注入使用的数据库会话生成器。"""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
