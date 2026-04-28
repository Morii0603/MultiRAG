from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.database import _engine
from db.models import Base
from routers import chat, ingest, knowledge_base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=_engine)
    yield


app = FastAPI(title="RAG Agent Service", version="0.1.0", lifespan=lifespan)
app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(knowledge_base.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
