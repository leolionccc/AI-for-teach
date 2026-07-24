from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChapterCreateRequest(BaseModel):
    title: str = Field(..., max_length=200, description="章节标题")
    description: Optional[str] = Field(None, description="章节说明")
    sort_order: int = Field(0, description="排序")


class ChapterUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200, description="章节标题")
    description: Optional[str] = Field(None, description="章节说明")
    sort_order: Optional[int] = Field(None, description="排序")


class ChapterResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    sort_order: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExamConfigCreateRequest(BaseModel):
    chapter_id: int = Field(..., description="章节ID")
    knowledge_points: str = Field(..., description="知识点")
    choice_count: int = Field(2, ge=0, le=50, description="选择题数量")
    judge_count: int = Field(2, ge=0, le=50, description="判断题数量")
    short_answer_count: int = Field(2, ge=0, le=50, description="简答题数量")
    total_score: float = Field(100.0, ge=1, description="总分")
    evaluation_dimensions: Optional[str] = Field(
        "知识掌握情况、基础概念掌握、综合分析能力、建议复习知识点",
        description="评价维度",
    )


class ExamConfigUpdateRequest(BaseModel):
    knowledge_points: Optional[str] = Field(None, description="知识点")
    choice_count: Optional[int] = Field(None, ge=0, le=50, description="选择题数量")
    judge_count: Optional[int] = Field(None, ge=0, le=50, description="判断题数量")
    short_answer_count: Optional[int] = Field(None, ge=0, le=50, description="简答题数量")
    total_score: Optional[float] = Field(None, ge=1, description="总分")
    evaluation_dimensions: Optional[str] = Field(None, description="评价维度")


class ExamConfigResponse(BaseModel):
    id: int
    chapter_id: int
    knowledge_points: str
    choice_count: int
    judge_count: int
    short_answer_count: int
    total_score: float
    evaluation_dimensions: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExamStartRequest(BaseModel):
    """
    开始考试请求
    """

    chapter_id: int = Field(..., description="章节ID")
    config_id: Optional[int] = Field(None, description="考核配置ID，不传则使用该章节最新配置")


class ExamRecordResponse(BaseModel):
    """
    考试记录响应
    """

    id: int
    user_id: int
    chapter_id: int
    config_id: int
    status: str
    total_score: float
    report: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExamQuestionResponse(BaseModel):
    """
    给学生展示的题目响应
    不返回 standard_answer 和 analysis
    """

    id: int
    exam_id: int
    question_type: str
    question_text: str
    options: Optional[List[str]] = None
    score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExamAnswerSubmitRequest(BaseModel):
    """
    提交单题答案请求
    """

    question_id: int = Field(..., description="题目ID")
    answer_text: str = Field(..., description="学生答案")


class ExamAnswerResponse(BaseModel):
    """
    答案响应
    """

    id: int
    exam_id: int
    question_id: int
    user_id: int
    answer_text: str
    score: float
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExamQuestionWithAnswerResponse(BaseModel):
    """
    考试报告详情：
    题目 + 标准答案 + 学生答案 + 得分 + 反馈
    """

    question_id: int
    question_type: str
    question_text: str
    options: Optional[List[str]] = None
    standard_answer: str
    analysis: Optional[str] = None
    question_score: float
    student_answer: Optional[str] = None
    student_score: float = 0.0
    feedback: Optional[str] = None


class ExamReportResponse(BaseModel):
    """
    考试报告响应
    """

    exam: ExamRecordResponse
    answers: List[ExamQuestionWithAnswerResponse]
