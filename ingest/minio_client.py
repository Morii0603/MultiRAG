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
