"""知识库管理 API - 仅管理员可访问"""

import os

from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.deps import get_current_active_user, require_admin
from app.db.session import get_db
from app.models.document import Document, DocumentChunk
from app.models.user import User
from app.schemas.knowledge_base import (
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentResponse,
    KnowledgeStatsResponse,
)
from app.services.document_service import (
    compute_file_hash,
    create_document_record,
    delete_document,
    extract_text_from_file,
    get_document,
    get_knowledge_stats,
    list_documents,
    save_uploaded_file,
    clean_text,
)
from app.rag.chunker import split_text
from app.rag.embeddings import get_embeddings
from app.rag.vector_store import get_global_collection, delete_collection

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "md", "csv", "xlsx"}


async def _process_single_file(file: UploadFile, current_user: User, db: AsyncSession) -> dict:
    """处理单个文件上传"""
    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        return {"filename": filename, "status": "error", "error": f"不支持的文件类型 .{ext}"}

    content = await file.read()
    file_size = len(content)
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size < 1024 and ext == "pdf":
        return {"filename": filename, "status": "error", "error": "文件过小（<1KB），不是有效的 PDF 文件"}
    if file_size > max_size:
        return {"filename": filename, "status": "error", "error": f"文件大小超过{settings.MAX_UPLOAD_SIZE_MB}MB"}

    # 去重
    file_hash = compute_file_hash(content)
    from sqlalchemy import select
    result = await db.execute(select(Document).where(Document.file_hash == file_hash))
    if result.scalar_one_or_none():
        return {"filename": filename, "status": "skipped", "error": "文件已存在"}

    # 保存文件（用哈希做文件名，避免中文乱码）
    os.makedirs("./data/uploads", exist_ok=True)
    safe_name = f"{file_hash}.{ext}"
    file_path = f"./data/uploads/{safe_name}"
    with open(file_path, "wb") as f:
        f.write(content)

    document = await create_document_record(db, filename, ext, file_size, file_hash, current_user)

    try:
        text = extract_text_from_file(file_path, ext)
        text = clean_text(text)
        if not text.strip():
            document.status = "error"
            document.error_message = "文档内容为空"
            db.add(document)
            await db.flush()
            return {"filename": filename, "status": "error", "error": "文档内容为空"}

        chunks = split_text(text)
        embeddings = get_embeddings()
        collection = get_global_collection()

        for i, chunk_text in enumerate(chunks):
            chunk_record = DocumentChunk(
                document_id=document.id, chunk_index=i,
                content=chunk_text, char_count=len(chunk_text),
                chroma_id=f"{document.collection_name}_{i}",
            )
            db.add(chunk_record)
            chunk_embedding = embeddings.embed_query(chunk_text)
            collection.add(
                ids=[f"{document.collection_name}_{i}"],
                embeddings=[chunk_embedding],
                documents=[chunk_text],
                metadatas=[{"document_id": str(document.id), "chunk_id": str(i),
                            "filename": filename, "file_type": ext,
                            "collection": document.collection_name}],
            )

        document.status = "ready"
        document.chunk_count = len(chunks)
        db.add(document)
        await db.flush()
        return {"filename": filename, "status": "ok", "chunks": len(chunks)}

    except Exception as e:
        document.status = "error"
        document.error_message = str(e)
        db.add(document)
        await db.flush()
        return {"filename": filename, "status": "error", "error": str(e)}


@router.post("/upload", summary="上传文档（支持多文件）")
async def upload_documents(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """上传一个或多个文档到知识库（仅管理员）"""
    results = []
    for file in files:
        result = await _process_single_file(file, current_user, db)
        results.append(result)

    ok_count = sum(1 for r in results if r["status"] == "ok")
    return {
        "message": f"上传完成: {ok_count}/{len(results)} 个文件成功",
        "results": results,
    }


@router.get("/documents", response_model=DocumentListResponse, summary="文档列表")
async def get_document_list(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取知识库文档列表（分页）"""
    docs, total = await list_documents(db, page, page_size)
    items = [DocumentResponse.model_validate(d) for d in docs]
    return DocumentListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse, summary="文档详情")
async def get_document_detail(
    document_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取文档详情（含所有分块）"""
    doc = await get_document(db, document_id)
    return DocumentDetailResponse.model_validate(doc)


@router.delete("/documents/{document_id}", summary="删除文档")
async def remove_document(
    document_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除文档及其向量数据"""
    doc = await get_document(db, document_id)

    # 删除 ChromaDB 中的向量
    try:
        collection = get_global_collection()
        # 按 collection_name 过滤删除
        from sqlalchemy import select as sql_select
        result = await db.execute(
            sql_select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        chunks = result.scalars().all()
        chroma_ids = [c.chroma_id for c in chunks if c.chroma_id]
        if chroma_ids:
            collection.delete(ids=chroma_ids)
    except Exception:
        pass  # ChromaDB 操作失败不影响数据库删除

    doc = await delete_document(db, document_id)
    return {"message": f"文档 '{doc.filename}' 已删除"}


@router.post("/documents/{document_id}/reindex", summary="重新索引")
async def reindex_document(
    document_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """重新对文档进行分块和向量化"""
    from sqlalchemy import select as sql_select

    doc = await get_document(db, document_id)

    # 1. 先删除旧的向量和分块记录
    try:
        collection = get_global_collection()
        old_chunks_result = await db.execute(
            sql_select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        old_chunks = old_chunks_result.scalars().all()
        old_chroma_ids = [c.chroma_id for c in old_chunks if c.chroma_id]
        if old_chroma_ids:
            collection.delete(ids=old_chroma_ids)

        # 删除数据库中的旧分块
        for chunk in old_chunks:
            await db.delete(chunk)
        await db.flush()
    except Exception as e:
        doc.status = "error"
        doc.error_message = f"清理旧数据失败: {str(e)}"
        db.add(doc)
        await db.flush()
        return {"error": doc.error_message}

    # 2. 重新处理文档
    file_path = f"./data/uploads/{doc.file_hash}.{doc.file_type}"
    if not os.path.exists(file_path):
        doc.status = "error"
        doc.error_message = "原始文件已丢失，无法重索引"
        db.add(doc)
        await db.flush()
        return {"error": doc.error_message}

    try:
        # 提取文本
        text = extract_text_from_file(file_path, doc.file_type)
        text = clean_text(text)

        if not text.strip():
            doc.status = "error"
            doc.error_message = "文档内容为空"
            db.add(doc)
            await db.flush()
            return {"error": doc.error_message}

        # 分块
        chunks = split_text(text)

        # 重新向量化
        embeddings = get_embeddings()
        collection = get_global_collection()

        for i, chunk_text in enumerate(chunks):
            chunk_record = DocumentChunk(
                document_id=doc.id,
                chunk_index=i,
                content=chunk_text,
                char_count=len(chunk_text),
                chroma_id=f"{doc.collection_name}_{i}",
            )
            db.add(chunk_record)

            chunk_embedding = embeddings.embed_query(chunk_text)
            collection.add(
                ids=[f"{doc.collection_name}_{i}"],
                embeddings=[chunk_embedding],
                documents=[chunk_text],
                metadatas=[{
                    "document_id": str(doc.id),
                    "chunk_id": str(i),
                    "filename": doc.filename,
                    "file_type": doc.file_type,
                    "collection": doc.collection_name,
                }],
            )

        # 更新文档状态
        doc.status = "ready"
        doc.chunk_count = len(chunks)
        doc.error_message = None
        db.add(doc)
        await db.flush()

        return {"message": "重索引完成", "document": DocumentResponse.model_validate(doc)}

    except Exception as e:
        doc.status = "error"
        doc.error_message = f"重索引失败: {str(e)}"
        db.add(doc)
        await db.flush()
        return {"error": doc.error_message}


@router.get("/stats", response_model=KnowledgeStatsResponse, summary="知识库统计")
async def get_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取知识库统计信息"""
    stats = await get_knowledge_stats(db)
    return KnowledgeStatsResponse(**stats)
