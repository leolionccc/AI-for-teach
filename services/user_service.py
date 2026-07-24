from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserRegisterRequest


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    根据用户ID查询用户
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    根据用户名查询用户
    """
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, request: UserRegisterRequest) -> User:
    """
    创建用户
    """
    user = User(
        username=request.username,
        password_hash=get_password_hash(request.password),
        nickname=request.nickname or request.username,
        role=request.role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    用户登录认证
    """
    user = get_user_by_username(db, username)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.is_active:
        return None

    return user