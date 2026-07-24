from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class SystemLog(Base, TimestampMixin):
    """
    系统日志表
    """

    __tablename__ = "system_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="日志ID",
    )

    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="操作用户ID",
    )

    username: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="用户名",
    )

    module: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="模块名称",
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="操作动作",
    )

    method: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="请求方法",
    )

    path: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="请求路径",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="success",
        comment="状态：success/fail",
    )

    message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="日志信息",
    )