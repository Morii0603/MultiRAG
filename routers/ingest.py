import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Document, KnowledgeBase
from ingest.pipeline import ingest_document_async

router = APIRouter()


@router.post("/ingest/")
async def ingest_document(
    file: UploadFile = File(...),
    knowledge_base_id: int = ...,
    db: Session = Depends(get_db),
):
    """上传文档至指定知识库：存 MinIO → 解析 → 切块 → 写入 Milvus → 记录到 MySQL"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    contents = await file.read()
    suffix = os.path.splitext(file.filename or "upload.pdf")[1]
    uploads_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=uploads_dir) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        result = await ingest_document_async(tmp_path, collection_name=kb.collection_name)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    doc = Document(
        knowledge_base_id=kb.id,
        paper_id=result.paper_id,
        filename=file.filename or "unknown",
        minio_path=result.minio_path,
        file_size=len(contents),
        chunk_count=result.chunk_count,
    )
    db.add(doc)
    db.commit()

    return {
        "message": "Document ingested successfully",
        "paper_id": result.paper_id,
        "chunk_count": result.chunk_count,
    }
