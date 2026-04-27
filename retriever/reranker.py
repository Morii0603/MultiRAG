import config
import requests
from typing import List, Dict
# from datamodel import Chunk
def vl_rerank(query:str, documents:List[Dict[str,str]]) -> List[float] :
    '''
        query: 查询文本
        documents: 格式为 [
        {"text": "文本内容1"},
        {"image": "图片路径1"},
        {"image": "图片路径2"},
        {"text": "文本内容2"}
        返回相关性分数列表，与原documents顺序一致
    ]
    '''
    API_URL = "https://api.siliconflow.cn/v1/rerank"
    API_KEY = config.RERANK_API_KEY
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Qwen/Qwen3-VL-Reranker-8B",
        "query": query,
        "documents": documents
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    results = response.json().get("results", [])
    results = sorted(results, key=lambda x: x.get("index", 0))
    scores = [result.get("relevance_score", 0) for result in results]
    return scores
def rerank(query:str, documents:List[str]) -> List[float] :
    '''
        query: 查询文本
        documents: 文本列表
        返回相关性分数列表，与原documents顺序一致
    '''
    API_URL = "https://api.siliconflow.cn/v1/rerank"
    API_KEY = config.RERANK_API_KEY
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Qwen/Qwen3-Reranker-8B",
        "query": query,
        "documents": documents
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    results = response.json().get("results", [])
    results = sorted(results, key=lambda x: x.get("index", 0))
    scores = [result.get("relevance_score", 0) for result in results]
    return scores

