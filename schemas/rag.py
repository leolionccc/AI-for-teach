from typing import List, Optional

from pydantic import BaseModel, Field


class BuildMaterialIndexRequest(BaseModel):
    """
    构建单个资料索引请求
    """

    material_id: int = Field(..., description="资料ID")


class RagSearchRequest(BaseModel):
    """
    RAG 检索请求
    """

    query: str = Field(..., description="用户问题")
    top_k: int = Field(5, ge=1, le=20, description="返回片段数量")


class RagSearchItem(BaseModel):
    """
    RAG 检索结果
    """

    material_id: str
    material_name: str
    chunk_index: int
    content: str
    distance: Optional[float] = None


class ChatStreamRequest(BaseModel):
    """
    智能体流式问答请求
    """

    question: str = Field(..., description="用户问题")
    session_id: Optional[int] = Field(None, description="会话ID，不传则自动创建")
    agent_id: Optional[int] = Field(None, description="智能体ID")
    top_k: int = Field(5, ge=1, le=20, description="检索片段数量")