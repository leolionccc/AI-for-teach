from fastapi import APIRouter

from app.api.v1.endpoints import (
    agents,
    auth,
    chat_history,
    health,
    materials,
    model_configs,
    rag,
    system_logs,
    users,
    exams,
)


api_router = APIRouter()

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["系统健康检查"],
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["用户认证"],
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用户管理"],
)

api_router.include_router(
    model_configs.router,
    prefix="/model-configs",
    tags=["大模型配置"],
)

api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["智能体管理"],
)

api_router.include_router(
    chat_history.router,
    prefix="/chat-history",
    tags=["调用历史"],
)

api_router.include_router(
    system_logs.router,
    prefix="/system-logs",
    tags=["系统日志"],
)

api_router.include_router(
    materials.router,
    prefix="/materials",
    tags=["课程资料"],
)

api_router.include_router(
    rag.router,
    prefix="/rag",
    tags=["智能体问答"],
)

api_router.include_router(
    exams.router,
    prefix="/exams",
    tags=["章节与考核配置"],
)