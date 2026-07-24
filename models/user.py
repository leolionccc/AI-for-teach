from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class User(Base, TimestampMixin):
    """
    用户表
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="用户ID",
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        comment="用户名",
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="加密后的密码",
    )

    nickname: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        comment="昵称",
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="student",
        comment="角色：student/teacher/admin",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否启用",
    )