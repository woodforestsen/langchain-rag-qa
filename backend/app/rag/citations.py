"""引用解析 - 从 LLM 回答中提取【来源N】引用标记"""

import re


def extract_citations(answer_text: str) -> list[int]:
    """从回答文本中提取所有被引用的来源编号"""
    pattern = r'【来源(\d+)】'
    matches = re.findall(pattern, answer_text)
    return sorted(set(int(m) for m in matches))


def format_citation_markdown(answer_text: str, citations: list[dict]) -> str:
    """将来源引用格式化为 Markdown，方便前端渲染

    将【来源N】替换为可点击的引用链接样式
    """
    formatted = answer_text

    # 构建引用脚注
    if citations:
        footnotes = "\n\n---\n**📚 参考来源：**\n"
        for c in citations:
            score_pct = f"{c['score'] * 100:.0f}%"
            footnotes += (
                f"\n- **[{c['index']}] {c['document_name']}** "
                f"(相关度: {score_pct})\n"
                f"  > {c['excerpt']}\n"
            )
        formatted += footnotes

    return formatted


def parse_sources_from_llm_response(response: str, citations: list[dict]) -> list[dict]:
    """解析 LLM 响应中被实际使用的引用

    只返回在回答中被标注的引用来源
    """
    used_indices = extract_citations(response)
    used_sources = [c for c in citations if c["index"] in used_indices]

    # 如果 LLM 没有正确标注引用，但有检索结果，返回全部高相关度来源
    if not used_sources and citations:
        used_sources = [c for c in citations if c["score"] >= 0.6]

    return used_sources
