import os
from io import BytesIO

from minio import Minio

import config


def get_minio_client() -> Minio:
    return Minio(
        config.MINIO_ENDPOINT,
        access_key=config.MINIO_ACCESS_KEY,
        secret_key=config.MINIO_SECRET_KEY,
        secure=config.MINIO_SECURE,
    )


def ensure_bucket():
    client = get_minio_client()
    if not client.bucket_exists(config.MINIO_BUCKET):
        client.make_bucket(config.MINIO_BUCKET)


def upload_document(file_path: str, object_name: str) -> str:
    """上传原始文档至 MinIO upload_documents 文件夹，返回对象路径"""
    ensure_bucket()
    client = get_minio_client()
    file_size = os.path.getsize(file_path)
    client.fput_object(config.MINIO_BUCKET, object_name, file_path)
    return object_name


def upload_image(image, object_name: str) -> str:
    """将 PIL 图片上传至 MinIO，返回预签名 URL"""
    client = get_minio_client()
    buf = BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    size = buf.getbuffer().nbytes
    client.put_object(
        config.MINIO_BUCKET,
        object_name,
        buf,
        size,
        content_type="image/png",
    )
    return client.presigned_get_object(config.MINIO_BUCKET, object_name)


def get_object_url(object_name: str) -> str:
    """获取 MinIO 对象的预签名 URL"""
    client = get_minio_client()
    return client.presigned_get_object(config.MINIO_BUCKET, object_name)
