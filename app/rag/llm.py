"""辅助任务的非流式模型客户端；主聊天流由 LangChain ReAct 处理。"""

from app.config import Settings


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

    from app.ai_service.thinking import payload_thinking_fields
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
        **payload_thinking_fields(enable_thinking, settings),
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
