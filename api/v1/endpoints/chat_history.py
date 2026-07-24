from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.users import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatMessageCreateRequest,
    ChatMessageResponse,
    ChatSessionCreateRequest,
    ChatSessionResponse,
    ChatSessionUpdateRequest,
)
from app.schemas.response import ApiResponse
from app.services.chat_service import (
    create_chat_message,
    create_chat_session,
    delete_chat_session,
    get_chat_session_by_id,
    list_chat_messages,
    list_chat_sessions,
    update_chat_session_title,
)
from app.services.system_log_service import create_system_log


router = APIRouter()


@router.get("/sessions", response_model=ApiResponse)
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = list_chat_sessions(db, current_user.id)

    return ApiResponse(
        code=200,
        message="success",
        data=[ChatSessionResponse.model_validate(item) for item in sessions],
    )


@router.post("/sessions", response_model=ApiResponse)
def create_session(
    request: ChatSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = create_chat_session(db, request, current_user.id)

    create_system_log(
        db=db,
        module="调用历史",
        action="创建对话会话",
        message=f"创建会话：{session.title}",
        user=current_user,
    )

    return ApiResponse(
        code=200,
        message="创建成功",
        data=ChatSessionResponse.model_validate(session),
    )


@router.put("/sessions/{session_id}", response_model=ApiResponse)
def update_session(
    session_id: int,
    request: ChatSessionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = get_chat_session_by_id(db, session_id, current_user.id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )

    session = update_chat_session_title(db, session, request.title)

    return ApiResponse(
        code=200,
        message="修改成功",
        data=ChatSessionResponse.model_validate(session),
    )


@router.delete("/sessions/{session_id}", response_model=ApiResponse)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = get_chat_session_by_id(db, session_id, current_user.id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )

    delete_chat_session(db, session)

    create_system_log(
        db=db,
        module="调用历史",
        action="删除对话会话",
        message=f"删除会话ID：{session_id}",
        user=current_user,
    )

    return ApiResponse(
        code=200,
        message="删除成功",
        data=None,
    )


@router.get("/sessions/{session_id}/messages", response_model=ApiResponse)
def list_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = get_chat_session_by_id(db, session_id, current_user.id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )

    messages = list_chat_messages(db, session_id, current_user.id)

    return ApiResponse(
        code=200,
        message="success",
        data=[ChatMessageResponse.model_validate(item) for item in messages],
    )


@router.post("/sessions/{session_id}/messages", response_model=ApiResponse)
def create_message(
    session_id: int,
    request: ChatMessageCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = get_chat_session_by_id(db, session_id, current_user.id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在",
        )

    if request.role not in ["user", "assistant", "system"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="role 只能是 user、assistant 或 system",
        )

    message = create_chat_message(db, session_id, current_user.id, request)

    return ApiResponse(
        code=200,
        message="创建成功",
        data=ChatMessageResponse.model_validate(message),
    )