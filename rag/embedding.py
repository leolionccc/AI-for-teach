from typing import List

import httpx

from app.core.config import settings


class DashScopeEmbeddingClient:
    """
    DashScope / 阿里百炼 text-embedding-v4 向量客户端

    使用 OpenAI 兼容接口：
    POST https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings
    """

    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        self.model = settings.EMBEDDING_MODEL
        self.base_url = settings.EMBEDDING_BASE_URL.rstrip("/")
        self.dimension = settings.EMBEDDING_DIMENSION

    def _embedding_url(self) -> str:
        if self.base_url.endswith("/embeddings"):
            return self.base_url

        return f"{self.base_url}/embeddings"

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成向量

        text-embedding-v4 批量建议每次不超过 10 条。
        """
        if not self.api_key:
            raise ValueError("未配置 DASHSCOPE_API_KEY")

        if not texts:
            return []

        url = self._embedding_url()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "input": texts,
            "dimensions": self.dimension,
            "encoding_format": "float",
        }

        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            raise ValueError(
                f"Embedding 调用失败，状态码：{response.status_code}，响应：{response.text}"
            )

        data = response.json()

        items = data.get("data", [])
        items = sorted(items, key=lambda x: x.get("index", 0))

        return [item["embedding"] for item in items]

    def embed_query(self, query: str) -> List[float]:
        """
        查询文本向量
        """
        vectors = self.embed_texts([query])

        if not vectors:
            return []

        return vectors[0]

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        文档片段向量
        """
        result = []
        batch_size = 10

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            result.extend(self.embed_texts(batch))

        return result