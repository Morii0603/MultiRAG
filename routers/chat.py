import logging
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

from agent import RagAgent

_log = logging.getLogger(__name__)

router = APIRouter()

agent = RagAgent()


class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    session_id: str = Field(default_factory=lambda: uuid4().hex, description="会话 ID，不传则自动新建")
    collection_name: str | None = Field(default=None, description="知识库集合名称，不传则使用默认")


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """发送消息并获取 Agent 回复。同一 session_id 会累积上下文。"""
    _log.info("session=%s coll=%s message=%s", req.session_id, req.collection_name, req.message[:120])
    reply = agent.chat(req.message, session_id=req.session_id, collection_name=req.collection_name)
    return ChatResponse(session_id=req.session_id, reply=reply)
