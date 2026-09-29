"""Token 用量：contextvar 打点 + 独立 session 落库 + 按用户汇总费用。

失败只打日志，不打断问答。没拿到官方 usage 时按字符估算。
"""

from __future__ import annotations

import contextvars
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import Settings, get_settings
from app.models.usage import ModelPricing, ModelTrace

logger = logging.getLogger(__name__)

_trace_ctx: contextvars.ContextVar[dict[str, str] | None] = contextvars.ContextVar(
    "model_trace_ctx", default=None
)
_session_factory: async_sessionmaker[AsyncSession] | None = None

DEFAULT_PRICING = {
    "qwen-plus": {"input_price_per_1k": 0.0008, "output_price_per_1k": 0.002, "currency": "CNY"},
    "qwen-turbo": {"input_price_per_1k": 0.0003, "output_price_per_1k": 0.0006, "currency": "CNY"},
    "text-embedding-v3": {"input_price_per_1k": 0.0005, "output_price_per_1k": 0.0, "currency": "CNY"},
}


def set_session_factory(factory: async_sessionmaker[AsyncSession] | None) -> None:
    global _session_factory
    _session_factory = factory


def set_trace_context(
    *,
    request_id: str | None = None,
    user_id: str = "",
    session_id: str = "",
    stage: str = "chat",
) -> None:
    _trace_ctx.set(
        {
            "request_id": request_id or uuid.uuid4().hex[:12],
            "user_id": user_id or "",
            "session_id": session_id or "",
            "stage": stage,
        }
    )


def clear_trace_context() -> None:
    _trace_ctx.set(None)


def set_trace_stage(stage: str) -> None:
    ctx = _trace_ctx.get()
    if ctx is not None:
        ctx["stage"] = stage


def get_trace_context() -> dict[str, str] | None:
    return _trace_ctx.get()


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, (len(text) + 1) // 2)


def parse_usage(data: dict | None, prompt: str, completion: str) -> tuple[int, int, int]:
    usage = (data or {}).get("usage") or {}
    prompt_tokens = int(usage.get("prompt_tokens") or 0) or estimate_tokens(prompt)
    completion_tokens = int(usage.get("completion_tokens") or 0) or estimate_tokens(completion)
    total = int(usage.get("total_tokens") or 0) or (prompt_tokens + completion_tokens)
    return prompt_tokens, completion_tokens, total


async def record_usage(
    *,
    stage: str | None = None,
    model: str | None = None,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    latency_ms: int | None = None,
    success: bool = True,
    error: str | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
    request_id: str | None = None,
) -> None:
    ctx = _trace_ctx.get() or {}
    user_id = user_id or ctx.get("user_id") or None
    if not user_id:
        return
    factory = _session_factory
    if factory is None:
        return
    prompt_tokens = int(prompt_tokens or 0)
    completion_tokens = int(completion_tokens or 0)
    row = ModelTrace(
        request_id=request_id or ctx.get("request_id"),
        user_id=user_id,
        session_id=session_id or ctx.get("session_id") or None,
        stage=stage or ctx.get("stage") or "chat",
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        latency_ms=latency_ms,
        success=success,
        error=(error or "")[:500] or None,
    )
    try:
        async with factory() as db:
            db.add(row)
            await db.commit()
    except Exception as exc:
        logger.warning("写入用量失败: %s", exc)


async def record_text_call(
    *,
    stage: str,
    model: str | None,
    prompt: str = "",
    completion: str = "",
    usage_payload: dict | None = None,
    latency_ms: int | None = None,
    success: bool = True,
    error: str | None = None,
) -> None:
    prompt_tokens, completion_tokens, _ = parse_usage(usage_payload, prompt, completion)
    await record_usage(
        stage=stage,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        success=success,
        error=error,
    )


class UsageTimer:
    def __init__(self, stage: str, model: str | None = None):
        self.stage = stage
        self.model = model
        self._started = time.perf_counter()

    def latency_ms(self) -> int:
        return int((time.perf_counter() - self._started) * 1000)

    async def finish(
        self,
        prompt: str = "",
        completion: str = "",
        usage_payload: dict | None = None,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        await record_text_call(
            stage=self.stage,
            model=self.model,
            prompt=prompt,
            completion=completion,
            usage_payload=usage_payload,
            latency_ms=self.latency_ms(),
            success=success,
            error=error,
        )


async def seed_model_pricing(db: AsyncSession, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    pricing: dict[str, dict[str, Any]] = dict(DEFAULT_PRICING)
    if settings.llm_model and settings.llm_model not in pricing:
        pricing[settings.llm_model] = {
            "input_price_per_1k": 0.0008,
            "output_price_per_1k": 0.002,
            "currency": "CNY",
        }
    for model, values in pricing.items():
        row = (
            await db.execute(select(ModelPricing).where(ModelPricing.model == model))
        ).scalar_one_or_none()
        if row:
            row.input_price_per_1k = float(values["input_price_per_1k"])
            row.output_price_per_1k = float(values["output_price_per_1k"])
            row.currency = values.get("currency", "CNY")
        else:
            db.add(
                ModelPricing(
                    model=model,
                    input_price_per_1k=float(values["input_price_per_1k"]),
                    output_price_per_1k=float(values["output_price_per_1k"]),
                    currency=values.get("currency", "CNY"),
                )
            )


async def get_usage_summary(
    db: AsyncSession,
    user_id: str,
    session_id: str | None = None,
    days: int = 30,
) -> dict:
    cutoff = datetime.now() - timedelta(days=days)
    conds = [ModelTrace.user_id == user_id, ModelTrace.created_at >= cutoff]
    if session_id:
        conds.append(ModelTrace.session_id == session_id)

    total_row = (
        await db.execute(
            select(
                func.count(),
                func.coalesce(func.sum(ModelTrace.prompt_tokens), 0),
                func.coalesce(func.sum(ModelTrace.completion_tokens), 0),
                func.coalesce(func.avg(ModelTrace.latency_ms), 0),
            ).where(*conds)
        )
    ).one()
    total_calls = int(total_row[0] or 0)
    total_prompt = int(total_row[1] or 0)
    total_completion = int(total_row[2] or 0)
    avg_latency_ms = round(float(total_row[3] or 0), 1)

    stage_rows = (
        await db.execute(
            select(
                ModelTrace.stage,
                func.count(),
                func.coalesce(func.sum(ModelTrace.prompt_tokens), 0),
                func.coalesce(func.sum(ModelTrace.completion_tokens), 0),
            )
            .where(*conds)
            .group_by(ModelTrace.stage)
        )
    ).all()
    by_stage = [
        {
            "stage": stage,
            "calls": int(calls),
            "prompt_tokens": int(prompt_tok),
            "completion_tokens": int(comp_tok),
        }
        for stage, calls, prompt_tok, comp_tok in stage_rows
    ]

    model_rows = (
        await db.execute(
            select(
                ModelTrace.model,
                func.count(),
                func.coalesce(func.sum(ModelTrace.prompt_tokens), 0),
                func.coalesce(func.sum(ModelTrace.completion_tokens), 0),
            )
            .where(*conds)
            .group_by(ModelTrace.model)
        )
    ).all()
    prices = {
        item.model: item
        for item in (await db.execute(select(ModelPricing))).scalars().all()
    }
    total_cost = 0.0
    by_model = []
    for model, calls, prompt_tok, comp_tok in model_rows:
        price = prices.get(model)
        if price:
            cost = (
                float(prompt_tok) / 1000 * price.input_price_per_1k
                + float(comp_tok) / 1000 * price.output_price_per_1k
            )
        else:
            cost = 0.0
        total_cost += cost
        by_model.append({"model": model, "calls": int(calls), "cost_cny": round(cost, 6)})

    return {
        "days": days,
        "total_calls": total_calls,
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "total_tokens": total_prompt + total_completion,
        "total_cost_cny": round(total_cost, 6),
        "avg_latency_ms": avg_latency_ms,
        "by_stage": by_stage,
        "by_model": by_model,
    }
