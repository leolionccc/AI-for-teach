from typing import Any, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """
    统一接口响应结构
    """

    code: int = 200
    message: str = "success"
    data: Optional[Any] = None