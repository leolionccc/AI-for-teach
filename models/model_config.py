from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class ModelConfig(Base, TimestampMixin):
    """
    大模型配置表
    """

    __tablename__ = "model_configs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="配置ID",
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="配置名称",
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="模型供应商：openai/qwen/deepseek/custom",
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="模型名称",
    )

    api_base_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="API基础地址",
    )

    api_key: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="API Key",
    )

    temperature: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="0.7",
        comment="温度参数",
    )

    max_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2048,
        comment="最大输出Token数",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="是否为当前启用配置",
    )

    remark: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="备注",
    )

    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="创建人ID",
    )