from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class Material(Base, TimestampMixin):
    """
    课程资料表
    """

    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="资料ID",
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="原始文件名",
    )

    stored_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="服务器存储文件名",
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="文件保存路径",
    )

    file_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="文件类型：pdf/docx/pptx",
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="文件大小，单位byte",
    )

    content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="解析后的文本内容",
    )

    parse_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="success",
        comment="解析状态：success/fail/skipped",
    )

    parse_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="解析失败原因",
    )

    created_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="上传用户ID",
    )