
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import AcceleratorDevice, AcceleratorOptions
from typing import List
from datamodel import ParsedDocument, TableItem, ImageItem
import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"  # 设置 Hugging Face 镜像（可选）
# 初始化PDF管道选项

def hash_file(file_path: str) -> str:
    """计算文件的SHA256哈希值，作为唯一标识符"""
    import hashlib

    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()



def parse_document(file_path: str) -> ParsedDocument:
    """
    从文档中提取表格、图片以及纯文本内容。

    Args:
        file_path: 文档路径 (支持 PDF, DOCX, PPTX, HTML, 图片等)

    Returns:
        ParsedDocument: 提取的论文文档内容
    """

    paper_id = hash_file(file_path) 
    pipeline_options = PdfPipelineOptions(
        do_formula_enrichment=True,
        generate_picture_images=True,
        images_scale=2.0,
        accelerator_options=AcceleratorOptions(
            device=AcceleratorDevice.AUTO,  
            # device=AcceleratorDevice.AUTO,  # 或者让库自动检测（优先CUDA）
            num_threads=4,  # 根据你的CPU核心数调整
        )
    )

    # 2. 解析文档
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    result = converter.convert(file_path)
    doc = result.document

    tables: List[TableItem] = []
    images: List[ImageItem] = []

    # 3. 提取表格
    for idx, table in enumerate(doc.tables):
        caption = table.caption_text(doc=doc)
        markdown_content = table.export_to_markdown(doc=doc)  # 将表格内容转换为Markdown格式
        tables.append(TableItem(
            paper_id=paper_id,
            table_id=f"{paper_id}_table_{idx}",
            caption=caption,
            content=markdown_content,
        ))

    # 4. 提取图片
    for idx, picture in enumerate(doc.pictures):

        caption = picture.caption_text(doc=doc)
        image = picture.get_image(doc=doc)  # 获取PIL Image对象
        images.append(ImageItem(
            paper_id=paper_id,
            image_id=f"{paper_id}_img_{idx}",
            caption=caption,
            image=image,
        ))

    # 5. 提取纯文本（整个文档的纯文本内容）
    # docling 的 Document 对象提供了 export_to_text() 或 .text 属性
    plain_text = doc.export_to_markdown()  


    return ParsedDocument(
        paper_id=paper_id,
        tables=tables,
        images=images,
        plain_text=plain_text
    )


# ------------------- 使用示例 -------------------
if __name__ == "__main__":
    # 替换为你的文档路径（支持本地或URL）
    example_file = "12906_2025_Article_5142.pdf"   # 或者 "https://arxiv.org/pdf/2401.12345.pdf"
    
    # 如果文件不存在，可以尝试使用一个公开的PDF测试
    # example_file = "https://arxiv.org/pdf/2401.12345.pdf"
    
    parsed_doc = parse_document(example_file)
    print(f"提取到 {len(parsed_doc.tables)} 个表格，{len(parsed_doc.images)} 张图片")

    with open("extracted_text.md", "w", encoding="utf-8") as f:
        f.write(parsed_doc.plain_text)