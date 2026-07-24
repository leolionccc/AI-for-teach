import re
from pathlib import Path
from typing import Dict, List, Optional

import chromadb
from sqlalchemy.orm import Session

from app.models.material import Material
from app.rag.embedding import DashScopeEmbeddingClient


BACKEND_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BACKEND_DIR / "data" / "chroma_db"

CHROMA_DIR.mkdir(parents=True, exist_ok=True)

embedding_client = DashScopeEmbeddingClient()

chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = chroma_client.get_or_create_collection(
    name="course_materials_v4"
)


def split_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    """
    将长文本切分成 chunks
    """
    if not text:
        return []

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    chunks = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= length:
            break

        start = max(end - overlap, 0)

    return chunks


def get_material_by_id(db: Session, material_id: int) -> Optional[Material]:
    return db.query(Material).filter(Material.id == material_id).first()


def delete_material_vectors(material_id: int) -> None:
    """
    删除某个资料已有向量
    """
    material_id_str = str(material_id)

    result = collection.get(
        where={
            "material_id": material_id_str
        }
    )

    ids = result.get("ids", [])

    if ids:
        collection.delete(ids=ids)


def build_material_index(db: Session, material_id: int) -> Dict:
    """
    为单个资料构建向量索引
    """
    material = get_material_by_id(db, material_id)

    if not material:
        raise ValueError("资料不存在")

    if not material.content:
        raise ValueError("资料没有解析内容，无法构建知识库")

    delete_material_vectors(material_id)

    chunks = split_text(material.content)

    if not chunks:
        raise ValueError("资料内容为空，无法切分")

    embeddings = embedding_client.embed_documents(chunks)

    ids = []
    metadatas = []

    for index, chunk in enumerate(chunks):
        chunk_id = f"material_{material.id}_chunk_{index}"

        ids.append(chunk_id)
        metadatas.append(
            {
                "material_id": str(material.id),
                "material_name": material.name,
                "file_type": material.file_type,
                "chunk_index": index,
            }
        )

    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    return {
        "material_id": material.id,
        "material_name": material.name,
        "chunk_count": len(chunks),
        "embedding_model": "text-embedding-v4",
    }


def build_all_material_indexes(db: Session) -> Dict:
    """
    为所有有解析内容的资料构建索引
    """
    materials = (
        db.query(Material)
        .filter(Material.content.isnot(None))
        .order_by(Material.id.asc())
        .all()
    )

    results = []
    success_count = 0
    fail_count = 0

    for material in materials:
        try:
            result = build_material_index(db, material.id)

            results.append(
                {
                    "material_id": material.id,
                    "material_name": material.name,
                    "status": "success",
                    "chunk_count": result["chunk_count"],
                    "error": None,
                }
            )

            success_count += 1

        except Exception as e:
            results.append(
                {
                    "material_id": material.id,
                    "material_name": material.name,
                    "status": "fail",
                    "chunk_count": 0,
                    "error": str(e),
                }
            )

            fail_count += 1

    return {
        "success_count": success_count,
        "fail_count": fail_count,
        "results": results,
    }


def search_knowledge(query: str, top_k: int = 5) -> List[Dict]:
    """
    从 Chroma 中检索相关课程片段
    """
    if not query:
        return []

    query_embedding = embedding_client.embed_query(query)

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    items = []

    for index, document in enumerate(documents):
        metadata = metadatas[index] if index < len(metadatas) else {}
        distance = distances[index] if index < len(distances) else None

        items.append(
            {
                "material_id": metadata.get("material_id", ""),
                "material_name": metadata.get("material_name", ""),
                "chunk_index": metadata.get("chunk_index", 0),
                "content": document,
                "distance": distance,
            }
        )

    return items


def build_rag_context(search_results: List[Dict]) -> str:
    """
    将检索结果拼接成 Prompt 上下文
    """
    if not search_results:
        return "当前知识库中没有检索到相关课程资料。"

    context_parts = []

    for index, item in enumerate(search_results, start=1):
        context_parts.append(
            f"【资料片段 {index}】\n"
            f"资料名称：{item.get('material_name')}\n"
            f"片段序号：{item.get('chunk_index')}\n"
            f"内容：\n{item.get('content')}\n"
        )

    return "\n".join(context_parts)


def build_recommendations(search_results: List[Dict]) -> List[Dict]:
    """
    根据检索结果生成资料推荐
    """
    seen = set()
    recommendations = []

    for item in search_results:
        material_id = item.get("material_id")
        material_name = item.get("material_name")

        if not material_id or material_id in seen:
            continue

        seen.add(material_id)

        recommendations.append(
            {
                "material_id": material_id,
                "material_name": material_name,
            }
        )

    return recommendations