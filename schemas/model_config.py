from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ModelConfigCreateRequest(BaseModel):
    """
    新增大模型配置请求
    """

    model_config = ConfigDict(protected_namespaces=())

    name: str = Field(..., max_length=100, description="配置名称")
    provider: str = Field(..., description="供应商：openai/qwen/deepseek/custom")
    model_name: str = Field(..., max_length=100, description="模型名称")
    api_base_url: Optional[str] = Field(None, max_length=255, description="API基础地址")
    api_key: Optional[str] = Field(None, description="API Key")
    temperature: str = Field("0.7", description="温度参数")
    max_tokens: int = Field(2048, ge=1, le=100000, description="最大Token数")
    is_active: bool = Field(False, description="是否启用")
    remark: Optional[str] = Field(None, description="备注")


class ModelConfigUpdateRequest(BaseModel):
    """
    修改大模型配置请求
    """

    model_config = ConfigDict(protected_namespaces=())

    name: Optional[str] = Field(None, max_length=100)
    provider: Optional[str] = None
    model_name: Optional[str] = Field(None, max_length=100)
    api_base_url: Optional[str] = Field(None, max_length=255)
    api_key: Optional[str] = None
    temperature: Optional[str] = None
    max_tokens: Optional[int] = Field(None, ge=1, le=100000)
    is_active: Optional[bool] = None
    remark: Optional[str] = None


class ModelConfigResponse(BaseModel):
    """
    大模型配置响应
    """

    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()
    )

    id: int
    name: str
    provider: str
    model_name: str
    api_base_url: Optional[str] = None
    api_key_masked: Optional[str] = None
    temperature: str
    max_tokens: int
    is_active: bool
    remark: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime