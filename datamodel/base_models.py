from pydantic import BaseModel
from PIL import Image as PILImage
from typing import List

class TableItem(BaseModel):
    paper_id: str # 论文ID，文件哈希值
    table_id: str # 表格ID，论文ID + 模态 + 表格索引
    caption: str # 表格标题
    content: str  # Markdown格式

class ImageItem(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    paper_id: str # 论文ID，文件哈希值
    image_id: str # 图片ID，论文ID + 模态 + 图片索引
    caption: str # 图片标题
    image: PILImage.Image  # PIL Image对象

class ParsedDocument(BaseModel):
    paper_id: str
    tables: List[TableItem]
    images: List[ImageItem]
    plain_text: str

class Chunk(BaseModel):
    id: str
    paper_id: str
    modality: str
    content: str
    section: str
    embedding: List[float]
    image_url: str = None
    score: float = None

