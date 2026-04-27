import config
import requests
from typing import List, Dict



def embed_multimodal(content_list: List[Dict[str, str]]) -> list:
    '''
        content_list: 格式为 [
        {"text": "文本内容1"},
        {"image": "图片路径1"},
        {"image": "图片路径2"},
        {"text": "文本内容2"}
    ]
    '''
    api_key = config.EMBEDDING_API_KEY
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen3-vl-embedding",
        "input": {
            "contents": content_list
        },
        "parameters": {
            "enable_fusion": True,
            "dimension": 1024
        }
    }
    base_url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding"
    response = requests.post(base_url, headers=headers, json=data)
    if response.status_code == 200:
        response_json = response.json()
        embedding_vector = response_json["output"]["embeddings"][0]["embedding"]
        return embedding_vector
    else:
        raise Exception(f"Multimodal Embedding API error: {response.status_code} - {response.text}")



