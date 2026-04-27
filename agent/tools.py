import contextvars

from langchain_core.tools import tool

import config
from ingest.minio_client import get_object_url
from retriever import hybrid_search

# 请求级别上下文变量，由 _execute_tools 在调用前注入
collection_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "collection_name", default=None
)


@tool
def search_knowledge_base(query: str):
    """检索知识库，返回相关文档片段（文本 + 图片）。调用此工具获取知识库内容后再作答。"""
    coll = collection_var.get() or config.DOC_COLLECTION_NAME
    chunks = hybrid_search(query, collection_name=coll)

    content_blocks: list[dict] = []
    text_parts: list[str] = []
    img_count = 0

    for i, chunk in enumerate(chunks):
        if chunk.modality == "text" and chunk.content:
            text_parts.append(
                f"[文献{i}] (section: {chunk.section or 'unknown'})\n{chunk.content}"
            )
        elif chunk.modality == "image" and img_count < 3:
            if chunk.content:
                content_blocks.append({
                    "type": "text",
                    "text": f"[图{img_count}] 标题: {chunk.content}",
                })
            try:
                url = get_object_url(f"imgs/{chunk.id}.png")
                content_blocks.append({
                    "type": "image_url",
                    "image_url": {"url": url},
                })
                img_count += 1
            except Exception:
                content_blocks.append({
                    "type": "text",
                    "text": f"[图{img_count}] 图片加载失败",
                })

    if text_parts:
        content_blocks.insert(0, {
            "type": "text",
            "text": "\n\n---\n\n".join(text_parts),
        })

    if not content_blocks:
        return "未找到相关文档，请告知用户知识库中暂无相关内容。"

    return content_blocks
