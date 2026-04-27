import config
import tiktoken
from typing import List
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from datamodel import ImageItem, TableItem, Chunk, ParsedDocument
from .embedder import embed_multimodal
from .minio_client import upload_image



# 初始化 tiktoken 编码器（与 OpenAI 模型兼容）
_tiktoken_encoder = tiktoken.get_encoding("cl100k_base")



def chunk_text(
    paper_id: str,
    markdown_text: str,
    prepend_section_title: bool = True,
) -> List[Chunk]:
    """对论文 Markdown 文本进行层级切分。

    1. MarkdownHeaderTextSplitter 按 ## 标题粗切为章节
    2. RecursiveCharacterTextSplitter 对每个章节内容细切
    3. 可选在每段文本前加入章节标题作为结构上下文
    """
    headers_to_split_on = [("##", "section")]

    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )
    section_docs = md_splitter.split_text(markdown_text)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.TEXT_CHUNK_SIZE,
        chunk_overlap=config.TEXT_CHUNK_OVERLAP,
        length_function=lambda text: len(_tiktoken_encoder.encode(text)),
        separators=["\n\n", "\n", ". ", "。", " ", ""],
        
    )

    chunks: List[Chunk] = []
    idx = 0

    for doc in section_docs:
        section_title = doc.metadata.get("section", "").strip()

        sub_docs = text_splitter.split_text(doc.page_content)

        for sub in sub_docs:
            sub = sub.strip()
            if not sub:
                continue

            content = f"{section_title}\n{sub}" if prepend_section_title and section_title else sub
            embedding = embed_multimodal([{"text": content}])  # 使用多模态接口获取文本向量
            chunks.append(Chunk(
                id=f"{paper_id}_text_{idx}",
                paper_id=paper_id,
                modality="text",
                content=content,
                section=section_title,
                embedding=embedding,
            ))
            idx += 1

    return chunks




def chunk_images(images: List[ImageItem]) -> List[Chunk]:
    """将图片列表转换为 Chunk 列表，上传至 MinIO 并向量化"""
    chunks: List[Chunk] = []
    for img in images:
        content_list = []
        if img.caption:
            content_list.append({"text": img.caption})
        image_url = upload_image(img.image, f"imgs/{img.image_id}.png")
        content_list.append({"image": image_url})
        embedding = embed_multimodal(content_list)

        chunks.append(Chunk(
            id=img.image_id,
            paper_id=img.paper_id,
            modality="image",
            content=img.caption,
            section="",
            embedding=embedding,

        ))
    return chunks

def chunk_tables(tables: List[TableItem]) -> List[Chunk]:
    """将表格列表转换为 Chunk 列表，并向量化"""
    chunks: List[Chunk] = []
    for table in tables:
        embedding = embed_multimodal([{"text": f"{table.caption}\n{table.content}"}])
        chunks.append(Chunk(
            id=table.table_id,
            paper_id=table.paper_id,
            modality="table",
            content=table.content,
            section="",
            embedding=embedding,
        ))
    return chunks

def chunk_document(document: ParsedDocument) -> List[Chunk]:
    """对论文 Markdown 文本进行切分，返回文本块列表"""
    text_chunks = chunk_text(
        paper_id=document.paper_id,
        markdown_text=document.plain_text,
        prepend_section_title=True,
    )
    image_chunks = chunk_images(document.images)
    table_chunks = chunk_tables(document.tables)
    return text_chunks + image_chunks + table_chunks