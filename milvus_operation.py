from pymilvus import MilvusClient
# 连接到 Milvus 服务
client = MilvusClient(
   uri="http://localhost:19530", # 替换为实际服务地址
   token="root:Milvus" # 替换为实际身份验证信息
)
# 删除集合
client.drop_collection(collection_name="test")
print("集合已成功删除！")