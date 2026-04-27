import config
from datamodel import Chunk
from typing import Dict, List

from ingest.embedder import embed_multimodal
from indexer.vector_store import MilvusStore
from retriever.reranker import rerank, vl_rerank
from ingest.minio_client import get_object_url


def rrf_fuse(dense_hits: List[Chunk], sparse_hits: List[Chunk], k: int = 60) -> List[Chunk]:
    dense_rank = {hit.id: idx for idx, hit in enumerate(dense_hits) if hit.id}
    sparse_rank = {hit.id: idx for idx, hit in enumerate(sparse_hits) if hit.id}

    merged_hits: Dict[str, Chunk] = {}
    for hit in dense_hits:
        if hit.id:
            merged_hits[hit.id] = hit
    for hit in sparse_hits:
        if hit.id and hit.id not in merged_hits:
            merged_hits[hit.id] = hit

    fused: List[Chunk] = []
    for hit_id, hit in merged_hits.items():
        d_rank = dense_rank.get(hit_id)
        s_rank = sparse_rank.get(hit_id)
        d_score = 1.0 / (k + d_rank + 1) if d_rank is not None else 0.0
        s_score = 1.0 / (k + s_rank + 1) if s_rank is not None else 0.0
        rrf_score = d_score + s_score

        fused.append(
            Chunk(
                id=hit_id,
                paper_id=hit.paper_id,
                modality=hit.modality,
                content=hit.content,
                section=hit.section,
                embedding=hit.embedding,
                score=rrf_score,
            )
        )

    fused.sort(key=lambda c: c.score if c.score is not None else 0.0, reverse=True)
    return fused[:config.RRF_TOP_K]


def _rerank_text_chunks(query: str, chunks: List[Chunk]) -> List[Chunk]:
    if not chunks:
        return []

    documents = [chunk.content or "" for chunk in chunks]
    scores = rerank(query, documents)
    for chunk, score in zip(chunks, scores):
        chunk.score = score

    chunks.sort(key=lambda c: c.score if c.score is not None else 0.0, reverse=True)
    return chunks[: config.RERANK_TOP_K]


def _rerank_image_chunks(query: str, chunks: List[Chunk]) -> List[Chunk]:
    if not chunks:
        return []

    documents = []
    for chunk in chunks:
        chunk.image_url = get_object_url(f"imgs/{chunk.id}.png")
        document = {"image": chunk.image_url}
        if chunk.content:
            document["text"] = chunk.content
        documents.append(document)

    scores = vl_rerank(query, documents)
    for chunk, score in zip(chunks, scores):
        chunk.score = score

    chunks.sort(key=lambda c: c.score if c.score is not None else 0.0, reverse=True)
    return chunks[: config.RERANK_TOP_K]


def hybrid_search(query: str, collection_name: str = config.DOC_COLLECTION_NAME) -> List[Chunk]:
    """双路混合检索：
    - 文本侧：Dense + BM25 -> RRF -> 文本 rerank
    - 图像侧：Dense + BM25 -> RRF -> VL rerank
    """

    store = MilvusStore(collection_name=collection_name)
    query_vector = embed_multimodal([{"text": query}])

    text_dense_hits = store.search_dense(query_vector, modality="text")
    text_sparse_hits = store.search_sparse(query, modality="text")
    text_chunks = rrf_fuse(dense_hits=text_dense_hits, sparse_hits=text_sparse_hits)
    text_chunks = _rerank_text_chunks(query, text_chunks)

    image_dense_hits = store.search_dense(query_vector, modality="image")
    image_sparse_hits = store.search_sparse(query, modality="image")
    image_chunks = rrf_fuse(dense_hits=image_dense_hits, sparse_hits=image_sparse_hits)
    image_chunks = _rerank_image_chunks(query, image_chunks)

    return text_chunks + image_chunks


