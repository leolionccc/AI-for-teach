from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.exam import Chapter, ExamConfig
from app.schemas.exam import (
    ChapterCreateRequest,
    ChapterUpdateRequest,
    ExamConfigCreateRequest,
    ExamConfigUpdateRequest,
)


# =========================================================
# 章节管理
# =========================================================

def list_chapters(db: Session) -> List[Chapter]:
    """
    查询章节列表
    """
    return (
        db.query(Chapter)
        .order_by(Chapter.sort_order.asc(), Chapter.id.asc())
        .all()
    )


def get_chapter_by_id(
    db: Session,
    chapter_id: int,
) -> Optional[Chapter]:
    """
    根据ID查询章节
    """
    return db.query(Chapter).filter(Chapter.id == chapter_id).first()


def create_chapter(
    db: Session,
    request: ChapterCreateRequest,
    user_id: int,
) -> Chapter:
    """
    创建章节
    """
    chapter = Chapter(
        title=request.title,
        description=request.description,
        sort_order=request.sort_order,
        created_by=user_id,
    )

    db.add(chapter)
    db.commit()
    db.refresh(chapter)

    return chapter


def update_chapter(
    db: Session,
    chapter: Chapter,
    request: ChapterUpdateRequest,
) -> Chapter:
    """
    修改章节
    """
    update_data = request.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(chapter, key, value)

    db.commit()
    db.refresh(chapter)

    return chapter


def delete_chapter(
    db: Session,
    chapter: Chapter,
) -> None:
    """
    删除章节

    注意：
    当前阶段先只删除章节本身。
    如果该章节已经有考核配置，建议前端先提示用户。
    后续也可以改成级联删除。
    """
    db.delete(chapter)
    db.commit()


# =========================================================
# 考核配置管理
# =========================================================

def list_exam_configs(
    db: Session,
    chapter_id: Optional[int] = None,
) -> List[ExamConfig]:
    """
    查询考核配置列表
    """
    query = db.query(ExamConfig)

    if chapter_id is not None:
        query = query.filter(ExamConfig.chapter_id == chapter_id)

    return query.order_by(ExamConfig.id.desc()).all()


def get_exam_config_by_id(
    db: Session,
    config_id: int,
) -> Optional[ExamConfig]:
    """
    根据ID查询考核配置
    """
    return db.query(ExamConfig).filter(ExamConfig.id == config_id).first()


def get_latest_exam_config_by_chapter(
    db: Session,
    chapter_id: int,
) -> Optional[ExamConfig]:
    """
    查询某章节最新考核配置

    后续开始考试时可以默认使用该章节最新配置。
    """
    return (
        db.query(ExamConfig)
        .filter(ExamConfig.chapter_id == chapter_id)
        .order_by(ExamConfig.id.desc())
        .first()
    )


def create_exam_config(
    db: Session,
    request: ExamConfigCreateRequest,
    user_id: int,
) -> ExamConfig:
    """
    创建章节考核配置
    """
    config = ExamConfig(
        chapter_id=request.chapter_id,
        knowledge_points=request.knowledge_points,
        choice_count=request.choice_count,
        judge_count=request.judge_count,
        short_answer_count=request.short_answer_count,
        total_score=request.total_score,
        evaluation_dimensions=request.evaluation_dimensions,
        created_by=user_id,
    )

    db.add(config)
    db.commit()
    db.refresh(config)

    return config


def update_exam_config(
    db: Session,
    config: ExamConfig,
    request: ExamConfigUpdateRequest,
) -> ExamConfig:
    """
    修改章节考核配置
    """
    update_data = request.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(config, key, value)

    db.commit()
    db.refresh(config)

    return config


def delete_exam_config(
    db: Session,
    config: ExamConfig,
) -> None:
    """
    删除考核配置
    """
    db.delete(config)
    db.commit()