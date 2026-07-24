from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.system_log import SystemLog
from app.models.user import User


def create_system_log(
    db: Session,
    module: str,
    action: str,
    status: str = "success",
    message: Optional[str] = None,
    user: Optional[User] = None,
    method: Optional[str] = None,
    path: Optional[str] = None,
) -> SystemLog:
    """
    创建系统日志
    """
    log = SystemLog(
        user_id=user.id if user else None,
        username=user.username if user else None,
        module=module,
        action=action,
        method=method,
        path=path,
        status=status,
        message=message,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


def list_system_logs(
    db: Session,
    module: Optional[str] = None,
    username: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[SystemLog]:
    """
    查询系统日志列表
    """
    query = db.query(SystemLog)

    if module:
        query = query.filter(SystemLog.module.like(f"%{module}%"))

    if username:
        query = query.filter(SystemLog.username.like(f"%{username}%"))

    if status:
        query = query.filter(SystemLog.status == status)

    return query.order_by(SystemLog.id.desc()).limit(limit).all()


def get_system_log_by_id(db: Session, log_id: int) -> Optional[SystemLog]:
    """
    根据ID查询系统日志
    """
    return db.query(SystemLog).filter(SystemLog.id == log_id).first()
