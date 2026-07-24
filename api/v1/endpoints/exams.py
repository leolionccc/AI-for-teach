from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.users import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.exam import (
    ChapterCreateRequest,
    ChapterResponse,
    ChapterUpdateRequest,
    ExamAnswerResponse,
    ExamAnswerSubmitRequest,
    ExamConfigCreateRequest,
    ExamConfigResponse,
    ExamConfigUpdateRequest,
    ExamRecordResponse,
    ExamStartRequest,
    ExamReportResponse,

)
from app.schemas.response import ApiResponse
from app.services.exam_config_service import (
    create_chapter,
    create_exam_config,
    delete_chapter,
    delete_exam_config,
    get_chapter_by_id,
    get_exam_config_by_id,
    list_chapters,
    list_exam_configs,
    update_chapter,
    update_exam_config,
)
from app.services.exam_runtime_service import (
    get_exam_record,
    list_exam_questions,
    list_exam_records,
    question_to_response_dict,
    start_exam,
    submit_answer,
    submit_exam,
    build_exam_report_detail,
)


router = APIRouter()


# =========================================================
# 章节接口
# =========================================================

@router.get("/chapters", response_model=ApiResponse)
def get_chapters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chapters = list_chapters(db)

    return ApiResponse(
        code=200,
        message="success",
        data=[ChapterResponse.model_validate(item) for item in chapters],
    )


@router.post("/chapters", response_model=ApiResponse)
def add_chapter(
    request: ChapterCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chapter = create_chapter(
        db=db,
        request=request,
        user_id=current_user.id,
    )

    return ApiResponse(
        code=200,
        message="创建成功",
        data=ChapterResponse.model_validate(chapter),
    )


@router.put("/chapters/{chapter_id}", response_model=ApiResponse)
def edit_chapter(
    chapter_id: int,
    request: ChapterUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chapter = get_chapter_by_id(db, chapter_id)

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在",
        )

    chapter = update_chapter(
        db=db,
        chapter=chapter,
        request=request,
    )

    return ApiResponse(
        code=200,
        message="修改成功",
        data=ChapterResponse.model_validate(chapter),
    )


@router.delete("/chapters/{chapter_id}", response_model=ApiResponse)
def remove_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chapter = get_chapter_by_id(db, chapter_id)

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在",
        )

    delete_chapter(db, chapter)

    return ApiResponse(
        code=200,
        message="删除成功",
        data=None,
    )


# =========================================================
# 考核配置接口
# =========================================================

@router.get("/configs", response_model=ApiResponse)
def get_configs(
    chapter_id: Optional[int] = Query(None, description="章节ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    configs = list_exam_configs(
        db=db,
        chapter_id=chapter_id,
    )

    return ApiResponse(
        code=200,
        message="success",
        data=[ExamConfigResponse.model_validate(item) for item in configs],
    )


@router.post("/configs", response_model=ApiResponse)
def add_config(
    request: ExamConfigCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chapter = get_chapter_by_id(db, request.chapter_id)

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="章节不存在",
        )

    total_count = (
        request.choice_count
        + request.judge_count
        + request.short_answer_count
    )

    if total_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="题目总数必须大于0",
        )

    config = create_exam_config(
        db=db,
        request=request,
        user_id=current_user.id,
    )

    return ApiResponse(
        code=200,
        message="创建成功",
        data=ExamConfigResponse.model_validate(config),
    )


@router.put("/configs/{config_id}", response_model=ApiResponse)
def edit_config(
    config_id: int,
    request: ExamConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    config = get_exam_config_by_id(db, config_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考核配置不存在",
        )

    config = update_exam_config(
        db=db,
        config=config,
        request=request,
    )

    return ApiResponse(
        code=200,
        message="修改成功",
        data=ExamConfigResponse.model_validate(config),
    )


@router.delete("/configs/{config_id}", response_model=ApiResponse)
def remove_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    config = get_exam_config_by_id(db, config_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考核配置不存在",
        )

    delete_exam_config(db, config)

    return ApiResponse(
        code=200,
        message="删除成功",
        data=None,
    )


# =========================================================
# 考试运行接口
# =========================================================

@router.post("/start", response_model=ApiResponse)
async def start_chapter_exam(
    request: ExamStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    开始章节考试，自动生成题目。
    """
    try:
        exam = await start_exam(
            db=db,
            user_id=current_user.id,
            chapter_id=request.chapter_id,
            config_id=request.config_id,
        )

        return ApiResponse(
            code=200,
            message="考试已开始",
            data=ExamRecordResponse.model_validate(exam),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/records", response_model=ApiResponse)
def get_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查询当前用户考试记录
    """
    records = list_exam_records(
        db=db,
        user_id=current_user.id,
    )

    return ApiResponse(
        code=200,
        message="success",
        data=[ExamRecordResponse.model_validate(item) for item in records],
    )


@router.get("/{exam_id}/questions", response_model=ApiResponse)
def get_questions(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查询考试题目
    """
    exam = get_exam_record(
        db=db,
        exam_id=exam_id,
        user_id=current_user.id,
    )

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试记录不存在",
        )

    questions = list_exam_questions(
        db=db,
        exam_id=exam.id,
    )

    return ApiResponse(
        code=200,
        message="success",
        data=[question_to_response_dict(item) for item in questions],
    )


@router.post("/{exam_id}/answer", response_model=ApiResponse)
def answer_question(
    exam_id: int,
    request: ExamAnswerSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    提交单题答案
    """
    exam = get_exam_record(
        db=db,
        exam_id=exam_id,
        user_id=current_user.id,
    )

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试记录不存在",
        )

    if exam.status == "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="考试已提交，不能继续答题",
        )

    try:
        answer = submit_answer(
            db=db,
            exam=exam,
            question_id=request.question_id,
            user_id=current_user.id,
            answer_text=request.answer_text,
        )

        return ApiResponse(
            code=200,
            message="提交成功",
            data=ExamAnswerResponse.model_validate(answer),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{exam_id}/submit", response_model=ApiResponse)
async def finish_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    提交考试并生成学习评价报告
    """
    exam = get_exam_record(
        db=db,
        exam_id=exam_id,
        user_id=current_user.id,
    )

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试记录不存在",
        )

    if exam.status == "submitted":
        return ApiResponse(
            code=200,
            message="考试已提交",
            data=ExamRecordResponse.model_validate(exam),
        )

    exam = await submit_exam(
        db=db,
        exam=exam,
    )

    return ApiResponse(
        code=200,
        message="考试提交成功，学习报告已生成",
        data=ExamRecordResponse.model_validate(exam),
    )


@router.get("/{exam_id}/report", response_model=ApiResponse)
def get_report(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查询考试学习评价报告。

    返回：
    1. 考试记录
    2. 学习评价报告 Markdown
    3. 每道题的作答详情
    """
    exam = get_exam_record(
        db=db,
        exam_id=exam_id,
        user_id=current_user.id,
    )

    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考试记录不存在",
        )

    answer_details = build_exam_report_detail(
        db=db,
        exam=exam,
    )

    report_data = ExamReportResponse(
        exam=ExamRecordResponse.model_validate(exam),
        answers=answer_details,
    )

    return ApiResponse(
        code=200,
        message="success",
        data=report_data,
    )