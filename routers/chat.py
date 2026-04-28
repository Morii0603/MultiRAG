import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agent import RagAgent
from db.database import get_db
from db.models import KnowledgeBase

_log = logging.getLogger(__name__)

router = APIRouter()

agent = RagAgent()


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    session_id: str = Field(default_factory=lambda: uuid4().hex, description="会话 ID，不传则自动新建")
    knowledge_base_id: int | None = Field(default=None, description="知识库 ID")
    collection_name: str | None = Field(default=None, description="知识库集合名称，不传则使用默认")


class ChatResponse(BaseModel):
    session_id: str
    reply: str


def _resolve_collection_name(knowledge_base_id: int | None, collection_name: str | None, db: Session) -> str | None:
    if knowledge_base_id is not None:
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")
        return kb.collection_name
    return collection_name


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """发送消息并获取 Agent 回复。同一 session_id 会累积上下文。"""
    coll = _resolve_collection_name(req.knowledge_base_id, req.collection_name, db)
    _log.info("session=%s coll=%s message=%s", req.session_id, coll, req.message[:120])
    reply = agent.chat(req.message, session_id=req.session_id, collection_name=coll)
    return ChatResponse(session_id=req.session_id, reply=reply)
