import json
import re
from typing import Dict, List, Optional, Tuple


from sqlalchemy.orm import Session

from app.models.exam import (
    Chapter,
    ExamAnswer,
    ExamConfig,
    ExamQuestion,
    ExamRecord,
)
from app.models.model_config import ModelConfig
from app.services.llm_service import chat_completion_once


# =========================================================
# 基础查询函数
# =========================================================

def get_chapter_by_id(
    db: Session,
    chapter_id: int,
) -> Optional[Chapter]:
    """
    根据章节ID查询章节
    """
    return (
        db.query(Chapter)
        .filter(Chapter.id == chapter_id)
        .first()
    )


def get_exam_config_by_id(
    db: Session,
    config_id: int,
) -> Optional[ExamConfig]:
    """
    根据配置ID查询考核配置
    """
    return (
        db.query(ExamConfig)
        .filter(ExamConfig.id == config_id)
        .first()
    )


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
# 大模型题目生成辅助函数
# =========================================================

def extract_json_array(text: str) -> List[Dict]:
    """
    从大模型输出内容中提取 JSON 数组。

    兼容以下情况：
    1. 纯 JSON 数组
    2. ```json ... ```
    3. 前后带解释文字的 JSON 数组
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

def extract_json_object(text: str) -> Dict:
    """
    从大模型输出中提取 JSON 对象。

    兼容：
    1. 纯 JSON 对象
    2. ```json ... ```
    3. 前后带解释文字的 JSON 对象
    """
    if not text:
        return {}

    raw = text.strip()
    raw = raw.replace("```json", "")
    raw = raw.replace("```", "")
    raw = raw.strip()

    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", raw)

    if not match:
        return {}

    try:
        data = json.loads(match.group(0))
        if isinstance(data, dict):
            return data
    except Exception:
        return {}

    return {}




def calculate_question_score(config: ExamConfig) -> float:
    """
    根据考核配置计算每道题的分值
    """
    total_count = (
        config.choice_count
        + config.judge_count
        + config.short_answer_count
    )

    if total_count <= 0:
        return 0.0

    return round(config.total_score / total_count, 2)


def build_fallback_questions(
    config: ExamConfig,
    chapter: Chapter,
) -> List[Dict]:
    """
    兜底题目生成。

    当未配置大模型、大模型调用失败或返回格式错误时，
    系统仍然可以生成题目，保证演示流程完整。
    """
    questions: List[Dict] = []

    for index in range(config.choice_count):
        questions.append(
            {
                "question_type": "choice",
                "question_text": (
                    f"关于“{chapter.title}”的学习内容，"
                    f"下列说法较为合理的是？"
                ),
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

    for index in range(config.judge_count):
        questions.append(
            {
                "question_type": "judge",
                "question_text": (
                    f"判断：学习“{chapter.title}”时，"
                    f"应关注不同要素之间的相互关系。"
                ),
                "options": ["正确", "错误"],
                "standard_answer": "正确",
                "analysis": "系统方法论强调要素之间的联系和协同。",
            }
        )

    for index in range(config.short_answer_count):
        questions.append(
            {
                "question_type": "short_answer",
                "question_text": (
                    f"请结合本章知识点，简述“{chapter.title}”"
                    f"体现的系统思维。"
                ),
                "options": [],
                "standard_answer": (
                    "应从整体性、关联性、协同性、统筹谋划等角度回答，"
                    "并结合具体知识点说明。"
                ),
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

        question_text = (
            item.get("question_text")
            or f"请简述“{chapter.title}”的相关知识点。"
        )

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

        return normalize_generated_questions(
            questions=questions,
            config=config,
            chapter=chapter,
        )

    except Exception:
        return build_fallback_questions(config, chapter)


# =========================================================
# 考试运行流程
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

    questions = await generate_questions_with_llm(
        db=db,
        chapter=chapter,
        config=config,
    )

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
    查询某次考试中某道题的学生答案
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


def list_exam_answers(
    db: Session,
    exam_id: int,
    user_id: int,
) -> List[ExamAnswer]:
    """
    查询某次考试的全部答案
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



def build_report_fallback(
    config: Optional[ExamConfig],
    total_score: float,
    questions: List[ExamQuestion],
    answers: List[ExamAnswer],
    reason: Optional[str] = None,
) -> str:
    """
    未配置大模型或大模型调用失败时生成兜底学习报告。
    """
    answer_count = len(answers)
    question_count = len(questions)

    dimensions = (
        config.evaluation_dimensions
        if config and config.evaluation_dimensions
        else "知识掌握情况、基础概念掌握、综合分析能力、建议复习知识点"
    )

    reason_text = ""
    if reason:
        reason_text = f"\n\n> 说明：{reason}\n"

    return (
        "## 学习评价报告\n\n"
        "### 一、总体评价\n"
        f"本次考试共 **{question_count}** 道题，学生已提交 **{answer_count}** 道题答案，"
        f"当前得分为 **{total_score}** 分。"
        f"{reason_text}\n\n"
        "### 二、知识掌握情况\n"
        "系统已完成客观题自动评分。建议学生结合错题、标准答案和题目解析复习本章节核心知识点。\n\n"
        "### 三、基础概念掌握\n"
        "如果选择题或判断题失分较多，说明基础概念仍需进一步巩固，应重点回看章节定义、分类、基本原理和关键概念。\n\n"
        "### 四、综合分析能力\n"
        "简答题主要考查学生对章节知识的综合理解、知识迁移和文字表达能力。建议学生对照标准答案补充关键概念、逻辑链条和例子说明。\n\n"
        "### 五、建议复习知识点\n"
        f"{dimensions}\n"
    )

async def evaluate_short_answers_and_generate_report(
    db: Session,
    exam: ExamRecord,
    questions: List[ExamQuestion],
    answers: List[ExamAnswer],
) -> Tuple[float, str]:
    """
    调用大模型评价简答题，并生成学习评价报告。

    返回：
    - total_score
    - report
    """
    config = get_exam_config_by_id(db, exam.config_id)
    model_config = get_active_model_config(db)

    answer_map = {
        answer.question_id: answer
        for answer in answers
    }

    current_total_score = round(sum(answer.score for answer in answers), 2)

    if not model_config:
        report = build_report_fallback(
            config=config,
            total_score=current_total_score,
            questions=questions,
            answers=answers,
            reason="当前未配置可用大模型，系统仅完成客观题自动评分。",
        )
        return current_total_score, report

    qa_items = []

    for question in questions:
        answer = answer_map.get(question.id)

        qa_items.append(
            {
                "question_id": question.id,
                "question_type": question.question_type,
                "question_score": question.score,
                "question_text": question.question_text,
                "standard_answer": question.standard_answer,
                "analysis": question.analysis or "",
                "student_answer": answer.answer_text if answer else "",
                "current_score": answer.score if answer else 0.0,
            }
        )

    dimensions = (
        config.evaluation_dimensions
        if config and config.evaluation_dimensions
        else "知识掌握情况、基础概念掌握、综合分析能力、建议复习知识点"
    )

    prompt = (
        "你是课程章节考核评价助手，请根据学生作答情况进行评分并生成学习评价报告。\n\n"
        "要求：\n"
        "1. 选择题和判断题已经由系统自动评分，你不要修改这些题的分数。\n"
        "2. 你只需要为 question_type 为 short_answer 的简答题评分。\n"
        "3. 简答题分数范围为 0 到 question_score。\n"
        "4. 请根据标准答案、题目解析和学生答案给出简答题反馈。\n"
        "5. 请生成 Markdown 格式学习评价报告。\n"
        "6. 不要输出 HTML 标签。\n\n"
        f"评价维度：{dimensions}\n\n"
        "考试数据 JSON：\n"
        f"{json.dumps(qa_items, ensure_ascii=False)}\n\n"
        "请只返回 JSON 对象，不要返回 Markdown 代码块，不要返回解释文字。\n"
        "JSON 格式如下：\n"
        "{\n"
        "  \"short_answer_scores\": [\n"
        "    {\n"
        "      \"question_id\": 1,\n"
        "      \"score\": 10,\n"
        "      \"feedback\": \"回答较完整，能够说明核心概念。\"\n"
        "    }\n"
        "  ],\n"
        "  \"report\": \"## 一、总体评价\\n...\"\n"
        "}\n"
    )

    try:
        content = await chat_completion_once(
            model_config=model_config,
            messages=[
                {
                    "role": "system",
                    "content": "你是严格输出 JSON 的课程学习评价助手。",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        data = extract_json_object(content)

        short_answer_scores = data.get("short_answer_scores", [])
        report = data.get("report", "")

        if isinstance(short_answer_scores, list):
            for item in short_answer_scores:
                if not isinstance(item, dict):
                    continue

                question_id = item.get("question_id")
                score = item.get("score", 0)
                feedback = item.get("feedback", "")

                try:
                    question_id = int(question_id)
                except Exception:
                    continue

                answer = answer_map.get(question_id)

                if not answer:
                    continue

                question = get_question_by_id(db, question_id)

                if not question:
                    continue

                if question.question_type != "short_answer":
                    continue

                try:
                    score_value = float(score)
                except Exception:
                    score_value = 0.0

                if score_value < 0:
                    score_value = 0.0

                if score_value > question.score:
                    score_value = question.score

                answer.score = round(score_value, 2)
                answer.feedback = feedback or "简答题由大模型完成评价"

        db.commit()

        refreshed_answers = list_exam_answers(
            db=db,
            exam_id=exam.id,
            user_id=exam.user_id,
        )

        total_score = round(sum(answer.score for answer in refreshed_answers), 2)

        if not report:
            report = build_report_fallback(
                config=config,
                total_score=total_score,
                questions=questions,
                answers=refreshed_answers,
                reason="大模型未返回有效报告，系统生成兜底学习报告。",
            )

        return total_score, report

    except Exception as e:
        refreshed_answers = list_exam_answers(
            db=db,
            exam_id=exam.id,
            user_id=exam.user_id,
        )

        total_score = round(sum(answer.score for answer in refreshed_answers), 2)

        report = build_report_fallback(
            config=config,
            total_score=total_score,
            questions=questions,
            answers=refreshed_answers,
            reason=f"大模型评价失败：{str(e)}",
        )

        return total_score, report





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
    提交单题答案。

    如果该题之前已经提交过答案，则更新答案；
    如果未提交过，则新增答案。
    """
    question = get_question_by_id(
        db=db,
        question_id=question_id,
    )

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

    score = score_objective_question(
        question=question,
        answer_text=answer_text,
    )

    if question.question_type == "short_answer":
        feedback = "简答题将在下一阶段由学习评价报告综合分析"
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



async def submit_exam(
    db: Session,
    exam: ExamRecord,
) -> ExamRecord:
    """
    提交考试并生成学习评价报告。
    """
    questions = list_exam_questions(
        db=db,
        exam_id=exam.id,
    )

    answers = list_exam_answers(
        db=db,
        exam_id=exam.id,
        user_id=exam.user_id,
    )

    total_score, report = await evaluate_short_answers_and_generate_report(
        db=db,
        exam=exam,
        questions=questions,
        answers=answers,
    )

    exam.total_score = total_score
    exam.status = "submitted"
    exam.report = report

    db.commit()
    db.refresh(exam)

    return exam




def build_exam_report_detail(
    db: Session,
    exam: ExamRecord,
) -> List[Dict]:
    """
    构建考试报告详情。

    返回内容包括：
    1. 题目信息
    2. 标准答案
    3. 题目解析
    4. 学生答案
    5. 学生得分
    6. 反馈信息
    """
    questions = list_exam_questions(
        db=db,
        exam_id=exam.id,
    )

    answers = list_exam_answers(
        db=db,
        exam_id=exam.id,
        user_id=exam.user_id,
    )

    answer_map = {
        answer.question_id: answer
        for answer in answers
    }

    result = []

    for question in questions:
        answer = answer_map.get(question.id)

        try:
            options = json.loads(question.options) if question.options else []
        except Exception:
            options = []

        result.append(
            {
                "question_id": question.id,
                "question_type": question.question_type,
                "question_text": question.question_text,
                "options": options,
                "standard_answer": question.standard_answer,
                "analysis": question.analysis,
                "question_score": question.score,
                "student_answer": answer.answer_text if answer else None,
                "student_score": answer.score if answer else 0.0,
                "feedback": answer.feedback if answer else None,
            }
        )

    return result
