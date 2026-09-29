"""混合检索零件：BM25、RRF 融合、可注入 / CrossEncoder / 词重叠重排序。

向量检索擅长语义相近，但对罕见专有名词、错误拼写的「字面命中」弱。
BM25 按词频打分，正好补这一面。两边名次用 RRF 合成，不必把余弦分和 BM25 分硬齐到同一量纲。

重排序优先级：set_rerank_fn > CrossEncoder（bge-reranker）> 查询词重叠。
测试可注入打分函数或假模型；默认不下载，加载失败回退词重叠。
"""

from __future__ import annotations

import inspect
import logging
import math
import os
import re
import threading
from collections import Counter
from collections.abc import Callable, Sequence
from typing import Any

from app.config import Settings

logger = logging.getLogger(__name__)

TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")

RerankFn = Callable[[str, list[str]], list[float]]

_injected_rerank: RerankFn | None = None
_cross_encoder: Any | None = None
_cross_encoder_failed = False
_cross_encoder_lock = threading.Lock()


def set_rerank_fn(fn: RerankFn | None) -> None:
    global _injected_rerank
    _injected_rerank = fn


def get_rerank_fn() -> RerankFn | None:
    return _injected_rerank


def set_cross_encoder(model: Any | None) -> None:
    """测试注入带 predict / compute_score 的假模型；None 表示清掉。"""
    global _cross_encoder, _cross_encoder_failed
    _cross_encoder = model
    _cross_encoder_failed = False


def reset_cross_encoder() -> None:
    set_cross_encoder(None)
    global _cross_encoder_failed
    _cross_encoder_failed = False


def _as_float_list(scores: Any, expected: int) -> list[float]:
    if hasattr(scores, "tolist"):
        scores = scores.tolist()
    if isinstance(scores, (int, float)):
        if expected == 1:
            return [float(scores)]
        raise ValueError("重排序只返回了一个分数")
    values = [float(item) for item in scores]
    if len(values) != expected:
        raise ValueError(f"重排序条数不匹配 ({len(values)} != {expected})")
    return values


def cross_encoder_scores(query: str, documents: list[str], model: Any) -> list[float]:
    """sentence-transformers.CrossEncoder 用 predict；FlagEmbedding 用 compute_score。"""
    pairs = [(query, doc) for doc in documents]
    if hasattr(model, "predict"):
        scores = model.predict(pairs)
    elif hasattr(model, "compute_score"):
        scores = model.compute_score(pairs)
    else:
        raise AttributeError("重排序模型既没有 predict 也没有 compute_score")
    return _as_float_list(scores, len(documents))


def _cached_rerank_dir(model_name: str) -> str | None:
    """Hugging Face 缓存里已有该模型时返回本地目录，避免再 HEAD Hub。"""
    if not model_name:
        return None
    if os.path.isdir(model_name):
        return model_name
    try:
        from huggingface_hub import try_to_load_from_cache
        from huggingface_hub.file_download import _CACHED_NO_EXIST

        cached = try_to_load_from_cache(repo_id=model_name, filename="config.json")
        if cached is None or cached is _CACHED_NO_EXIST:
            return None
        return os.path.dirname(str(cached))
    except Exception:
        return None


def _apply_hub_offline_env(enabled: bool) -> dict[str, str | None]:
    keys = ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")
    previous = {key: os.environ.get(key) for key in keys}
    if enabled:
        for key in keys:
            os.environ[key] = "1"
    return previous


def _restore_hub_offline_env(previous: dict[str, str | None]) -> None:
    for key, value in previous.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def _load_cross_encoder(model_name: str, *, local_files_only: bool) -> Any:
    """加载 CrossEncoder。

    bge-reranker 不是 sentence-transformers 仓库，没有 modules.json。
    传 Hub id 且允许联网时，ST 每次都会 HEAD huggingface.co/.../modules.json。
    有本地缓存时必须传本地目录 + local_files_only，并临时打开 HF 离线环境变量。
    """
    from sentence_transformers import CrossEncoder

    kwargs: dict[str, Any] = {}
    try:
        params = inspect.signature(CrossEncoder.__init__).parameters
    except (TypeError, ValueError):
        params = {}
    if "local_files_only" in params:
        kwargs["local_files_only"] = local_files_only
    if "model_kwargs" in params:
        kwargs["model_kwargs"] = {"local_files_only": local_files_only}
    elif "automodel_args" in params:
        kwargs["automodel_args"] = {"local_files_only": local_files_only}
    if "tokenizer_kwargs" in params:
        kwargs["tokenizer_kwargs"] = {"local_files_only": local_files_only}
    if "processor_kwargs" in params:
        kwargs["processor_kwargs"] = {"local_files_only": local_files_only}
    if "config_kwargs" in params:
        kwargs["config_kwargs"] = {"local_files_only": local_files_only}

    previous = _apply_hub_offline_env(local_files_only)
    try:
        return CrossEncoder(model_name, **kwargs)
    finally:
        _restore_hub_offline_env(previous)


def get_or_load_cross_encoder(settings: Settings | None) -> Any | None:
    """已注入则直接用；否则按配置懒加载。失败记一次，之后不再试。"""
    global _cross_encoder, _cross_encoder_failed
    if _cross_encoder is not None:
        return _cross_encoder
    if _cross_encoder_failed or settings is None or not settings.rerank_enabled:
        return None
    if settings.app_env == "test" and not settings.rerank_download:
        return None

    with _cross_encoder_lock:
        if _cross_encoder is not None:
            return _cross_encoder
        if _cross_encoder_failed:
            return None
        try:
            cached_dir = _cached_rerank_dir(settings.rerank_model)
            source = cached_dir or settings.rerank_model
            local_only = cached_dir is not None or not settings.rerank_download
            _cross_encoder = _load_cross_encoder(source, local_files_only=local_only)
            logger.info("重排序模型已加载: %s", source)
            return _cross_encoder
        except Exception as exc:
            _cross_encoder_failed = True
            logger.warning("重排序模型加载失败，回退词重叠: %s", exc)
            return None


def tokenize(text: str) -> list[str]:
    """英文按词；连续汉字拆成单字 + 双字，便于 BM25 打到词组。"""
    tokens: list[str] = []
    for raw in TOKEN_RE.findall((text or "").lower()):
        if _CJK_RE.search(raw) and len(raw) > 1:
            chars = list(raw)
            tokens.extend(chars)
            tokens.extend(raw[i : i + 2] for i in range(len(raw) - 1))
        else:
            tokens.append(raw)
    return tokens


def bm25_scores(
    query_tokens: Sequence[str],
    docs_tokens: Sequence[Sequence[str]],
    *,
    k1: float = 1.5,
    b: float = 0.75,
) -> list[float]:
    """标准 BM25。query 或语料为空时返回全 0。"""
    n = len(docs_tokens)
    if n == 0 or not query_tokens:
        return [0.0] * n

    df: Counter[str] = Counter()
    lengths: list[int] = []
    for tokens in docs_tokens:
        lengths.append(len(tokens))
        df.update(set(tokens))
    avgdl = (sum(lengths) / n) if n else 0.0

    idf: dict[str, float] = {}
    for term in set(query_tokens):
        freq = df.get(term, 0)
        idf[term] = math.log(1.0 + (n - freq + 0.5) / (freq + 0.5))

    scores: list[float] = []
    query_tf = Counter(query_tokens)
    for tokens, dl in zip(docs_tokens, lengths):
        tf = Counter(tokens)
        denom_len = k1 * (1.0 - b + b * (dl / avgdl if avgdl else 0.0))
        score = 0.0
        for term, qtf in query_tf.items():
            term_tf = tf.get(term, 0)
            if term_tf == 0:
                continue
            score += idf[term] * qtf * (term_tf * (k1 + 1.0)) / (term_tf + denom_len)
        scores.append(score)
    return scores


def rrf_fuse(
    ranked_lists: Sequence[Sequence[dict]],
    *,
    k: int = 60,
    id_field: str = "chunk_id",
) -> list[dict]:
    """倒数排名融合。同一文档出现在多路里会累加 1/(k+rank)。"""
    k = max(k, 1)
    merged: dict[str, dict] = {}
    rrf: dict[str, float] = {}
    for hits in ranked_lists:
        for rank, hit in enumerate(hits, start=1):
            chunk_id = str(hit.get(id_field) or "")
            if not chunk_id:
                continue
            rrf[chunk_id] = rrf.get(chunk_id, 0.0) + 1.0 / (k + rank)
            if chunk_id not in merged:
                merged[chunk_id] = dict(hit)
    ordered = sorted(
        merged.values(),
        key=lambda item: rrf.get(str(item.get(id_field)), 0.0),
        reverse=True,
    )
    for item in ordered:
        item["rrf_score"] = rrf.get(str(item.get(id_field)), 0.0)
        item["score"] = item["rrf_score"]
    return ordered


def overlap_scores(query: str, documents: list[str]) -> list[float]:
    """查询词覆盖率：命中的查询 token 数 / 查询 token 数。"""
    query_set = set(tokenize(query))
    if not query_set:
        return [0.0] * len(documents)
    scores: list[float] = []
    for text in documents:
        tokens = set(tokenize(text))
        scores.append(len(query_set & tokens) / len(query_set))
    return scores


def _score_hits(
    query: str, documents: list[str], settings: Settings | None
) -> list[float]:
    if _injected_rerank is not None:
        return _injected_rerank(query, documents)
    model = get_or_load_cross_encoder(settings)
    if model is not None:
        return cross_encoder_scores(query, documents, model)
    return overlap_scores(query, documents)


def rerank_hits(
    query: str,
    hits: list[dict],
    *,
    top_n: int | None = None,
    settings: Settings | None = None,
) -> list[dict]:
    """注入函数 > CrossEncoder > 词重叠。失败则保持融合顺序。"""
    if not hits:
        return []
    documents = [str(hit.get("content") or "") for hit in hits]
    try:
        scores = _score_hits(query, documents, settings)
        if len(scores) != len(hits):
            raise ValueError(f"重排序条数不匹配 ({len(scores)} != {len(hits)})")
    except Exception as exc:
        logger.warning("重排序失败，使用融合顺序: %s", exc)
        return hits[:top_n] if top_n is not None else hits
    for hit, score in zip(hits, scores):
        hit["rerank_score"] = float(score)
        hit["score"] = float(score)
    ranked = sorted(
        hits, key=lambda item: item.get("rerank_score") or 0.0, reverse=True
    )
    if top_n is not None:
        return ranked[:top_n]
    return ranked
