"""文本分块 - 中文优化的递归分块器"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """获取针对中文优化的文本分块器"""
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        # 分隔符按优先级：段落 → 换行 → 中文句号 → 感叹号 → 问号 → 分号 → 空格
        separators=[
            "\n\n",
            "\n",
            "。",
            "！",
            "？",
            "；",
            "，",
            " ",
            "",
        ],
        length_function=len,
        is_separator_regex=False,
    )


def split_text(text: str) -> list[str]:
    """将长文本分割为文档块"""
    splitter = get_text_splitter()
    chunks = splitter.split_text(text)
    return chunks
