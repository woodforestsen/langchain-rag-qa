"""RAG 管道单元测试"""

import pytest


# ===== 文本分块测试 =====

@pytest.mark.asyncio
async def test_chunker_basic():
    """测试基本中文文本分块"""
    from app.rag.chunker import split_text

    text = "这是一个测试句子。这是第二个句子。这是第三个句子。"
    chunks = split_text(text)

    assert len(chunks) >= 1
    assert all(isinstance(c, str) for c in chunks)
    assert all(len(c) > 0 for c in chunks)


@pytest.mark.asyncio
async def test_chunker_short_text():
    """测试短文本分块"""
    from app.rag.chunker import split_text

    text = "短文本"
    chunks = split_text(text)

    assert len(chunks) == 1
    assert chunks[0] == "短文本"


@pytest.mark.asyncio
async def test_chunker_long_text():
    """测试长文本分块"""
    from app.rag.chunker import split_text

    # 生成约 2000 字的长文本
    text = "这是一个测试句子。" * 200
    chunks = split_text(text)

    assert len(chunks) > 1
    # 每个块不应超过设定大小太多
    for chunk in chunks:
        assert len(chunk) <= 600  # chunk_size=500 + 一些容差


@pytest.mark.asyncio
async def test_chunker_chinese_separators():
    """测试中文分隔符分块"""
    from app.rag.chunker import split_text

    text = "第一段。\n\n第二段，包含信息。\n第三行内容；第四部分。"
    chunks = split_text(text)

    assert len(chunks) >= 1
    combined = "".join(chunks)
    assert "第一段" in combined


@pytest.mark.asyncio
async def test_chunker_empty_text():
    """测试空文本"""
    from app.rag.chunker import split_text

    chunks = split_text("")
    assert isinstance(chunks, list)


# ===== 引用提取测试 =====

@pytest.mark.asyncio
async def test_citation_extraction():
    """测试来源引用提取"""
    from app.rag.citations import extract_citations

    response = "根据资料，商品很好【来源1】。价格实惠【来源2】【来源3】。"
    indices = extract_citations(response)

    assert 1 in indices
    assert 2 in indices
    assert 3 in indices
    assert len(indices) == 3


@pytest.mark.asyncio
async def test_citation_single():
    """测试单个来源引用"""
    from app.rag.citations import extract_citations

    response = "答案是【来源1】。"
    indices = extract_citations(response)

    assert indices == [1]


@pytest.mark.asyncio
async def test_citation_no_markers():
    """测试无来源标记"""
    from app.rag.citations import extract_citations

    response = "这个商品不错，但没找到具体信息。"
    indices = extract_citations(response)

    assert len(indices) == 0


@pytest.mark.asyncio
async def test_citation_duplicate_removal():
    """测试重复来源去重"""
    from app.rag.citations import extract_citations

    response = "【来源1】...【来源1】...【来源2】...【来源1】"
    indices = extract_citations(response)

    assert indices == [1, 2]


@pytest.mark.asyncio
async def test_parse_sources():
    """测试解析LLM响应中的实际引用"""
    from app.rag.citations import parse_sources_from_llm_response

    citations = [
        {"index": 1, "document_name": "a.pdf", "chunk_id": 1, "excerpt": "...", "score": 0.95},
        {"index": 2, "document_name": "b.pdf", "chunk_id": 2, "excerpt": "...", "score": 0.80},
        {"index": 3, "document_name": "c.pdf", "chunk_id": 3, "excerpt": "...", "score": 0.50},
    ]

    response = "答案是【来源1】【来源2】。"
    used = parse_sources_from_llm_response(response, citations)

    assert len(used) == 2
    assert used[0]["index"] == 1
    assert used[1]["index"] == 2


@pytest.mark.asyncio
async def test_parse_sources_fallback():
    """测试无引用标记时的回退策略"""
    from app.rag.citations import parse_sources_from_llm_response

    citations = [
        {"index": 1, "document_name": "a.pdf", "chunk_id": 1, "excerpt": "...", "score": 0.95},
        {"index": 2, "document_name": "b.pdf", "chunk_id": 2, "excerpt": "...", "score": 0.30},
    ]

    response = "答案是..."
    used = parse_sources_from_llm_response(response, citations)

    # 应回退到高分来源（>= 0.6）
    assert len(used) == 1
    assert used[0]["score"] >= 0.6


# ===== 文档格式化测试 =====

@pytest.mark.asyncio
async def test_format_docs_for_context():
    """测试文档上下文格式化"""
    from app.rag.retriever import format_docs_for_context

    chunks = [
        {
            "content": "商品A价格99元",
            "metadata": {"filename": "价格表.pdf"},
            "score": 0.92,
        },
        {
            "content": "商品A规格100ml",
            "metadata": {"filename": "规格表.pdf"},
            "score": 0.85,
        },
    ]

    context, citations = format_docs_for_context(chunks)

    assert len(citations) == 2
    assert citations[0]["score"] >= citations[1]["score"]
    assert "价格表" in context
    assert "规格表" in context
    assert citations[0]["excerpt"]  # excerpt 不为空


@pytest.mark.asyncio
async def test_format_docs_empty():
    """测试空块列表"""
    from app.rag.retriever import format_docs_for_context

    context, citations = format_docs_for_context([])

    assert context == ""
    assert citations == []


# ===== 自动标题生成测试 =====

@pytest.mark.asyncio
async def test_generate_auto_title_short():
    """测试短问题标题生成"""
    from app.services.chat_service import generate_auto_title

    title = await generate_auto_title("这个商品多少钱？")
    assert len(title) <= 10


@pytest.mark.asyncio
async def test_generate_auto_title_long():
    """测试长问题标题截断"""
    from app.services.chat_service import generate_auto_title

    long_question = "请问这个笔记本电脑的处理器型号是什么，内存多大，硬盘容量是多少，屏幕尺寸是多少？"
    title = await generate_auto_title(long_question)

    assert len(title) <= 33  # 30 + "..."
    assert title.endswith("...")


@pytest.mark.asyncio
async def test_generate_auto_title_newlines():
    """测试带换行的问题"""
    from app.services.chat_service import generate_auto_title

    question = "你好\n请问这个商品怎么样？"
    title = await generate_auto_title(question)

    assert "\n" not in title


# ===== LLM 工厂测试 =====

@pytest.mark.asyncio
async def test_get_llm_aliyun():
    """测试获取阿里云LLM实例"""
    from app.rag.llm_factory import get_llm
    from app.config import settings

    llm = get_llm(provider="aliyun", streaming=False)
    assert llm is not None
    assert hasattr(llm, "model_name")
    assert settings.ALIYUN_MODEL in (llm.model_name or "")


@pytest.mark.asyncio
async def test_get_llm_unknown_provider():
    """测试未知提供商抛出异常"""
    from app.rag.llm_factory import get_llm
    import pytest as pt

    with pt.raises(ValueError):
        get_llm(provider="unknown_provider_xyz")
