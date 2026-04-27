import asyncio

from .parser import parse_document
from .chunker import chunk_document
from indexer.vector_store import MilvusStore

def ingest_document(file_path: str, collection_name: str | None = None):
    """摄取一篇文档：解析 → 切块 → 写入 Milvus。

    Args:
        file_path: 文档路径 (PDF, DOCX, PPTX 等)
        collection_name: Milvus 集合名称
    """
    parsed = parse_document(file_path)
    chunks = chunk_document(parsed)
    store = MilvusStore(collection_name=collection_name) if collection_name else MilvusStore()
    store.insert(chunks)



async def ingest_document_async(file_path: str, collection_name: str | None = None):
    """异步摄取文档：将同步重计算/IO放到线程池，避免阻塞事件循环。"""

    parsed = await asyncio.to_thread(parse_document, file_path)
    chunks = await asyncio.to_thread(chunk_document, parsed)

    store = MilvusStore(collection_name=collection_name) if collection_name else MilvusStore()
    await asyncio.to_thread(store.insert, chunks)
