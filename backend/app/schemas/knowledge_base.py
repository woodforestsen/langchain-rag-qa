"""知识库相关 Pydantic 模型"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """文档响应"""
    id: int
    filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    error_message: Optional[str] = None
    uploader_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentChunkResponse(BaseModel):
    """文档块响应"""
    id: int
    chunk_index: int
    content: str
    char_count: int

    model_config = {"from_attributes": True}


class DocumentDetailResponse(DocumentResponse):
    """文档详情（含分块列表）"""
    chunks: list[DocumentChunkResponse] = []


class DocumentListResponse(BaseModel):
    """文档列表分页响应"""
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int


class KnowledgeStatsResponse(BaseModel):
    """知识库统计"""
    total_documents: int
    total_chunks: int
    total_chars: int
    documents_by_type: dict[str, int]
    documents_by_status: dict[str, int]
