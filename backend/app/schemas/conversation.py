"""会话相关 Pydantic 模型"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    """创建会话请求"""
    title: str = Field(default="新对话", max_length=200)


class ConversationUpdate(BaseModel):
    """更新会话标题"""
    title: str = Field(..., min_length=1, max_length=200)


class ConversationResponse(BaseModel):
    """会话响应"""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class ConversationDetail(ConversationResponse):
    """会话详情（含消息列表）"""
    messages: list = []


class ConversationListResponse(BaseModel):
    """会话列表分页响应"""
    items: list[ConversationResponse]
    total: int
    page: int
    page_size: int
