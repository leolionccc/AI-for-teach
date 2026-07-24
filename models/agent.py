from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class Agent(Base, TimestampMixin):
    """
    智能体配置表
    """

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="智能体ID",
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="智能体名称",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="智能体介绍",
    )

    system_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="系统提示词",
    )

    welcome_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="欢迎语",
    )

    avatar: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="头像地址",
    )

    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否启用",
    )

    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="创建人ID",
    )
