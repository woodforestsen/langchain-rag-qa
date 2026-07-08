"""RAG Prompt 模板 - 中文电商场景优化"""

from langchain_core.prompts import ChatPromptTemplate

# 系统级 RAG 提示词
RAG_SYSTEM_TEMPLATE = """你是一个专业的电商客服助手，负责回答用户关于平台商品的问题。

## 核心规则
1. 直接回答用户问题，不要描述你检索到了什么、没检索到什么。
2. 当参考文档有相关内容时，基于文档回答并标注来源编号【来源N】。
3. 参考文档为空或不相关时，用你自己的知识直接回答，无需解释原因。
4. 商品规格、价格、优惠等关键信息优先引用原文数据。
5. 中文回答，简洁明了。"""

# 带对话历史的 RAG 用户提示词模板
RAG_USER_TEMPLATE = """## 参考文档
{context}

## 对话历史
{chat_history}

## 用户问题
{question}

请根据以上参考文档回答用户的问题："""

# 独立问题重写提示词（用于结合对话历史）
QUERY_REWRITE_TEMPLATE = """请根据以下对话历史，将用户的后续问题改写为一个独立、完整的问题，方便在知识库中检索。

## 对话历史
{chat_history}

## 用户后续问题
{question}

## 改写后的独立问题："""


def get_rag_prompt() -> ChatPromptTemplate:
    """获取 RAG 对话提示词模板"""
    return ChatPromptTemplate.from_messages([
        ("system", RAG_SYSTEM_TEMPLATE),
        ("human", RAG_USER_TEMPLATE),
    ])


def get_query_rewrite_prompt() -> ChatPromptTemplate:
    """获取查询重写提示词模板"""
    return ChatPromptTemplate.from_messages([
        ("system", "你是一个帮助改写搜索引擎查询的助手。请将模糊的后续问题改写成清晰独立的问题。"),
        ("human", QUERY_REWRITE_TEMPLATE),
    ])
