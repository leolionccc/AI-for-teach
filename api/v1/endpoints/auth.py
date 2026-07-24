from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.response import ApiResponse
from app.schemas.token import TokenResponse
from app.schemas.user import UserLoginRequest, UserRegisterRequest, UserResponse
from app.services.user_service import (
    authenticate_user,
    create_user,
    get_user_by_username,
)


router = APIRouter()


@router.post("/register", response_model=ApiResponse)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册
    """

    exists_user = get_user_by_username(db, request.username)
    if exists_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )

    if request.role not in ["student", "teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色只能是 student、teacher 或 admin",
        )

    user = create_user(db, request)

    return ApiResponse(
        code=200,
        message="注册成功",
        data=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=ApiResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    """

    user = authenticate_user(db, request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=access_token_expires,
    )

    token_data = TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )

    return ApiResponse(
        code=200,
        message="登录成功",
        data={
            "token": token_data.model_dump(),
            "user": UserResponse.model_validate(user).model_dump(),
        },
    )