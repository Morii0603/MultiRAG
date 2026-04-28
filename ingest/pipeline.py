import asyncio
import os
from dataclasses import dataclass

from .parser import parse_document
from .chunker import chunk_document
from .minio_client import upload_document
from indexer.vector_store import MilvusStore


@dataclass
class IngestResult:
    paper_id: str
    chunk_count: int
    minio_path: str


def ingest_document(file_path: str, collection_name: str | None = None) -> IngestResult:
    """摄取一篇文档：上传至 MinIO → 解析 → 切块 → 写入 Milvus。"""
    parsed = parse_document(file_path)
    paper_id = parsed.paper_id

    filename = os.path.basename(file_path)
    minio_path = upload_document(file_path, f"upload_documents/{paper_id}/{filename}")

    chunks = chunk_document(parsed)
    store = MilvusStore(collection_name=collection_name) if collection_name else MilvusStore()
    store.insert(chunks)

    return IngestResult(paper_id=paper_id, chunk_count=len(chunks), minio_path=minio_path)


async def ingest_document_async(file_path: str, collection_name: str | None = None) -> IngestResult:
    """异步摄取文档：将同步重计算/IO放到线程池，避免阻塞事件循环。"""
    parsed = await asyncio.to_thread(parse_document, file_path)
    paper_id = parsed.paper_id

    filename = os.path.basename(file_path)
    minio_path = await asyncio.to_thread(upload_document, file_path, f"upload_documents/{paper_id}/{filename}")

    chunks = await asyncio.to_thread(chunk_document, parsed)

    store = MilvusStore(collection_name=collection_name) if collection_name else MilvusStore()
    await asyncio.to_thread(store.insert, chunks)

    return IngestResult(paper_id=paper_id, chunk_count=len(chunks), minio_path=minio_path)
