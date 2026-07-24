from typing import Optional

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class Chapter(Base, TimestampMixin):
    """
    课程章节表
    """

    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="章节ID",
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="章节标题",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="章节说明",
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="排序",
    )

    created_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="创建人ID",
    )


class ExamConfig(Base, TimestampMixin):
    """
    章节考核配置表
    """

    __tablename__ = "exam_configs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="考核配置ID",
    )

    chapter_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="章节ID",
    )

    knowledge_points: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="知识点，逗号或换行分隔",
    )

    choice_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
        comment="选择题数量",
    )

    judge_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
        comment="判断题数量",
    )

    short_answer_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
        comment="简答题数量",
    )

    total_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=100.0,
        comment="总分",
    )

    evaluation_dimensions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="评价维度",
    )

    created_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="创建人ID",
    )


class ExamRecord(Base, TimestampMixin):
    """
    学生考试记录表
    """

    __tablename__ = "exam_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="考试记录ID",
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="学生ID",
    )

    chapter_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="章节ID",
    )

    config_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="考核配置ID",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="in_progress",
        comment="状态：in_progress/submitted",
    )

    total_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="当前得分",
    )

    report: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="学习评价报告，下一阶段使用",
    )


class ExamQuestion(Base, TimestampMixin):
    """
    考试题目表
    """

    __tablename__ = "exam_questions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="题目ID",
    )

    exam_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="考试记录ID",
    )

    question_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="题型：choice/judge/short_answer",
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="题干",
    )

    options: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="选项JSON字符串",
    )

    standard_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="标准答案",
    )

    analysis: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="题目解析",
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="题目分值",
    )


class ExamAnswer(Base, TimestampMixin):
    """
    学生答案表
    """

    __tablename__ = "exam_answers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="答案ID",
    )

    exam_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="考试记录ID",
    )

    question_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="题目ID",
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="学生ID",
    )

    answer_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="学生答案",
    )

    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="该题得分",
    )

    feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="判分反馈",
    )