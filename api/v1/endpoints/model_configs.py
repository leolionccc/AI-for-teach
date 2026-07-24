from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.users import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.model_config import (
    ModelConfigCreateRequest,
    ModelConfigResponse,
    ModelConfigUpdateRequest,
)
from app.schemas.response import ApiResponse
from app.services.model_config_service import (
    activate_model_config,
    create_model_config,
    delete_model_config,
    get_active_model_config,
    get_model_config_by_id,
    list_model_configs,
    to_model_config_response_data,
    update_model_config,
)
from app.services.system_log_service import create_system_log


router = APIRouter()


@router.get("", response_model=ApiResponse)
def list_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    configs = list_model_configs(db)

    return ApiResponse(
        code=200,
        message="success",
        data=[to_model_config_response_data(item) for item in configs],
    )


@router.get("/active", response_model=ApiResponse)
def get_active_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    config = get_active_model_config(db)

    if not config:
        return ApiResponse(
            code=200,
            message="当前没有启用的大模型配置",
            data=None,
        )

    return ApiResponse(
        code=200,
        message="success",
        data=to_model_config_response_data(config),
    )


@router.post("", response_model=ApiResponse)
def create_config(
    request: ModelConfigCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    config = create_model_config(db, request, current_user.id)

    create_system_log(
        db=db,
        module="大模型配置",
        action="新增大模型配置",
        message=f"新增配置：{config.name}",
        user=current_user,
    )

    return ApiResponse(
        code=200,
        message="创建成功",
        data=to_model_config_response_data(config),
    )


@router.put("/{config_id}", response_model=ApiResponse)
def update_config(
    config_id: int,
    request: ModelConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    config = get_model_config_by_id(db, config_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="大模型配置不存在",
        )

    config = update_model_config(db, config, request)

    create_system_log(
        db=db,
        module="大模型配置",
        action="修改大模型配置",
        message=f"修改配置：{config.name}",
        user=current_user,
    )

    return ApiResponse(
        code=200,
        message="修改成功",
        data=to_model_config_response_data(config),
    )


@router.post("/{config_id}/activate", response_model=ApiResponse)
def activate_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    config = get_model_config_by_id(db, config_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="大模型配置不存在",
        )

    config = activate_model_config(db, config)

    create_system_log(
        db=db,
        module="大模型配置",
        action="启用大模型配置",
        message=f"启用配置：{config.name}",
        user=current_user,
    )

    return ApiResponse(
        code=200,
        message="启用成功",
        data=to_model_config_response_data(config),
    )


@router.delete("/{config_id}", response_model=ApiResponse)
def delete_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    config = get_model_config_by_id(db, config_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="大模型配置不存在",
        )

    config_name = config.name
    delete_model_config(db, config)

    create_system_log(
        db=db,
        module="大模型配置",
        action="删除大模型配置",
        message=f"删除配置：{config_name}",
        user=current_user,
    )

    return ApiResponse(
        code=200,
        message="删除成功",
        data=None,
    )