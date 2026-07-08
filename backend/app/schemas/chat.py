"""聊天相关 Pydantic 模型"""

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """发送消息请求"""
    conversation_id: int = Field(..., description="会话ID")
    question: str = Field(..., min_length=1, max_length=5000, description="用户问题")


class CitationSource(BaseModel):
    """知识库引用来源"""
    index: int = Field(..., description="引用序号")
    document_name: str = Field(..., description="来源文档名")
    chunk_id: int = Field(..., description="文档块ID")
    excerpt: str = Field(..., description="引用原文片段")
    score: float = Field(..., description="相似度分数")


class MessageResponse(BaseModel):
    """消息响应"""
    id: int
    conversation_id: int
    role: str
    content: str
    sources: Optional[list[dict]] = None
    created_at: str

    model_config = {"from_attributes": True}
