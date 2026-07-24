from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.response import ApiResponse


router = APIRouter()


@router.get("", response_model=ApiResponse)
def health_check():
    """
    系统健康检查接口
    """

    return ApiResponse(
        code=200,
        message="success",
        data={
            "status": "ok",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "env": settings.APP_ENV,
        },
    )


@router.get("/db", response_model=ApiResponse)
def database_check(db: Session = Depends(get_db)):
    """
    数据库连接检查接口
    """

    db.execute(text("SELECT 1"))

    return ApiResponse(
        code=200,
        message="database connected",
        data={
            "database": "sqlite",
            "status": "ok",
        },
    )