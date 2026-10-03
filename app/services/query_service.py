"""Persist -> parallel RAG/memory -> routing graph -> persist -> maintenance."""

import asyncio
import hashlib
import json
import logging
from contextlib import aclosing

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError

from app.ai_service.chat_graph import stream_chat_graph
from app.ai_service.react_agent import get_react_streamer
from app.ai_service.sse_slot import acquire_sse_slot, release_sse_slot
from app.ai_service.thinking import resolve_agent_thinking
from app.core.task_runner import spawn_background_task
from app.models.chat import ChatMessage, ChatSession
from app.rag.chat_cache import invalidate_session_list, push_message
from app.rag.chat_history import build_agent_history, rag_context_text
from app.rag.hyde import generate_hyde
from app.rag.memory import check_and_summarize, get_summary
from app.rag.note_cards import visible_question
from app.rag.rag_route import RouteDecision, decide_retrieval
from app.rag.rag_summarize import summarize_hits
from app.rag.session_title import DEFAULT_TITLE, generate_session_title
from app.rag.vector_store import get_vector_store
from app.services import usage_service
from app.services.chat_service import (
    _add_message, _message_dump, create_session, get_session,
)

logger = logging.getLogger(__name__)


def _sse_data(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def compose_answer(
    question: str, hits: list[dict], *, used_retrieval: bool = True
) -> str:
    """本地降级回答：区分未检索、无命中和命中参考资料。"""
    if not used_retrieval:
        return (
            f"「{question}」看起来和你已有的知识库、笔记不太相关，这一轮没有检索资料。"
            "如果问的是文档里的内容，试着换更具体的关键词；闲聊的话可以直接继续。"
        )
    if not hits:
        return (
            "知识库和笔记里都没有检索到相关内容。"
            "请先上传文档或写笔记，或换一个更具体的问题。"
        )
    lines = [f"根据知识库和笔记，与「{question}」相关的内容如下：", ""]
    for i, hit in enumerate(hits, start=1):
        kind = "笔记" if hit.get("source") == "note" else "知识库"
        header = hit.get("filename") or "未命名"
        if hit.get("section_title"):
            header = f"{header} / {hit['section_title']}"
        lines.extend([f"[{i}] [{kind}] {header}", (hit.get("content") or "").strip(), ""])
    lines.append("以上为参考资料摘录。")
    return "\n".join(lines).strip()


def _key(user_id, key, role):
    if not key:
        return None
    return hashlib.sha256(f"{user_id}:{role}:{key}".encode()).hexdigest()


async def _load_memory(factory, session_id, before_id):
    async with factory() as db:
        rows = list((await db.execute(
            select(ChatMessage).where(
                ChatMessage.session_id == session_id, ChatMessage.id < before_id,
            ).order_by(ChatMessage.id)
        )).scalars().all())
        summary = await get_summary(db, session_id)
        return rows, summary.summary_text if summary else "", summary.last_message_id if summary else 0


async def _retrieve(question, user_id, top_k, settings):
    try:
        async with asyncio.timeout(settings.rag_timeout):
            decision = await decide_retrieval(question, user_id, settings)
            if not decision.retrieve:
                return [], [], decision
            query = await generate_hyde(question, user_id, settings) if settings.chat_hyde_enabled else question
            hits = await get_vector_store().search_both(query, user_id, top_k, rerank_query=question)
            context = await summarize_hits(question, hits, settings)
            return hits, context, decision
    except Exception:
        logger.warning("RAG 不可用，本轮继续 Agent", exc_info=True)
        return [], [], RouteDecision(False, float("inf"), "unavailable")


async def _update_title(factory, session_id, question, settings):
    async with factory() as db:
        session = await db.get(ChatSession, session_id)
        if not session or session.title_manual:
            return
        count = await db.scalar(select(func.count(ChatMessage.id)).where(
            ChatMessage.session_id == session_id, ChatMessage.role == "user",
        ))
        if count > settings.chat_auto_title_rounds:
            return
        previous_title = session.title
        user_id = session.user_id
    title = await generate_session_title(question, settings)
    async with factory() as db:
        await db.execute(update(ChatSession).where(
            ChatSession.id == session_id, ChatSession.title_manual.is_(False),
            ChatSession.title == previous_title,
        ).values(title=title))
        await db.commit()
    if settings.chat_cache_enabled:
        await invalidate_session_list(user_id)


async def _summarize(factory, session_id, settings):
    async with factory() as db:
        await check_and_summarize(db, session_id, settings)
        await db.commit()


async def stream_query(factory, user_id, data, settings):
    if not await acquire_sse_slot(user_id, settings):
        yield _sse_data({"type": "error", "content": "并发连接数已达上限，请稍后重试"})
        return
    raw = data.message.strip()
    question = visible_question(raw)
    user_key = _key(user_id, data.idempotency_key, "user")
    reply_key = _key(user_id, data.idempotency_key, "assistant")
    uncached = settings.model_copy(update={"chat_cache_enabled": False})
    try:
        async with factory() as db:
            existing = None
            if user_key:
                existing = await db.scalar(select(ChatMessage).where(
                    ChatMessage.idempotency_key == user_key,
                ))
            if existing:
                if existing.content != raw or (data.session_id and data.session_id != existing.session_id):
                    yield _sse_data({"type": "error", "content": "同一幂等键不能用于不同请求"})
                    return
                session = await get_session(db, user_id, existing.session_id)
                reply = await db.scalar(select(ChatMessage).where(
                    ChatMessage.idempotency_key == reply_key,
                ))
                yield _sse_data({"type": "meta", "session_id": session.id,
                                 "user_message": _message_dump(existing)})
                if reply:
                    yield _sse_data({"type": "response_replace", "content": reply.content})
                    yield _sse_data({"type": "done", "session_id": session.id,
                                     "answer": reply.content, "title": session.title,
                                     "assistant_message": _message_dump(reply), "replayed": True})
                else:
                    yield _sse_data({"type": "error", "content": "该请求已接收，请查看会话；为避免重复操作不会自动重放"})
                return
            session = (
                await get_session(db, user_id, data.session_id) if data.session_id
                else await create_session(db, user_id, DEFAULT_TITLE, uncached)
            )
            message = await _add_message(db, session.id, "user", raw, uncached, user_key)
            await db.commit()
            session_id = session.id
            message_id = message.id
            user_dump = _message_dump(message)
        if settings.chat_cache_enabled:
            await push_message(session_id, message, settings.chat_cache_buffer_size)
            await invalidate_session_list(user_id)
        usage_service.set_trace_context(user_id=user_id, session_id=session_id, stage="chat")
        yield _sse_data({"type": "meta", "session_id": session_id, "user_message": user_dump})
        yield _sse_data({"type": "thinking", "stage": "processing", "content": "正在准备上下文..."})
        rag, memory = await asyncio.gather(
            _retrieve(question, user_id, data.top_k, settings),
            _load_memory(factory, session_id, message_id),
        )
        hits, context_hits, decision = rag
        rows, summary, summarized_through = memory
        rag_text = rag_context_text(context_hits)
        history = build_agent_history(
            rows, settings, rag_text=rag_text, question=raw,
            summary=summary, summarized_through=summarized_through,
        )
        if rag_text:
            yield _sse_data({"type": "thinking", "stage": "rag",
                             "content": f"已检索到 {len(hits)} 个参考片段"})
        thinking = resolve_agent_thinking(
            data.enable_thinking, has_attachments=bool(data.attachment_ids), settings=settings,
        )
        if thinking.sse_notice():
            yield _sse_data(thinking.sse_notice())
        parts = []
        tools = []
        routing = {}
        stream = stream_chat_graph(
            raw, user_id, factory, settings, history=history, summary=summary,
            rag_context=rag_text, enable_thinking=thinking.applied,
            fallback_answer=compose_answer(question, context_hits, used_retrieval=decision.retrieve),
        )
        async with aclosing(stream):
            async for event in stream:
                kind = event.get("type")
                if kind == "routing":
                    routing = {key: value for key, value in event.items() if key != "type"}
                    continue
                if kind == "stream_done":
                    parts = [event.get("full_response") or ""]
                    continue
                if kind == "response":
                    parts.append(event.get("content") or "")
                elif kind == "response_replace":
                    parts = [event.get("content") or ""]
                elif kind == "tool_end":
                    tools.append({"name": event.get("name"),
                                  "status": "error" if event.get("error") else "ok",
                                  "result": event.get("error") or event.get("result") or ""})
                elif kind == "plan_fallback":
                    routing["route"] = "react"
                yield _sse_data(event)
                if kind == "error":
                    return
        answer = "".join(parts)
        if not answer.strip():
            yield _sse_data({"type": "error", "content": "未生成有效回答，请稍后重试"})
            return
        async with factory() as db:
            session = await get_session(db, user_id, session_id)
            reply = await _add_message(db, session_id, "assistant", answer, uncached, reply_key)
            session.updated_at = reply.created_at
            # A cheap provisional title is available before the background model call.
            if session.title == DEFAULT_TITLE and not session.title_manual:
                session.title = question[:settings.chat_auto_title_fallback_chars] or DEFAULT_TITLE
            await db.commit()
            title = session.title
            reply_dump = _message_dump(reply)
        if settings.chat_cache_enabled:
            await push_message(session_id, reply, settings.chat_cache_buffer_size)
            await invalidate_session_list(user_id)
        spawn_background_task(
            lambda: _update_title(factory, session_id, question, settings),
            key=f"title:{session_id}",
        )
        spawn_background_task(
            lambda: _summarize(factory, session_id, settings),
            key=f"summary:{session_id}",
        )
        yield _sse_data({
            "type": "done", "session_id": session_id, "answer": answer,
            "title": title, "assistant_message": reply_dump,
            "used_retrieval": decision.retrieve,
            "used_agent": bool(settings.agent_enabled and (settings.llm_api_key or get_react_streamer() or tools)),
            "used_plan": routing.get("route") == "plan_execute", **routing,
            "enable_thinking": thinking.applied, "thinking_requested": thinking.requested,
            "thinking_reason": thinking.reason, "tool_calls": tools,
            "sources": [{"content": item.get("content", "")[:100],
                         "source": item.get("source", "")} for item in hits[:3]],
        })
    except IntegrityError:
        yield _sse_data({"type": "error", "content": "请求已接收，请勿重复提交"})
    except Exception:
        logger.exception("AI 对话失败")
        yield _sse_data({"type": "error", "content": "生成失败，请稍后重试"})
    finally:
        usage_service.clear_trace_context()
        await release_sse_slot(user_id)
