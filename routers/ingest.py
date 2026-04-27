import os
import tempfile

from fastapi import APIRouter, File, UploadFile

from ingest.pipeline import ingest_document_async

router = APIRouter()

@router.post("/ingest/")
async def ingest_document(file: UploadFile = File(...), collection_name: str = "default_collection"):
    contents = await file.read()
    suffix = os.path.splitext(file.filename or "upload.pdf")[1]
    uploads_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=uploads_dir) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        await ingest_document_async(tmp_path, collection_name=collection_name)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return {"message": "Document ingested successfully"}