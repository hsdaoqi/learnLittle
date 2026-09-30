"""问答用的 LLM 流式客户端。

设计：
- 测试可 set_llm_stream() 注入假模型，不打外网
- 配了 LLM_API_KEY 则走 OpenAI 兼容 /chat/completions（DashScope / vLLM 都行）
- 都没有时返回 None，由 chat_service 把本地拼接答案切片推出去
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator, Callable

from app.config import Settings

logger = logging.getLogger(__name__)

LLMStream = Callable[[str], AsyncIterator[str]]

_injected: LLMStream | None = None


def set_llm_stream(fn: LLMStream | None) -> None:
    global _injected
    _injected = fn


def get_llm_stream() -> LLMStream | None:
    return _injected


def _history_section(history: str, summary: str = "") -> str:
    parts: list[str] = []
    summary_text = (summary or "").strip()
    if summary_text:
        parts.append(f"[历史对话摘要]\n{summary_text}")
    history_text = (history or "").strip()
    if history_text:
        parts.append(f"近期对话：\n{history_text}")
    if not parts:
        return ""
    return "\n\n".join(parts) + "\n\n"


def build_rewrite_prompt(
    question: str,
    hits: list[dict],
    *,
    used_retrieval: bool = True,
    history: str = "",
    summary: str = "",
) -> str:
    history_block = _history_section(history, summary)
    if not used_retrieval:
        return (
            f"{history_block}"
            "用户问题：\n"
            f"{question}\n\n"
            "系统判断这个问题与用户知识库、笔记相关性低，没有检索资料。"
            "请结合近期对话当作普通对话简短回答。不要编造用户文档里的内容。"
        )
    if not hits:
        return (
            f"{history_block}"
            "用户问题：\n"
            f"{question}\n\n"
            "当前没有检索到任何资料。请明确告诉用户：知识库和笔记里没有相关内容，"
            "建议先上传文档或换一个更具体的问题。不要编造事实。"
        )

    blocks = []
    for i, hit in enumerate(hits, start=1):
        kind = "笔记" if hit.get("source") == "note" else "知识库"
        header = hit.get("filename") or "未命名"
        section = hit.get("section_title") or ""
        if section:
            header = f"{header} / {section}"
        blocks.append(f"[{i}] [{kind}] {header}\n{(hit.get('content') or '').strip()}")
    context = "\n\n".join(blocks)
    return (
        "你是学习助手。只根据下列检索资料回答用户问题。"
        "如果资料不足以回答，就说资料不够，不要编造。\n"
        "回答用简洁中文，必要时引用资料编号 [1]、[2]。\n"
        "用户用「它 / 那个 / 刚才」指代时，结合近期对话理解，不要丢掉上一轮实体。\n\n"
        f"{history_block}"
        f"资料：\n{context}\n\n"
        f"用户问题：\n{question}"
    )


async def stream_openai_compatible(
    prompt: str, settings: Settings
) -> AsyncIterator[str]:
    """调用 OpenAI 兼容的流式 chat/completions。"""
    import httpx

    from app.services.usage_service import UsageTimer

    timer = UsageTimer("chat", settings.llm_model)
    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.llm_model,
        "stream": True,
        "stream_options": {"include_usage": True},
        "messages": [{"role": "user", "content": prompt}],
        "enable_thinking": False,
    }
    parts: list[str] = []
    usage_payload: dict | None = None
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", url, headers=headers, json=payload
            ) as resp:
                if resp.status_code >= 400:
                    body = (await resp.aread()).decode("utf-8", errors="replace")[:300]
                    raise RuntimeError(f"LLM HTTP {resp.status_code}: {body}")
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if not data or data == "[DONE]":
                        continue
                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    if chunk.get("usage"):
                        usage_payload = chunk
                    delta = (chunk.get("choices") or [{}])[0].get("delta") or {}
                    text = delta.get("content") or ""
                    if text:
                        parts.append(text)
                        yield text
        await timer.finish(prompt, "".join(parts), usage_payload)
    except Exception as exc:
        await timer.finish(
            prompt, "".join(parts), usage_payload, success=False, error=str(exc)
        )
        raise


async def complete_openai_compatible(
    prompt: str,
    settings: Settings,
    *,
    enable_thinking: bool = False,
    timeout: float = 30.0,
) -> str:
    """非流式 chat/completions，给 HyDE / 分类 / 计划这种短补全用。

    enable_thinking 默认关。分类器和计划不要跟前端深度思考走同一套开关。
    """
    import httpx

    from app.services.usage_service import UsageTimer, get_trace_context

    ctx = get_trace_context() or {}
    timer = UsageTimer(ctx.get("stage") or "complete", settings.llm_model)
    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.llm_model,
        "stream": False,
        "messages": [{"role": "user", "content": prompt}],
        "enable_thinking": bool(enable_thinking),
    }
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            body = resp.text[:300]
            raise RuntimeError(f"LLM HTTP {resp.status_code}: {body}")
        data = resp.json()
        message = (data.get("choices") or [{}])[0].get("message") or {}
        text = (message.get("content") or "").strip()
        await timer.finish(prompt, text, data)
        return text
    except Exception as exc:
        await timer.finish(prompt, "", success=False, error=str(exc))
        raise


async def iter_llm_tokens(
    question: str,
    hits: list[dict],
    settings: Settings,
    *,
    used_retrieval: bool = True,
    history: str = "",
    summary: str = "",
) -> AsyncIterator[str]:
    """统一出口：注入模型 > 真实 API > 无模型（空迭代，调用方自行降级）。"""
    prompt = build_rewrite_prompt(
        question,
        hits,
        used_retrieval=used_retrieval,
        history=history,
        summary=summary,
    )
    if _injected is not None:
        from app.services.usage_service import UsageTimer

        timer = UsageTimer("chat", settings.llm_model)
        parts: list[str] = []
        try:
            async for token in _injected(prompt):
                parts.append(token)
                yield token
            await timer.finish(prompt, "".join(parts))
        except Exception as exc:
            await timer.finish(prompt, "".join(parts), success=False, error=str(exc))
            raise
        return
    if settings.llm_api_key:
        async for token in stream_openai_compatible(prompt, settings):
            yield token
        return
    return
