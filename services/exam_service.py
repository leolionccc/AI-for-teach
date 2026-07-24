import json
import re
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.exam import (
    Chapter,
    ExamAnswer,
    ExamConfig,
    ExamQuestion,
    ExamRecord,
)
from app.models.model_config import ModelConfig
from app.schemas.exam import (
    ChapterCreateRequest,
    ChapterUpdateRequest,
    ExamConfigCreateRequest,
    ExamConfigUpdateRequest,
)
from app.services.llm_service import chat_completion_once


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


def get_chapter_by_id(db: Session, chapter_id: int) -> Optional[Chapter]:
    """
    根据章节ID查询章节
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


def delete_chapter(db: Session, chapter: Chapter) -> None:
    """
    删除章节
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
    根据配置ID查询考核配置
    """
    return db.query(ExamConfig).filter(ExamConfig.id == config_id).first()


def get_latest_exam_config_by_chapter(
    db: Session,
    chapter_id: int,
) -> Optional[ExamConfig]:
    """
    查询某章节最新考核配置
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


# =========================================================
# 大模型配置
# =========================================================

def get_active_model_config(db: Session) -> Optional[ModelConfig]:
    """
    获取当前启用的大模型配置
    """
    return (
        db.query(ModelConfig)
        .filter(ModelConfig.is_active == True)
        .first()
    )


# =========================================================
# 题目生成相关工具
# =========================================================

def extract_json_array(text: str) -> List[Dict]:
    """
    从大模型输出中提取 JSON 数组。

    兼容：
    1. 纯 JSON 数组
    2. ```json ... ```
    3. 前后带说明文字的 JSON
    """
    if not text:
        return []

    raw = text.strip()

    raw = raw.replace("```json", "")
    raw = raw.replace("```", "")
    raw = raw.strip()

    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except Exception:
        pass

    match = re.search(r"\[[\s\S]*\]", raw)

    if not match:
        return []

    try:
        data = json.loads(match.group(0))
        if isinstance(data, list):
            return data
    except Exception:
        return []

    return []


def build_fallback_questions(
    config: ExamConfig,
    chapter: Chapter,
) -> List[Dict]:
    """
    兜底题目生成。

    当未配置大模型，或大模型调用失败、返回格式错误时，
    系统仍然可以生成题目，保证演示流程完整。
    """
    questions: List[Dict] = []

    for _ in range(config.choice_count):
        questions.append(
            {
                "question_type": "choice",
                "question_text": f"关于“{chapter.title}”的学习内容，下列说法较为合理的是？",
                "options": [
                    "A. 只关注单一要素，忽略整体联系",
                    "B. 强调整体性、关联性和协同性",
                    "C. 完全不需要分析系统内部关系",
                    "D. 只关注短期结果，不关注长期影响",
                ],
                "standard_answer": "B",
                "analysis": "系统方法论通常强调整体性、关联性和协同性。",
            }
        )

    for _ in range(config.judge_count):
        questions.append(
            {
                "question_type": "judge",
                "question_text": f"判断：学习“{chapter.title}”时，应关注不同要素之间的相互关系。",
                "options": ["正确", "错误"],
                "standard_answer": "正确",
                "analysis": "系统方法论强调要素之间的联系和协同。",
            }
        )

    for _ in range(config.short_answer_count):
        questions.append(
            {
                "question_type": "short_answer",
                "question_text": f"请结合本章知识点，简述“{chapter.title}”体现的系统思维。",
                "options": [],
                "standard_answer": "应从整体性、关联性、协同性、统筹谋划等角度回答，并结合具体知识点说明。",
                "analysis": "简答题重点考查学生对章节知识的理解和综合表达能力。",
            }
        )

    return questions


def normalize_generated_questions(
    questions: List[Dict],
    config: ExamConfig,
    chapter: Chapter,
) -> List[Dict]:
    """
    规范化大模型生成的题目。

    作用：
    1. 修正非法题型
    2. 补齐缺失字段
    3. 防止选项为空
    4. 保证题目数量符合配置
    """
    normalized: List[Dict] = []

    allowed_types = {"choice", "judge", "short_answer"}

    for item in questions:
        if not isinstance(item, dict):
            continue

        question_type = item.get("question_type", "short_answer")

        if question_type not in allowed_types:
            question_type = "short_answer"

        question_text = item.get("question_text") or f"请简述“{chapter.title}”的相关知识点。"
        options = item.get("options", [])
        standard_answer = item.get("standard_answer") or "参考课程资料作答。"
        analysis = item.get("analysis") or "请结合课程知识点进行分析。"

        if question_type == "choice":
            if not isinstance(options, list) or len(options) < 4:
                options = [
                    "A. 只关注局部",
                    "B. 关注整体与协同",
                    "C. 忽略系统结构",
                    "D. 不考虑发展目标",
                ]

            if not standard_answer:
                standard_answer = "B"

        elif question_type == "judge":
            options = ["正确", "错误"]

            if standard_answer not in ["正确", "错误"]:
                standard_answer = "正确"

        else:
            options = []

        normalized.append(
            {
                "question_type": question_type,
                "question_text": question_text,
                "options": options,
                "standard_answer": standard_answer,
                "analysis": analysis,
            }
        )

    expected_count = (
        config.choice_count
        + config.judge_count
        + config.short_answer_count
    )

    if len(normalized) < expected_count:
        fallback = build_fallback_questions(config, chapter)
        normalized.extend(fallback[len(normalized):expected_count])

    return normalized[:expected_count]


async def generate_questions_with_llm(
    db: Session,
    chapter: Chapter,
    config: ExamConfig,
) -> List[Dict]:
    """
    调用大模型生成章节考核题目。
    """
    model_config = get_active_model_config(db)

    if not model_config:
        return build_fallback_questions(config, chapter)

    total_count = (
        config.choice_count
        + config.judge_count
        + config.short_answer_count
    )

    prompt = (
        "你是课程章节考核出题助手。\n"
        "请根据以下章节和知识点生成考核题目。\n\n"
        f"章节名称：{chapter.title}\n"
        f"章节说明：{chapter.description or ''}\n"
        f"知识点：{config.knowledge_points}\n\n"
        "题型要求：\n"
        f"选择题数量：{config.choice_count}\n"
        f"判断题数量：{config.judge_count}\n"
        f"简答题数量：{config.short_answer_count}\n"
        f"总题数：{total_count}\n\n"
        "输出要求：\n"
        "1. 只返回 JSON 数组，不要返回 Markdown，不要返回解释文字。\n"
        "2. 每个题目对象必须包含 question_type、question_text、options、standard_answer、analysis。\n"
        "3. question_type 只能是 choice、judge、short_answer。\n"
        "4. 选择题 options 必须包含 A/B/C/D 四个选项。\n"
        "5. 判断题 options 固定为 [\"正确\", \"错误\"]。\n"
        "6. 简答题 options 为空数组。\n\n"
        "示例格式：\n"
        "[\n"
        "  {\n"
        "    \"question_type\": \"choice\",\n"
        "    \"question_text\": \"题干内容\",\n"
        "    \"options\": [\"A. 选项A\", \"B. 选项B\", \"C. 选项C\", \"D. 选项D\"],\n"
        "    \"standard_answer\": \"B\",\n"
        "    \"analysis\": \"解析内容\"\n"
        "  }\n"
        "]"
    )

    try:
        content = await chat_completion_once(
            model_config=model_config,
            messages=[
                {
                    "role": "system",
                    "content": "你是严格输出 JSON 的考试题目生成助手。",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        questions = extract_json_array(content)

        if not questions:
            return build_fallback_questions(config, chapter)

        return normalize_generated_questions(questions, config, chapter)

    except Exception:
        return build_fallback_questions(config, chapter)


def calculate_question_score(config: ExamConfig) -> float:
    """
    根据总分和总题数计算每题分值
    """
    total_count = (
        config.choice_count
        + config.judge_count
        + config.short_answer_count
    )

    if total_count <= 0:
        return 0.0

    return round(config.total_score / total_count, 2)


# =========================================================
# 考试流程
# =========================================================

async def start_exam(
    db: Session,
    user_id: int,
    chapter_id: int,
    config_id: Optional[int] = None,
) -> ExamRecord:
    """
    开始章节考试。

    流程：
    1. 查询章节
    2. 查询考核配置
    3. 创建考试记录
    4. 调用大模型生成题目
    5. 保存题目
    """
    chapter = get_chapter_by_id(db, chapter_id)

    if not chapter:
        raise ValueError("章节不存在")

    if config_id:
        config = get_exam_config_by_id(db, config_id)
    else:
        config = get_latest_exam_config_by_chapter(db, chapter_id)

    if not config:
        raise ValueError("该章节暂无考核配置")

    exam = ExamRecord(
        user_id=user_id,
        chapter_id=chapter_id,
        config_id=config.id,
        status="in_progress",
        total_score=0.0,
        report=None,
    )

    db.add(exam)
    db.commit()
    db.refresh(exam)

    question_score = calculate_question_score(config)
    questions = await generate_questions_with_llm(db, chapter, config)

    for item in questions:
        question = ExamQuestion(
            exam_id=exam.id,
            question_type=item.get("question_type", "short_answer"),
            question_text=item.get("question_text", ""),
            options=json.dumps(item.get("options", []), ensure_ascii=False),
            standard_answer=item.get("standard_answer", ""),
            analysis=item.get("analysis", ""),
            score=question_score,
        )

        db.add(question)

    db.commit()

    return exam


def list_exam_records(
    db: Session,
    user_id: int,
) -> List[ExamRecord]:
    """
    查询当前用户考试记录
    """
    return (
        db.query(ExamRecord)
        .filter(ExamRecord.user_id == user_id)
        .order_by(ExamRecord.id.desc())
        .all()
    )


def get_exam_record(
    db: Session,
    exam_id: int,
    user_id: int,
) -> Optional[ExamRecord]:
    """
    查询当前用户某次考试记录
    """
    return (
        db.query(ExamRecord)
        .filter(
            ExamRecord.id == exam_id,
            ExamRecord.user_id == user_id,
        )
        .first()
    )


def list_exam_questions(
    db: Session,
    exam_id: int,
) -> List[ExamQuestion]:
    """
    查询某次考试题目
    """
    return (
        db.query(ExamQuestion)
        .filter(ExamQuestion.exam_id == exam_id)
        .order_by(ExamQuestion.id.asc())
        .all()
    )


def question_to_response_dict(question: ExamQuestion) -> Dict:
    """
    题目转响应对象。

    注意：
    不返回 standard_answer 和 analysis，避免学生考试时看到答案。
    """
    try:
        options = json.loads(question.options) if question.options else []
    except Exception:
        options = []

    return {
        "id": question.id,
        "exam_id": question.exam_id,
        "question_type": question.question_type,
        "question_text": question.question_text,
        "options": options,
        "score": question.score,
        "created_at": question.created_at,
    }


def get_question_by_id(
    db: Session,
    question_id: int,
) -> Optional[ExamQuestion]:
    """
    根据题目ID查询题目
    """
    return (
        db.query(ExamQuestion)
        .filter(ExamQuestion.id == question_id)
        .first()
    )


def get_answer_by_question(
    db: Session,
    exam_id: int,
    question_id: int,
    user_id: int,
) -> Optional[ExamAnswer]:
    """
    查询学生某题答案
    """
    return (
        db.query(ExamAnswer)
        .filter(
            ExamAnswer.exam_id == exam_id,
            ExamAnswer.question_id == question_id,
            ExamAnswer.user_id == user_id,
        )
        .first()
    )


def normalize_answer_text(answer_text: str) -> str:
    """
    标准化答案文本，方便客观题判分
    """
    if answer_text is None:
        return ""

    text = answer_text.strip()

    text = text.replace("．", ".")
    text = text.replace("。", "")
    text = text.replace(" ", "")
    text = text.replace("\n", "")
    text = text.replace("\r", "")

    return text.lower()


def score_objective_question(
    question: ExamQuestion,
    answer_text: str,
) -> float:
    """
    客观题自动评分。

    choice:
    - 支持 B
    - 支持 b
    - 支持 B. xxx
    - 支持 选项B

    judge:
    - 支持 正确/错误
    - 支持 对/错
    - 支持 true/false
    """
    student = normalize_answer_text(answer_text)
    standard = normalize_answer_text(question.standard_answer)

    if question.question_type == "choice":
        if student.startswith(standard):
            return question.score

        if len(standard) == 1 and standard in student:
            return question.score

        return 0.0

    if question.question_type == "judge":
        true_values = {"正确", "对", "true", "yes", "是"}
        false_values = {"错误", "错", "false", "no", "否"}

        if standard in true_values and student in true_values:
            return question.score

        if standard in false_values and student in false_values:
            return question.score

        return 0.0

    return 0.0


def submit_answer(
    db: Session,
    exam: ExamRecord,
    question_id: int,
    user_id: int,
    answer_text: str,
) -> ExamAnswer:
    """
    提交单题答案
    """
    question = get_question_by_id(db, question_id)

    if not question:
        raise ValueError("题目不存在")

    if question.exam_id != exam.id:
        raise ValueError("题目不属于当前考试")

    answer = get_answer_by_question(
        db=db,
        exam_id=exam.id,
        question_id=question_id,
        user_id=user_id,
    )

    score = score_objective_question(question, answer_text)

    if question.question_type == "short_answer":
        feedback = "简答题将在提交考试后由学习报告综合评价"
    else:
        feedback = "客观题自动判分"

    if answer:
        answer.answer_text = answer_text
        answer.score = score
        answer.feedback = feedback
    else:
        answer = ExamAnswer(
            exam_id=exam.id,
            question_id=question_id,
            user_id=user_id,
            answer_text=answer_text,
            score=score,
            feedback=feedback,
        )
        db.add(answer)

    db.commit()
    db.refresh(answer)

    return answer


# =========================================================
# 交卷与评价报告
# =========================================================

def list_exam_answers(
    db: Session,
    exam_id: int,
    user_id: int,
) -> List[ExamAnswer]:
    """
    查询某次考试的答案
    """
    return (
        db.query(ExamAnswer)
        .filter(
            ExamAnswer.exam_id == exam_id,
            ExamAnswer.user_id == user_id,
        )
        .order_by(ExamAnswer.id.asc())
        .all()
    )


async def generate_exam_report(
    db: Session,
    exam: ExamRecord,
    questions: List[ExamQuestion],
    answers: List[ExamAnswer],
) -> str:
    """
    生成学习评价报告
    """
    config = get_exam_config_by_id(db, exam.config_id)
    model_config = get_active_model_config(db)

    answer_map = {
        answer.question_id: answer
        for answer in answers
    }

    qa_texts = []

    for question in questions:
        answer = answer_map.get(question.id)

        qa_texts.append(
            "--------------------\n"
            f"题型：{question.question_type}\n"
            f"题目：{question.question_text}\n"
            f"标准答案：{question.standard_answer}\n"
            f"题目解析：{question.analysis or ''}\n"
            f"学生答案：{answer.answer_text if answer else '未作答'}\n"
            f"当前得分：{answer.score if answer else 0}\n"
        )

    if not model_config:
        return (
            "## 学习评价报告\n\n"
            "当前未配置可用大模型，系统已完成客观题自动评分。\n\n"
            "### 一、总体评价\n"
            "学生已完成本章节考核，客观题已根据标准答案自动评分。\n\n"
            "### 二、知识掌握情况\n"
            "建议结合标准答案进一步复习本章节核心概念。\n\n"
            "### 三、基础概念掌握\n"
            "请重点检查选择题和判断题中错误的知识点。\n\n"
            "### 四、综合分析能力\n"
            "简答题需要从整体性、关联性、协同性等角度展开分析。\n\n"
            "### 五、建议复习知识点\n"
            "- 复习本章节核心概念。\n"
            "- 对照标准答案检查简答题表达是否完整。\n"
            "- 重点关注知识点之间的联系和综合应用。"
        )

    dimensions = (
        config.evaluation_dimensions
        if config and config.evaluation_dimensions
        else "知识掌握情况、基础概念掌握、综合分析能力、建议复习知识点"
    )

    prompt = (
        "你是课程学习评价助手，请根据学生章节考核情况生成学习评价报告。\n\n"
        f"评价维度：{dimensions}\n\n"
        "考试作答情况：\n"
        f"{chr(10).join(qa_texts)}\n\n"
        "输出要求：\n"
        "1. 使用 Markdown。\n"
        "2. 不要输出 HTML 标签。\n"
        "3. 结构必须包含：\n"
        "## 一、总体评价\n"
        "## 二、知识掌握情况\n"
        "## 三、基础概念掌握\n"
        "## 四、综合分析能力\n"
        "## 五、建议复习知识点\n"
        "4. 评价要具体，结合学生答案指出问题。"
    )

    try:
        return await chat_completion_once(
            model_config=model_config,
            messages=[
                {
                    "role": "system",
                    "content": "你是课程学习评价报告生成助手。",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

    except Exception as e:
        return (
            "## 学习评价报告\n\n"
            f"大模型评价失败：{str(e)}\n\n"
            "系统已完成客观题自动评分，请教师结合学生简答题进行进一步评价。"
        )



async def submit_exam(
    db: Session,
    exam: ExamRecord,
) -> ExamRecord:
    """
    提交考试并生成报告
    """
    questions = list_exam_questions(db, exam.id)

    answers = list_exam_answers(
        db=db,
        exam_id=exam.id,
        user_id=exam.user_id,
    )

    total_score = sum(answer.score for answer in answers)

    report = await generate_exam_report(
        db=db,
        exam=exam,
        questions=questions,
        answers=answers,
    )

    exam.total_score = round(total_score, 2)
    exam.status = "submitted"
    exam.report = report

    db.commit()
    db.refresh(exam)

    return exam