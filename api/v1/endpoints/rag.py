import asyncio
import json
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.v1.endpoints.users import get_current_user
from app.core.database import get_db
from app.models.agent import Agent
from app.models.chat import ChatMessage, ChatSession
from app.models.model_config import ModelConfig
from app.models.user import User
from app.schemas.rag import (
    BuildMaterialIndexRequest,
    ChatStreamRequest,
    RagSearchRequest,
)
from app.schemas.response import ApiResponse
from app.services.llm_service import (
    fallback_stream_answer,
    stream_openai_compatible_chat,
)
from app.services.rag_service import (
    build_all_material_indexes,
    build_material_index,
    build_rag_context,
    build_recommendations,
    search_knowledge,
)


router = APIRouter()


def sse_event(data: dict) -> str:
    """
    构造 SSE 数据格式。
    """
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def sse_comment_padding() -> str:
    """
    SSE 注释行，用于减少浏览器/代理小块缓冲。
    前端会忽略不是 data: 开头的行。
    """
    return ":" + (" " * 2048) + "\n\n"


def get_active_model_config(db: Session) -> Optional[ModelConfig]:

    """
    获取当前启用的大模型配置
    """
    return (
        db.query(ModelConfig)
        .filter(ModelConfig.is_active == True)
        .first()
    )


def get_agent(
    db: Session,
    agent_id: Optional[int],
) -> Optional[Agent]:
    """
    获取智能体。
    如果传 agent_id，则查指定智能体；
    否则查第一个启用状态的智能体。
    """
    if agent_id:
        return db.query(Agent).filter(Agent.id == agent_id).first()

    return (
        db.query(Agent)
        .filter(Agent.is_enabled == True)
        .order_by(Agent.id.asc())
        .first()
    )


def get_or_create_session(
    db: Session,
    user_id: int,
    session_id: Optional[int],
    agent_id: Optional[int],
    question: str,
) -> ChatSession:
    """
    获取或创建对话会话
    """
    if session_id:
        session = (
            db.query(ChatSession)
            .filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
            .first()
        )

        if not session:
            raise ValueError("会话不存在")

        return session

    session = ChatSession(
        user_id=user_id,
        agent_id=agent_id,
        title=question[:30] if question else "新的智能体问答",
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def save_chat_message(
    db: Session,
    session_id: int,
    user_id: int,
    role: str,
    content: str,
    model_name: Optional[str] = None,
) -> ChatMessage:
    """
    保存对话消息
    """
    message = ChatMessage(
        session_id=session_id,
        user_id=user_id,
        role=role,
        content=content,
        model_name=model_name,
        token_count=len(content) if content else 0,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


async def yield_text_by_char(
    text: str,
    delay: float = 0.03,
) -> AsyncGenerator[str, None]:
    """
    将一段文本拆成单字符 SSE 输出。
    这样即使大模型一次返回一大段，前端也能明显看到流式效果。
    """
    if not text:
        return

    for char in text:
        yield sse_event(
            {
                "type": "delta",
                "content": char,
            }
        )
        await asyncio.sleep(delay)


@router.post("/materials/build-index", response_model=ApiResponse)
def build_one_material_index(
    request: BuildMaterialIndexRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    为单个课程资料构建知识库索引
    """
    try:
        result = build_material_index(db, request.material_id)

        return ApiResponse(
            code=200,
            message="构建成功",
            data=result,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/materials/build-all", response_model=ApiResponse)
def build_all_indexes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    为所有课程资料构建知识库索引
    """
    result = build_all_material_indexes(db)

    return ApiResponse(
        code=200,
        message="构建完成",
        data=result,
    )


@router.post("/search", response_model=ApiResponse)
def rag_search(
    request: RagSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    RAG 知识库检索测试接口
    """
    results = search_knowledge(
        query=request.query,
        top_k=request.top_k,
    )

    return ApiResponse(
        code=200,
        message="success",
        data=results,
    )


@router.post("/chat/stream")
async def rag_chat_stream(
    request: ChatStreamRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    智能体问答 SSE 流式接口。
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        full_answer = ""
        model_name = None
        recommendations = []

        try:
            # 关键：先发 padding，减少代理/浏览器缓冲
            yield sse_comment_padding()

            question = request.question.strip()

            if not question:
                yield sse_event(
                    {
                        "type": "error",
                        "message": "问题不能为空",
                    }
                )
                return

            agent = get_agent(
                db=db,
                agent_id=request.agent_id,
            )

            model_config = get_active_model_config(db)

            session = get_or_create_session(
                db=db,
                user_id=current_user.id,
                session_id=request.session_id,
                agent_id=agent.id if agent else request.agent_id,
                question=question,
            )

            # 立即通知前端会话已创建
            yield sse_event(
                {
                    "type": "session",
                    "session_id": session.id,
                }
            )

            yield sse_event(
                {
                    "type": "status",
                    "message": "正在保存用户问题...",
                }
            )

            save_chat_message(
                db=db,
                session_id=session.id,
                user_id=current_user.id,
                role="user",
                content=question,
            )

            yield sse_event(
                {
                    "type": "status",
                    "message": "正在检索课程知识库...",
                }
            )

            search_results = search_knowledge(
                query=question,
                top_k=request.top_k,
            )

            rag_context = build_rag_context(search_results)
            recommendations = build_recommendations(search_results)

            yield sse_event(
                {
                    "type": "references",
                    "data": recommendations,
                }
            )

            yield sse_event(
                {
                    "type": "status",
                    "message": "正在生成回答...",
                }
            )

            system_prompt = (
                agent.system_prompt
                if agent and agent.system_prompt
                else "你是人工智能导论课程学习助手，请基于课程资料回答学生问题。"
            )

            prompt = (
                f"{system_prompt}\n\n"
                f"请严格参考以下课程资料内容回答问题。如果资料中没有相关内容，"
                f"请明确说明“资料中未找到直接依据”，不要编造。\n\n"
                f"【课程资料上下文】\n"
                f"{rag_context}\n\n"
                f"【学生问题】\n"
                f"{question}\n\n"
                f"【回答格式要求】\n"
                f"请只输出标准 Markdown，不要输出 HTML。\n"
                f"禁止使用 <br>、<strong>、<ul>、<li>、<p> 等 HTML 标签。\n"
                f"不要输出连续空行，每个段落之间最多 1 个空行。\n"
                f"请按以下结构回答：\n\n"
                f"## 一、核心回答\n"
                f"简要回答用户问题。\n\n"
                f"## 二、具体分析\n"
                f"使用项目符号列表展开说明，重点概念用 **加粗**。\n\n"
                f"## 三、总结\n"
                f"用 1 段话总结。\n\n"
                f"## 四、相关资料建议\n"
                f"列出与问题相关的资料名称。"
            )

            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ]

            if model_config:
                model_name = model_config.model_name

            if not model_config:
                async for token in fallback_stream_answer(
                    question=question,
                    context=rag_context,
                    reason="未找到已启用的大模型配置",
                ):
                    full_answer += token

                    async for event in yield_text_by_char(token, delay=0.03):
                        yield event

            else:
                try:
                    async for token in stream_openai_compatible_chat(
                        model_config=model_config,
                        messages=messages,
                    ):
                        full_answer += token

                        async for event in yield_text_by_char(token, delay=0.03):
                            yield event

                except Exception as e:
                    async for token in fallback_stream_answer(
                        question=question,
                        context=rag_context,
                        reason=str(e),
                    ):
                        full_answer += token

                        async for event in yield_text_by_char(token, delay=0.03):
                            yield event

            save_chat_message(
                db=db,
                session_id=session.id,
                user_id=current_user.id,
                role="assistant",
                content=full_answer,
                model_name=model_name,
            )

            yield sse_event(
                {
                    "type": "done",
                    "session_id": session.id,
                    "references": recommendations,
                }
            )

        except ValueError as e:
            yield sse_event(
                {
                    "type": "error",
                    "message": str(e),
                }
            )

        except Exception as e:
            yield sse_event(
                {
                    "type": "error",
                    "message": f"系统异常：{str(e)}",
                }
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )