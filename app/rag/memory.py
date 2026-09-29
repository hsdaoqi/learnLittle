"""记忆压缩：窗口外旧对话做成增量里程碑摘要。

对齐原项目 memory_compressor：
- 消息总数超过阈值，且距上次摘要后新增足够多，才压缩
- 保留最近 keep_recent 条原文，更早的送给 LLM 和已有摘要融合
- 失败保留旧摘要，不打断问答

原项目用 msg_count - last_message_id 当间隔，把自增 ID 和条数混了。
这里改成统计 last_message_id 之后的消息条数。
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.models.chat import ChatMessage, ChatSummary
from app.rag.token_budget import TokenCounter

logger = logging.getLogger(__name__)

SUMMARY_PROMPT = """你是一个对话摘要助手。请阅读以下信息，生成一段简洁的结构化摘要。

## 已有的历史摘要
{existing_summary}

## 新增的对话片段（需要融合到摘要中）
{new_messages}

## 要求
1. 融合已有摘要和新对话，生成新的完整摘要
2. 重点保留以下类型的信息：
   - **关键决策**：用户做了什么技术/业务决策
   - **用户偏好**：用户表达过的喜好、习惯、要求
   - **未完成任务**：对话中提到但尚未完成的事项
   - **重要事实**：用户提供的关键信息
   - **上下文延续**：可能需要跨轮次引用的信息
3. 摘要长度控制在 500 字以内
4. 使用中文
5. 仅输出摘要文本，不要加任何前缀或解释"""

SummaryFn = Callable[[str], Awaitable[str]]

_injected: SummaryFn | None = None


def set_summary_fn(fn: SummaryFn | None) -> None:
    global _injected
    _injected = fn


def get_summary_fn() -> SummaryFn | None:
    return _injected


def truncate_summary(summary: str, max_tokens: int) -> str:
    text = (summary or "").strip()
    if not text:
        return ""
    tokens = TokenCounter.count(text)
    if tokens <= max_tokens:
        return text
    ratio = max_tokens / max(1, tokens)
    max_chars = int(len(text) * ratio)
    truncated = text[:max_chars]
    last_period = max(
        truncated.rfind("。"), truncated.rfind("."), truncated.rfind("\n")
    )
    if last_period > len(truncated) // 2:
        truncated = truncated[: last_period + 1]
    return truncated.strip()


def format_messages_for_summary(messages: list[Any], max_chars: int = 300) -> str:
    lines: list[str] = []
    for msg in messages:
        if isinstance(msg, dict):
            role = msg.get("role") or ""
            content = msg.get("content") or ""
        else:
            role = getattr(msg, "role", "") or ""
            content = getattr(msg, "content", "") or ""
        label = (
            "用户"
            if role == "user"
            else "助手"
            if role == "assistant"
            else role or "未知"
        )
        lines.append(f"[{label}]: {content[:max_chars]}")
    return "\n\n".join(lines)


def build_summary_prompt(existing_summary: str, new_messages: list[Any]) -> str:
    return SUMMARY_PROMPT.format(
        existing_summary=existing_summary.strip() or "（暂无历史摘要）",
        new_messages=format_messages_for_summary(new_messages),
    )


async def get_summary(db: AsyncSession, session_id: str) -> ChatSummary | None:
    return (
        await db.execute(
            select(ChatSummary).where(ChatSummary.session_id == session_id)
        )
    ).scalar_one_or_none()


async def update_summary(
    db: AsyncSession, session_id: str, summary_text: str, last_message_id: int
) -> ChatSummary:
    existing = await get_summary(db, session_id)
    token_count = TokenCounter.count(summary_text)
    if existing:
        existing.summary_text = summary_text
        existing.last_message_id = last_message_id
        existing.version += 1
        existing.token_count = token_count
        await db.flush()
        await db.refresh(existing)
        return existing
    row = ChatSummary(
        session_id=session_id,
        summary_text=summary_text,
        last_message_id=last_message_id,
        version=1,
        token_count=token_count,
    )
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


async def _complete_summary(prompt: str, settings: Settings) -> str:
    from app.services.usage_service import UsageTimer, set_trace_stage

    set_trace_stage("summary")
    if _injected is not None:
        timer = UsageTimer("summary", settings.llm_model)
        try:
            text = (await _injected(prompt)).strip()
            await timer.finish(prompt, text)
            return text
        except Exception as exc:
            await timer.finish(prompt, "", success=False, error=str(exc))
            raise
    if not settings.llm_api_key:
        return ""
    from app.rag.llm import complete_openai_compatible

    return (await complete_openai_compatible(prompt, settings)).strip()


async def check_and_summarize(
    db: AsyncSession, session_id: str, settings: Settings
) -> ChatSummary | None:
    """消息足够多时压缩窗口外旧对话。失败返回已有摘要，不抛给主流程。"""
    try:
        if not settings.memory_summarize_enabled:
            return await get_summary(db, session_id)

        msg_count = (
            await db.execute(
                select(func.count(ChatMessage.id)).where(
                    ChatMessage.session_id == session_id
                )
            )
        ).scalar() or 0
        if msg_count < settings.memory_summarize_threshold:
            return await get_summary(db, session_id)

        existing = await get_summary(db, session_id)
        existing_text = existing.summary_text if existing else ""
        last_id = existing.last_message_id if existing else 0

        new_count = (
            await db.execute(
                select(func.count(ChatMessage.id)).where(
                    ChatMessage.session_id == session_id,
                    ChatMessage.id > last_id,
                )
            )
        ).scalar() or 0
        if new_count < settings.memory_min_summary_interval:
            return existing

        compress_messages = list(
            (
                await db.execute(
                    select(ChatMessage)
                    .where(
                        ChatMessage.session_id == session_id,
                        ChatMessage.id > last_id,
                    )
                    .order_by(ChatMessage.id.asc())
                )
            )
            .scalars()
            .all()
        )
        keep_recent = max(settings.memory_keep_recent, 0)
        if len(compress_messages) <= keep_recent:
            return existing
        to_compress = (
            compress_messages[:-keep_recent] if keep_recent else compress_messages
        )

        prompt = build_summary_prompt(existing_text, to_compress)
        new_summary = await _complete_summary(prompt, settings)
        if not new_summary:
            return existing
        new_summary = truncate_summary(new_summary, settings.memory_summary_max_tokens)
        if not new_summary:
            return existing
        return await update_summary(db, session_id, new_summary, to_compress[-1].id)
    except Exception as exc:
        logger.warning("摘要检查/生成失败（不影响主流程）: %s", exc)
        try:
            return await get_summary(db, session_id)
        except Exception:
            return None
