from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import ChatMessageCreateRequest, ChatSessionCreateRequest


def list_chat_sessions(db: Session, user_id: int) -> List[ChatSession]:
    """
    查询当前用户的所有对话会话
    """
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.id.desc())
        .all()
    )


def get_chat_session_by_id(
    db: Session,
    session_id: int,
    user_id: int,
) -> Optional[ChatSession]:
    """
    根据会话ID和用户ID查询会话
    """
    return (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id,
        )
        .first()
    )


def create_chat_session(
    db: Session,
    request: ChatSessionCreateRequest,
    user_id: int,
) -> ChatSession:
    """
    创建对话会话
    """
    session = ChatSession(
        user_id=user_id,
        agent_id=request.agent_id,
        title=request.title,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def update_chat_session_title(
    db: Session,
    session: ChatSession,
    title: str,
) -> ChatSession:
    """
    修改会话标题
    """
    session.title = title

    db.commit()
    db.refresh(session)

    return session


def delete_chat_session(db: Session, session: ChatSession) -> None:
    """
    删除会话及其下面的所有消息
    """
    db.query(ChatMessage).filter(ChatMessage.session_id == session.id).delete()
    db.delete(session)
    db.commit()


def list_chat_messages(
    db: Session,
    session_id: int,
    user_id: int,
) -> List[ChatMessage]:
    """
    查询某个会话下的消息列表
    """
    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id,
            ChatMessage.user_id == user_id,
        )
        .order_by(ChatMessage.id.asc())
        .all()
    )


def create_chat_message(
    db: Session,
    session_id: int,
    user_id: int,
    request: ChatMessageCreateRequest,
) -> ChatMessage:
    """
    创建一条聊天消息
    """
    message = ChatMessage(
        session_id=session_id,
        user_id=user_id,
        role=request.role,
        content=request.content,
        model_name=request.model_name,
        token_count=request.token_count,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message