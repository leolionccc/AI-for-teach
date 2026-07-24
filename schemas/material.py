from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MaterialListResponse(BaseModel):
    """
    课程资料列表响应对象
    不返回 content，避免列表接口响应过大
    """

    id: int
    name: str
    stored_name: str
    file_path: str
    file_type: str
    file_size: int
    parse_status: str
    parse_error: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MaterialDetailResponse(BaseModel):
    """
    课程资料详情响应对象
    查看内容时才返回 content
    """

    id: int
    name: str
    stored_name: str
    file_path: str
    file_type: str
    file_size: int
    content: Optional[str] = None
    parse_status: str
    parse_error: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)