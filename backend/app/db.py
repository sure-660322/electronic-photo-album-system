"""SQLAlchemy 引擎与会话工厂。表结构由 docker/postgres/02-schema.sql 创建，
应用侧只维护与之一致的 ORM 模型（models.py），不自动建表。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
