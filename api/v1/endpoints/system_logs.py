from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.users import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.system_log import SystemLogResponse
from app.services.system_log_service import get_system_log_by_id, list_system_logs


router = APIRouter()


@router.get("", response_model=ApiResponse)
def list_logs(
    module: Optional[str] = Query(None, description="模块名称"),
    username: Optional[str] = Query(None, description="用户名"),
    log_status: Optional[str] = Query(None, description="状态 success/fail"),
    limit: int = Query(100, ge=1, le=500, description="返回条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = list_system_logs(
        db=db,
        module=module,
        username=username,
        status=log_status,
        limit=limit,
    )

    return ApiResponse(
        code=200,
        message="success",
        data=[SystemLogResponse.model_validate(item) for item in logs],
    )


@router.get("/{log_id}", response_model=ApiResponse)
def get_log_detail(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = get_system_log_by_id(db, log_id)

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志不存在",
        )

    return ApiResponse(
        code=200,
        message="success",
        data=SystemLogResponse.model_validate(log),
    )