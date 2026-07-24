from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.user import (
    UserPasswordUpdateRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.services.user_service import get_user_by_id


router = APIRouter()

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前登录用户
    前端请求时需要携带请求头：
    Authorization: Bearer xxxxx
    """

    token = credentials.credentials

    user_id = decode_access_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效或已过期",
        )

    user = get_user_by_id(db, int(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    return user


@router.get("/me", response_model=ApiResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息
    """

    return ApiResponse(
        code=200,
        message="success",
        data=UserResponse.model_validate(current_user),
    )


@router.put("/me", response_model=ApiResponse)
def update_me(
    request: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    修改当前用户基本信息
    """

    if request.nickname is not None:
        current_user.nickname = request.nickname

    db.commit()
    db.refresh(current_user)

    return ApiResponse(
        code=200,
        message="修改成功",
        data=UserResponse.model_validate(current_user),
    )


@router.put("/me/password", response_model=ApiResponse)
def update_password(
    request: UserPasswordUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    修改当前用户密码
    """

    if not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误",
        )

    current_user.password_hash = get_password_hash(request.new_password)

    db.commit()

    return ApiResponse(
        code=200,
        message="密码修改成功",
        data=None,
    )