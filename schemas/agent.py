from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AgentCreateRequest(BaseModel):
    """
    新增智能体请求
    """

    name: str = Field(..., max_length=100, description="智能体名称")
    description: Optional[str] = Field(None, description="智能体介绍")
    system_prompt: str = Field(..., description="系统提示词")
    welcome_message: Optional[str] = Field(None, description="欢迎语")
    avatar: Optional[str] = Field(None, max_length=255, description="头像地址")
    is_enabled: bool = Field(True, description="是否启用")


class AgentUpdateRequest(BaseModel):
    """
    修改智能体请求
    """

    name: Optional[str] = Field(None, max_length=100, description="智能体名称")
    description: Optional[str] = Field(None, description="智能体介绍")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    welcome_message: Optional[str] = Field(None, description="欢迎语")
    avatar: Optional[str] = Field(None, max_length=255, description="头像地址")
    is_enabled: Optional[bool] = Field(None, description="是否启用")


class AgentResponse(BaseModel):
    """
    智能体响应
    """

    id: int
    name: str
    description: Optional[str] = None
    system_prompt: str
    welcome_message: Optional[str] = None
    avatar: Optional[str] = None
    is_enabled: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }