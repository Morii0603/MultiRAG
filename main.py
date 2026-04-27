from fastapi import FastAPI

from routers import ingest, chat

app = FastAPI(title="RAG Agent Service", version="0.1.0")
app.include_router(ingest.router)
app.include_router(chat.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
