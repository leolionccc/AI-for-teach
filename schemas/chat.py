from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatSessionCreateRequest(BaseModel):
    title: str = Field("新的对话", max_length=200, description="会话标题")
    agent_id: Optional[int] = Field(None, description="智能体ID")


class ChatSessionUpdateRequest(BaseModel):
    title: str = Field(..., max_length=200, description="会话标题")


class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    agent_id: Optional[int] = None
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ChatMessageCreateRequest(BaseModel):
    role: str = Field(..., description="角色：user/assistant/system")
    content: str = Field(..., description="消息内容")
    model_name: Optional[str] = Field(None, description="模型名称")
    token_count: Optional[int] = Field(None, description="Token数量")


class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    user_id: int
    role: str
    content: str
    model_name: Optional[str] = None
    token_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }