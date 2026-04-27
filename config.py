from dotenv import load_dotenv
import os
load_dotenv(verbose=True)
# ========== LLM 模型配置 ==========
LLM_MODEL = "qwen3.6-plus"  # 使用的语言模型
LLM_API_KEY = os.getenv("LLM_API_KEY")  # 语言模型 API Key
LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # OpenAI API Base URL

# ========== 切块配置 ==========
TEXT_CHUNK_SIZE = 1000
TEXT_CHUNK_OVERLAP = 150

# ========== Embedding 模型配置 ==========
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY")  # Embedding API Key


# ========== Milvus 向量数据库配置 ==========
MILVUS_URI = "http://localhost:19530"  # Milvus 服务地址
MILVUS_TOKEN = ""  # Milvus 认证 token
DOC_COLLECTION_NAME = "test"  # Milvus 集合名称


# ========== MinIO 配置 ==========
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")  # MinIO 服务地址
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = "knowledge-base"
MINIO_SECURE = False



RERANK_API_KEY = os.getenv("RERANK_API_KEY")  # 重排序 API Key

DENSE_TOP_K = 15  # 向量检索返回的文档数量
SPARSE_TOP_K = 15  # BM25 检索返回的文档数量
RRF_TOP_K = 15  # RRF 融合后返回的文档数量
RERANK_TOP_K = 10  # 重排序后返回的文档数量

