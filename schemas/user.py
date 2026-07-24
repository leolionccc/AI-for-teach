from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    """
    用户注册请求
    """

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    role: str = Field("student", description="角色：student/teacher/admin")


class UserLoginRequest(BaseModel):
    """
    用户登录请求
    """

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserUpdateRequest(BaseModel):
    """
    修改当前用户信息请求
    """

    nickname: Optional[str] = Field(None, max_length=50, description="昵称")


class UserPasswordUpdateRequest(BaseModel):
    """
    修改密码请求
    """

    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class UserResponse(BaseModel):
    """
    用户响应
    """

    id: int
    username: str
    nickname: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }