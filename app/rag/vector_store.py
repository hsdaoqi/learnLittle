"""Chroma 向量库：知识库与笔记切片的写入、检索、删除。

两个 collection 分开存，避免笔记和文档切片互相污染过滤条件。
测试可注入 client（如 chromadb.EphemeralClient），避免写磁盘。
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from app.config import Settings
from app.core.failed_response import BusinessError, ErrorCode
from app.rag.embeddings import embed_texts
from app.rag.retriever import bm25_scores, rerank_hits, rrf_fuse, tokenize

logger = logging.getLogger(__name__)

CollectionName = Literal["rag", "notes"]

_service: VectorStoreService | None = None


class VectorStoreService:
    def __init__(self, settings: Settings, client: Any | None = None):
        self.settings = settings
        self._client = client
        self._rag = None
        self._notes = None
        self._dim_checked = False

    def _ensure(self):
        if self._rag is not None and self._notes is not None:
            return
        if self._client is None:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self._client = chromadb.PersistentClient(
                path=self.settings.chroma_persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        self._rag = self._client.get_or_create_collection(
            name=self.settings.chroma_collection_rag,
            metadata={"hnsw:space": "cosine"},
        )
        self._notes = self._client.get_or_create_collection(
            name=self.settings.chroma_collection_notes,
            metadata={"hnsw:space": "cosine"},
        )

    def _collection(self, name: CollectionName):
        self._ensure()
        return self._rag if name == "rag" else self._notes

    async def _check_dimension(self, probe: list[float]) -> None:
        """集合非空时，已存向量维度必须和当前模型输出一致。"""
        if self._dim_checked:
            return
        model_dim = len(probe)
        for name, col in (("rag", self._rag), ("notes", self._notes)):
            if col is None or col.count() == 0:
                continue
            stored = (col.get(limit=1, include=["embeddings"]) or {}).get("embeddings")
            if stored is None or len(stored) == 0:
                continue
            first = stored[0]
            stored_dim = first.shape[0] if hasattr(first, "shape") else len(first)
            if stored_dim != model_dim:
                raise BusinessError(
                    code=ErrorCode.EMBEDDING_DIM_MISMATCH,
                    http_status=500,
                    detail=(
                        f"集合 {name} 为 {stored_dim} 维，当前模型输出 {model_dim} 维。"
                        "请删除 data/chroma 后重新上传文档并保存笔记。"
                    ),
                )
        self._dim_checked = True

    async def upsert_chunks(
        self,
        *,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str],
        collection: CollectionName = "rag",
    ) -> None:
        if not documents:
            return
        target = self._collection(collection)
        embeddings = await embed_texts(documents, self.settings)
        await self._check_dimension(embeddings[0])
        target.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def _candidate_k(self, top_k: int) -> int:
        multiplier = max(self.settings.hybrid_candidate_multiplier, 1)
        cap = max(self.settings.hybrid_max_candidates, top_k)
        return min(max(top_k * multiplier, top_k), cap)

    def _format_hit(
        self,
        *,
        doc: str,
        meta: dict,
        collection: CollectionName,
        chroma_id: str = "",
        score: float = 0.0,
    ) -> dict:
        source = "note" if collection == "notes" else "knowledge"
        document_id = int(meta.get("document_id") or 0)
        note_id = meta.get("note_id") or ""
        chunk_index = int(meta.get("chunk_index") or 0)
        chunk_id = chroma_id or (
            f"{note_id}_{chunk_index}"
            if source == "note"
            else f"{document_id}_{chunk_index}"
        )
        return {
            "content": doc,
            "score": float(score),
            "source": source,
            "document_id": document_id,
            "note_id": note_id,
            "filename": meta.get("filename") or meta.get("title") or "",
            "section_title": meta.get("section_title") or "",
            "chunk_index": chunk_index,
            "chunk_id": chunk_id,
        }

    async def _vector_search(
        self,
        query: str,
        user_id: str,
        n_results: int,
        collection: CollectionName,
    ) -> list[dict]:
        target = self._collection(collection)
        if target.count() == 0:
            return []
        query_embedding = await embed_texts([query], self.settings)
        await self._check_dimension(query_embedding[0])
        n_results = min(max(n_results, 1), max(target.count(), 1))
        results = target.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where={"user_id": user_id},
            include=["documents", "metadatas", "distances"],
        )
        docs = (results.get("documents") or [[]])[0]
        metas = (results.get("metadatas") or [[]])[0]
        distances = (results.get("distances") or [[]])[0]
        ids = (results.get("ids") or [[]])[0]
        formatted: list[dict] = []
        for i, doc in enumerate(docs):
            distance = distances[i] if i < len(distances) else 1.0
            meta = metas[i] if i < len(metas) else {}
            chroma_id = ids[i] if i < len(ids) else ""
            formatted.append(
                self._format_hit(
                    doc=doc,
                    meta=meta,
                    collection=collection,
                    chroma_id=chroma_id,
                    score=1 - float(distance),
                )
            )
        return formatted

    def _bm25_search(
        self,
        query: str,
        user_id: str,
        top_k: int,
        collection: CollectionName,
    ) -> list[dict]:
        target = self._collection(collection)
        if target.count() == 0:
            return []
        found = target.get(
            where={"user_id": user_id},
            include=["documents", "metadatas"],
            limit=max(self.settings.bm25_max_docs, 1),
        )
        ids = found.get("ids") or []
        docs = found.get("documents") or []
        metas = found.get("metadatas") or []
        if not docs:
            return []
        scores = bm25_scores(
            tokenize(query),
            [tokenize(doc or "") for doc in docs],
            k1=self.settings.bm25_k1,
            b=self.settings.bm25_b,
        )
        hits: list[dict] = []
        for i, doc in enumerate(docs):
            if scores[i] <= 0:
                continue
            meta = metas[i] if i < len(metas) else {}
            chroma_id = ids[i] if i < len(ids) else ""
            hits.append(
                self._format_hit(
                    doc=doc,
                    meta=meta,
                    collection=collection,
                    chroma_id=chroma_id,
                    score=scores[i],
                )
            )
        hits.sort(key=lambda item: item.get("score") or 0, reverse=True)
        return hits[:top_k]

    def _maybe_rerank(
        self, query: str, hits: list[dict], top_k: int, enabled: bool
    ) -> list[dict]:
        if not hits:
            return []
        if enabled and self.settings.rerank_enabled:
            return rerank_hits(query, hits, top_n=top_k, settings=self.settings)
        return hits[:top_k]

    async def search(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
        collection: CollectionName = "rag",
        rerank: bool = True,
    ) -> list[dict]:
        """向量 + BM25，RRF 融合后再可选重排序。"""
        target = self._collection(collection)
        if target.count() == 0:
            return []
        candidate_k = self._candidate_k(top_k)
        vector_hits = await self._vector_search(query, user_id, candidate_k, collection)
        lexical_hits = self._bm25_search(query, user_id, candidate_k, collection)
        fused = rrf_fuse(
            [vector_hits, lexical_hits],
            k=self.settings.rrf_k,
        )
        return self._maybe_rerank(query, fused, top_k, rerank)

    async def compute_route_score(self, query: str, user_id: str) -> float:
        """当前用户知识库 + 笔记的 Top-1 余弦距离，越小越相关。

        只做向量 Top-1，不走 BM25 / HyDE / 重排序。两边都空或没有该用户的切片时返回 inf。
        """
        query = (query or "").strip()
        if not query:
            return float("inf")
        self._ensure()
        query_embedding = await embed_texts([query], self.settings)
        await self._check_dimension(query_embedding[0])

        best = float("inf")
        for name in ("rag", "notes"):
            target = self._collection(name)
            if target.count() == 0:
                continue
            results = target.query(
                query_embeddings=query_embedding,
                n_results=1,
                where={"user_id": user_id},
                include=["distances"],
            )
            distances = (results.get("distances") or [[]])[0]
            if distances:
                best = min(best, float(distances[0]))
        return best

    async def search_both(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
        rerank_query: str | None = None,
    ) -> list[dict]:
        """
        知识库与笔记各自混合检索，再 RRF 合成，最后重排序。
        query 用于向量/BM25 召回（可以是 HyDE 文本）；
        rerank_query 缺省等于 query，问答传入原问题以免假设句冲掉用户用词。
        """
        rag_hits = await self.search(query, user_id, top_k, "rag", rerank=False)
        note_hits = await self.search(query, user_id, top_k, "notes", rerank=False)
        fused = rrf_fuse([rag_hits, note_hits], k=self.settings.rrf_k)
        return self._maybe_rerank(rerank_query or query, fused, top_k, True)

    def delete_document(self, document_id: int | str) -> None:
        self._delete_by("rag", "document_id", str(document_id))

    def delete_note(self, note_id: str) -> None:
        self._delete_by("notes", "note_id", note_id)

    def _delete_by(self, collection: CollectionName, field: str, value: str) -> None:
        target = self._collection(collection)
        found = target.get(where={field: value}, include=[])
        ids = found.get("ids") or []
        if ids:
            target.delete(ids=ids)
            logger.info(
                "已删除向量: collection=%s %s=%s count=%s",
                collection,
                field,
                value,
                len(ids),
            )


def set_vector_store(service: VectorStoreService | None) -> None:
    global _service
    _service = service


def get_vector_store() -> VectorStoreService:
    if _service is None:
        raise RuntimeError("向量库未初始化：应在应用 lifespan 中 init_vector_store()")
    return _service


def init_vector_store(
    settings: Settings, client: Any | None = None
) -> VectorStoreService:
    global _service
    if _service is not None:
        return _service
    _service = VectorStoreService(settings, client=client)
    return _service


def close_vector_store() -> None:
    global _service
    _service = None
