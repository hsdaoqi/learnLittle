"""文本向量化。

优先级：测试注入 > Embedding API > 确定性哈希回退。

哈希回退保证无密钥时测试和离线检索仍能跑通。
配了密钥后向量维度由模型决定；换模型必须清空 Chroma 目录再重建。
"""

from __future__ import annotations

import hashlib
import logging
import math
import re
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from time import time

from app.config import Settings
from app.core.failed_response import BusinessError, ErrorCode

logger = logging.getLogger(__name__)

EmbedFn = Callable[[list[str]], Awaitable[list[list[float]]]]

_TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)

_injected: EmbedFn | None = None
_cache: OrderedDict[str, tuple[list[float], float]] = OrderedDict()


def set_embed_fn(fn: EmbedFn | None) -> None:
    global _injected
    _injected = fn


def get_embed_fn() -> EmbedFn | None:
    return _injected


def reset_embedding_cache() -> None:
    _cache.clear()


def hash_embed_text(text: str, dim: int = 64) -> list[float]:
    """确定性哈希向量：相近文本会共享部分 token 槽，已 L2 归一化。"""
    vector = [0.0] * dim
    tokens = _TOKEN_RE.findall((text or "").lower())
    if not tokens:
        tokens = ["_empty"]

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for i in range(0, min(len(digest), dim * 2), 2):
            idx = digest[i] % dim
            sign = 1.0 if digest[i + 1] % 2 == 0 else -1.0
            vector[idx] += sign

    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def hash_embed_texts(texts: list[str], dim: int = 64) -> list[list[float]]:
    return [hash_embed_text(t, dim) for t in texts]


# 兼容旧测试名
embed_text = hash_embed_text


def _backend_tag(settings: Settings) -> str:
    if _injected is not None:
        return "injected"
    if _embedding_api_key(settings):
        return f"api:{settings.embedding_model}"
    return f"hash:{settings.embedding_dim}"


def _cache_key(text: str, settings: Settings) -> str:
    raw = f"{_backend_tag(settings)}\0{text}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _embedding_api_key(settings: Settings) -> str:
    return (settings.embedding_api_key or settings.llm_api_key or "").strip()


def _embedding_base_url(settings: Settings) -> str:
    return (settings.embedding_base_url or settings.llm_base_url).rstrip("/")


async def embed_openai_compatible(
    texts: list[str],
    settings: Settings,
    api_key: str,
) -> list[list[float]]:
    """调用 OpenAI 兼容 /embeddings（DashScope compatible-mode / vLLM 都行）。"""
    import httpx

    url = _embedding_base_url(settings) + "/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": settings.embedding_model, "input": texts}
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        raise BusinessError(
            code=ErrorCode.EMBEDDING_CALL_FAILED,
            http_status=502,
            detail=str(exc),
        ) from exc
    if resp.status_code >= 400:
        body = resp.text[:300]
        raise BusinessError(
            code=ErrorCode.EMBEDDING_CALL_FAILED,
            http_status=502,
            detail=f"Embedding HTTP {resp.status_code}: {body}",
        )
    data = resp.json()

    items = list(data.get("data") or [])
    items.sort(key=lambda item: item.get("index", 0))
    vectors = [item.get("embedding") or [] for item in items]
    if len(vectors) != len(texts) or any(not vec for vec in vectors):
        raise BusinessError(
            code=ErrorCode.EMBEDDING_CALL_FAILED,
            http_status=502,
            detail="Embedding 返回条数或向量为空",
        )
    return vectors


async def _embed_batch(texts: list[str], settings: Settings) -> list[list[float]]:
    if _injected is not None:
        return await _injected(texts)
    api_key = _embedding_api_key(settings)
    if api_key:
        return await embed_openai_compatible(texts, settings, api_key)
    return hash_embed_texts(texts, settings.embedding_dim)


async def embed_texts(texts: list[str], settings: Settings) -> list[list[float]]:
    """带 LRU 缓存的批量向量化。缓存按文本 MD5 寻址，与 user_id 无关。"""
    if not texts:
        return []

    now = time()
    ttl = settings.embedding_cache_ttl_seconds
    max_entries = settings.embedding_cache_max_entries
    results: list[list[float] | None] = [None] * len(texts)
    missing_idx: list[int] = []
    missing_texts: list[str] = []

    for i, text in enumerate(texts):
        key = _cache_key(text, settings)
        cached = _cache.get(key)
        if cached and (now - cached[1]) < ttl:
            results[i] = cached[0]
            _cache.move_to_end(key)
        else:
            missing_idx.append(i)
            missing_texts.append(text)

    if missing_texts:
        new_vectors: list[list[float]] = []
        batch_size = max(settings.embedding_batch_size, 1)
        for start in range(0, len(missing_texts), batch_size):
            batch = missing_texts[start : start + batch_size]
            new_vectors.extend(await _embed_batch(batch, settings))
        for idx, text, vec in zip(missing_idx, missing_texts, new_vectors):
            results[idx] = vec
            key = _cache_key(text, settings)
            _cache[key] = (vec, now)
            _cache.move_to_end(key)
        while len(_cache) > max_entries:
            _cache.popitem(last=False)

    filled: list[list[float]] = []
    for vec in results:
        if vec is None:
            raise RuntimeError("embedding 结果缺失")
        filled.append(vec)
    return filled
