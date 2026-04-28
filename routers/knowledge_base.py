from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_serializer
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Document, KnowledgeBase
from indexer.vector_store import MilvusStore

router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])


class CreateKBRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class KBResponse(BaseModel):
    id: int
    name: str
    collection_name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at")
    def serialize_created_at(self, v: datetime) -> str:
        return v.isoformat()


class DocumentResponse(BaseModel):
    id: int
    paper_id: str
    filename: str
    minio_path: str
    file_size: int
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at")
    def serialize_created_at(self, v: datetime) -> str:
        return v.isoformat()


@router.post("/", response_model=KBResponse)
def create_knowledge_base(req: CreateKBRequest, db: Session = Depends(get_db)):
    """创建知识库，同时创建对应的 Milvus collection"""
    existing = db.query(KnowledgeBase).filter(KnowledgeBase.name == req.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="知识库名称已存在")

    collection_name = f"kb_{uuid4().hex[:16]}"

    # 在 Milvus 中创建 collection
    store = MilvusStore(collection_name=collection_name)
    store.client.release_collection(collection_name)

    kb = KnowledgeBase(
        name=req.name,
        collection_name=collection_name,
        description=req.description,
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb


@router.delete("/{kb_id}")
def delete_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    """删除知识库，同时删除对应的 Milvus collection 和 MinIO 文档"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")

    # 删除 Milvus collection
    store = MilvusStore(collection_name=kb.collection_name)
    store.client.release_collection(kb.collection_name)
    store.client.drop_collection(kb.collection_name)

    db.delete(kb)
    db.commit()
    return {"message": "知识库已删除"}


@router.get("/", response_model=list[KBResponse])
def list_knowledge_bases(db: Session = Depends(get_db)):
    """列举所有知识库"""
    return db.query(KnowledgeBase).order_by(KnowledgeBase.created_at.desc()).all()


@router.get("/{kb_id}/documents", response_model=list[DocumentResponse])
def list_documents(kb_id: int, db: Session = Depends(get_db)):
    """列举某个知识库下的所有文档"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return db.query(Document).filter(Document.knowledge_base_id == kb_id).order_by(Document.created_at.desc()).all()
