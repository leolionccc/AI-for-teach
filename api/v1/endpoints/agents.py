from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.users import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.agent import AgentCreateRequest, AgentResponse, AgentUpdateRequest
from app.schemas.response import ApiResponse
from app.services.agent_service import (
    create_agent,
    delete_agent,
    get_agent_by_id,
    list_agents,
    update_agent,
)
from app.services.system_log_service import create_system_log


router = APIRouter()


@router.get("", response_model=ApiResponse)
def list_agent_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agents = list_agents(db)

    return ApiResponse(
        code=200,
        message="success",
        data=[AgentResponse.model_validate(item) for item in agents],
    )


@router.get("/{agent_id}", response_model=ApiResponse)
def get_agent_detail(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent = get_agent_by_id(db, agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="智能体不存在",
        )

    return ApiResponse(
        code=200,
        message="success",
        data=AgentResponse.model_validate(agent),
    )


@router.post("", response_model=ApiResponse)
def create_agent_config(
    request: AgentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent = create_agent(db, request, current_user.id)

    create_system_log(
        db=db,
        module="智能体管理",
        action="新增智能体",
        message=f"新增智能体：{agent.name}",
        user=current_user,
    )

    return ApiResponse(
        code=200,
        message="创建成功",
        data=AgentResponse.model_validate(agent),
    )


@router.put("/{agent_id}", response_model=ApiResponse)
def update_agent_config(
    agent_id: int,
    request: AgentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent = get_agent_by_id(db, agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="智能体不存在",
        )

    agent = update_agent(db, agent, request)

    create_system_log(
        db=db,
        module="智能体管理",
        action="修改智能体",
        message=f"修改智能体：{agent.name}",
        user=current_user,
    )

    return ApiResponse(
        code=200,
        message="修改成功",
        data=AgentResponse.model_validate(agent),
    )


@router.delete("/{agent_id}", response_model=ApiResponse)
def delete_agent_config(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent = get_agent_by_id(db, agent_id)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="智能体不存在",
        )

    agent_name = agent.name
    delete_agent(db, agent)

    create_system_log(
        db=db,
        module="智能体管理",
        action="删除智能体",
        message=f"删除智能体：{agent_name}",
        user=current_user,
    )

    return ApiResponse(
        code=200,
        message="删除成功",
        data=None,
    )