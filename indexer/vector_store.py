from typing import List,Literal
import config
from datamodel import Chunk
from pymilvus import (
    CollectionSchema,
    FieldSchema,
    MilvusClient,
    DataType,
    Function,
    FunctionType,
)


class MilvusStore:
    """Milvus 向量存储，支持 dense (embedding) + sparse (BM25) 双路检索。"""

    def __init__(self, collection_name: str = config.DOC_COLLECTION_NAME):
        self.client = MilvusClient(uri=config.MILVUS_URI, token=config.MILVUS_TOKEN)

        self.collection_name = collection_name 

        self._ensure_collection()

    def _ensure_collection(self):
        if self.client.has_collection(self.collection_name):
            self.client.load_collection(self.collection_name)
            return

        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=256), 
            FieldSchema(name="paper_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="modality", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535, enable_analyzer=True),
            FieldSchema(name="section", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="dense_vector", dtype=DataType.FLOAT_VECTOR, dim=1024),
            # BM25 函数输出字段不能是 nullable
            FieldSchema(name="sparse_vector", dtype=DataType.SPARSE_FLOAT_VECTOR),
        ]
        bm25_function = Function(
            name="bm25",
            function_type=FunctionType.BM25,
            input_field_names=["content"],
            output_field_names=["sparse_vector"],
        )
        schema = CollectionSchema(fields, "Document chunks — dense + BM25", functions=[bm25_function])

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
        )

        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="dense_vector",
            index_type="IVF_FLAT",
            metric_type="COSINE",
            params={"nlist": 128},
        )
        index_params.add_index(
            field_name="sparse_vector",
            index_type="SPARSE_INVERTED_INDEX",
            metric_type="BM25",
        )

        self.client.create_index(
            collection_name=self.collection_name,
            index_params=index_params,
        )
        self.client.load_collection(self.collection_name)

    def _hit_to_chunk(self, hit) -> Chunk:
        entity = hit.get("entity", {}) if isinstance(hit, dict) else {}

        return Chunk(
            id=hit.get("id") or entity.get("id"),
            paper_id=hit.get("paper_id") or entity.get("paper_id"),
            modality=hit.get("modality") or entity.get("modality"),
            content=hit.get("content") or entity.get("content"),
            section=hit.get("section") or entity.get("section"),
            embedding=[],
        )

    # ------------------------------------------------------------------
    # 写入
    # ------------------------------------------------------------------
    def insert(self, chunks: List[Chunk]):
        if not chunks:
            raise ValueError("No chunks to insert")

        rows = []
        for chunk in chunks:
            rows.append({
                "id": chunk.id,
                "paper_id": chunk.paper_id,
                "modality": chunk.modality,
                "content": chunk.content,
                "section": chunk.section,
                "dense_vector": chunk.embedding,
            })

        self.client.insert(collection_name=self.collection_name, data=rows)
        self.client.flush(collection_name=self.collection_name)

    # ------------------------------------------------------------------
    # Dense 检索
    # ------------------------------------------------------------------
    def search_dense(self, query_vector: List[float], modality: Literal["text", "image"] = "text") -> List[Chunk]:

        result = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            anns_field="dense_vector",
            search_params={"metric_type": "COSINE", "params": {"nprobe": 10}},
            limit=config.DENSE_TOP_K,
            output_fields=["id", "paper_id", "modality", "content", "section"],
            filter=f'modality == "{modality}"',
        )
        hits = result[0]
        return [self._hit_to_chunk(hit) for hit in hits]


    # ------------------------------------------------------------------
    # BM25 检索
    # ------------------------------------------------------------------
    def search_sparse(self, query_text: str, modality: Literal["text", "image"] = "text") -> List[Chunk]:

        result = self.client.search(
            collection_name=self.collection_name,
            data=[query_text],
            anns_field="sparse_vector",
            search_params={"metric_type": "BM25", "params": {}},
            limit=config.SPARSE_TOP_K,
            output_fields=["id", "paper_id", "modality", "content", "section"],
            filter=f'modality == "{modality}"',
        )
        hits = result[0]
        return [self._hit_to_chunk(hit) for hit in hits]
