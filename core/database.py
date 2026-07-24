import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """
    SQLAlchemy 所有模型的基类
    """
    pass


# 确保 data 目录存在
os.makedirs("data", exist_ok=True)


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {},
    echo=False,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    获取数据库会话
    FastAPI 依赖注入使用
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库表
    第一阶段暂时没有业务表，后续用户表、资料表、考试表都会在这里统一创建
    """

    # 导入所有模型，确保 SQLAlchemy 可以识别
    # 后续新增模型后，在 app/models/__init__.py 中统一导入即可
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)