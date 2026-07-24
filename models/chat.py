from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class ChatSession(Base, TimestampMixin):
    """
    对话会话表
    """

    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="会话ID",
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="用户ID",
    )

    agent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="智能体ID",
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        default="新的对话",
        comment="会话标题",
    )


class ChatMessage(Base, TimestampMixin):
    """
    对话消息表
    """

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="消息ID",
    )

    session_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="会话ID",
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="用户ID",
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="角色：user/assistant/system",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="消息内容",
    )

    model_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="使用的模型名称",
    )

    token_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Token数量",
    )