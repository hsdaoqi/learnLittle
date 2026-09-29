"""聊天服务：会话 CRUD + 检索后流式改写（可降级为本地拼接）。"""

import logging
from collections.abc import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_service.runner import run_agent, should_use_agent
from app.config import Settings
from app.core.failed_response import BusinessError, ErrorCode
from app.models.chat import ChatMessage, ChatSession
from app.rag.chat_cache import (
    DEFAULT_BUFFER_SIZE,
    DEFAULT_SESSION_LIST_TTL,
    delete_messages,
    get_recent_messages,
    get_session_list,
    invalidate_session_list,
    push_message,
    rebuild_messages,
    set_session_list,
)
from app.rag.chat_history import (
    expand_retrieval_query,
    format_history_block,
    rag_context_text,
    select_history_messages,
)
from app.rag.hyde import generate_hyde
from app.rag.llm import get_llm_stream, iter_llm_tokens
from app.rag.memory import check_and_summarize, get_summary, truncate_summary
from app.rag.note_cards import referenced_notes_prompt, visible_question
from app.rag.rag_route import RouteDecision, decide_retrieval
from app.rag.rag_summarize import summarize_hits
from app.rag.session_title import DEFAULT_TITLE, generate_session_title
from app.rag.vector_store import get_vector_store
from app.schemas.chat import ChatAskRequest, ChatMessageResponse, ChatSessionResponse
from app.services import usage_service

logger = logging.getLogger(__name__)


def _session_dump(session: ChatSession) -> dict:
    return ChatSessionResponse.model_validate(session).model_dump(mode="json")


def _message_dump(message: ChatMessage) -> dict:
    return ChatMessageResponse.model_validate(message).model_dump(mode="json")


def _cache_on(settings: Settings | None) -> bool:
    return True if settings is None else settings.chat_cache_enabled


def _cache_buffer(settings: Settings | None) -> int:
    return settings.chat_cache_buffer_size if settings else DEFAULT_BUFFER_SIZE


def _cache_ttl(settings: Settings | None) -> int:
    return (
        settings.chat_cache_session_ttl_seconds
        if settings
        else DEFAULT_SESSION_LIST_TTL
    )


def compose_skipped_answer(question: str) -> str:
    """路由判定不检索时的本地回答，和「检索过但没命中」区分开。"""
    return (
        f"「{question}」看起来和你已有的知识库、笔记不太相关，这一轮没有检索资料。"
        "如果问的是文档里的内容，试着换更具体的关键词；闲聊的话可以直接继续。"
    )


def compose_answer(
    question: str, hits: list[dict], *, used_retrieval: bool = True
) -> str:
    """把检索切片拼成可读回答，明确标注来源。无命中时说明知识库为空。"""
    if not used_retrieval:
        return compose_skipped_answer(question)
    if not hits:
        return (
            "知识库和笔记里都没有检索到相关内容。"
            "请先上传文档或写笔记，或换一个更具体的问题。"
        )

    lines = [f"根据知识库和笔记，与「{question}」相关的内容如下：", ""]
    for i, hit in enumerate(hits, start=1):
        kind = "笔记" if hit.get("source") == "note" else "知识库"
        section = hit.get("section_title") or ""
        header = hit.get("filename") or "未命名"
        if section:
            header = f"{header} / {section}"
        lines.append(f"[{i}] [{kind}] {header}")
        lines.append((hit.get("content") or "").strip())
        lines.append("")
    lines.append("以上摘自你的文档和笔记，本阶段尚未接入大模型改写。")
    return "\n".join(lines).strip()


async def list_sessions(
    db: AsyncSession, user_id: str, settings: Settings | None = None
) -> list[dict]:
    if _cache_on(settings):
        cached = await get_session_list(user_id)
        if cached is not None:
            return cached
    rows = (
        (
            await db.execute(
                select(ChatSession)
                .where(ChatSession.user_id == user_id)
                .order_by(ChatSession.updated_at.desc())
            )
        )
        .scalars()
        .all()
    )
    data = [_session_dump(s) for s in rows]
    if _cache_on(settings):
        await set_session_list(user_id, data, _cache_ttl(settings))
    return data


async def get_session(db: AsyncSession, user_id: str, session_id: str) -> ChatSession:
    session = (
        await db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if session is None:
        raise BusinessError(code=ErrorCode.SESSION_NOT_FOUND, http_status=404)
    return session


async def create_session(
    db: AsyncSession,
    user_id: str,
    title: str = "新对话",
    settings: Settings | None = None,
) -> ChatSession:
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    await db.flush()
    await db.refresh(session)
    if _cache_on(settings):
        await invalidate_session_list(user_id)
    return session


async def update_session_title(
    db: AsyncSession,
    user_id: str,
    session_id: str,
    title: str,
    settings: Settings | None = None,
) -> ChatSession:
    session = await get_session(db, user_id, session_id)
    session.title = title
    await db.flush()
    await db.refresh(session)
    if _cache_on(settings):
        await invalidate_session_list(user_id)
    return session


async def delete_session(
    db: AsyncSession, user_id: str, session_id: str, settings: Settings | None = None
) -> None:
    session = await get_session(db, user_id, session_id)
    await db.delete(session)
    await db.flush()
    if _cache_on(settings):
        await invalidate_session_list(user_id)
        await delete_messages(session_id)


async def list_messages(db: AsyncSession, user_id: str, session_id: str) -> list[dict]:
    await get_session(db, user_id, session_id)
    rows = (
        (
            await db.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            )
        )
        .scalars()
        .all()
    )
    return [_message_dump(m) for m in rows]


async def _session_messages(
    db: AsyncSession, session_id: str, settings: Settings | None = None
) -> list:
    if _cache_on(settings):
        cached = await get_recent_messages(session_id)
        if cached:
            return cached
    rows = (
        (
            await db.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            )
        )
        .scalars()
        .all()
    )
    messages = list(rows)
    if _cache_on(settings) and messages:
        await rebuild_messages(session_id, messages, _cache_buffer(settings))
    return messages


def _history_block(
    messages: list, settings: Settings, rag_text: str | None = None
) -> str:
    selected = select_history_messages(messages, settings, rag_text=rag_text)
    return format_history_block(selected, settings.chat_history_max_chars)


async def _summary_text(db: AsyncSession, session_id: str, settings: Settings) -> str:
    row = await get_summary(db, session_id)
    if row is None or not row.summary_text:
        return ""
    return truncate_summary(row.summary_text, settings.memory_summary_max_tokens)


def _context_query(question: str, history_block: str, summary: str) -> str:
    parts: list[str] = []
    if summary.strip():
        parts.append(f"[历史对话摘要]\n{summary.strip()}")
    if history_block.strip():
        parts.append(history_block.strip())
    combined = "\n\n".join(parts)
    return expand_retrieval_query(question, combined)


async def _retrieve_or_skip(
    question: str,
    user_id: str,
    top_k: int,
    settings: Settings,
    history_block: str = "",
    summary: str = "",
) -> tuple[list[dict], RouteDecision]:
    route_query = _context_query(question, history_block, summary)
    decision = await decide_retrieval(route_query, user_id, settings)
    if not decision.retrieve:
        return [], decision
    retrieval_query = await generate_hyde(route_query, user_id, settings)
    hits = await get_vector_store().search_both(
        retrieval_query, user_id, top_k, rerank_query=route_query
    )
    return hits, decision


def _ask_payload(
    session_id: str,
    answer: str,
    hits: list[dict],
    decision: RouteDecision,
    user_msg,
    assistant_msg,
    *,
    used_agent: bool = False,
    tool_calls: list[dict] | None = None,
    title: str | None = None,
) -> dict:
    return {
        "session_id": session_id,
        "answer": answer,
        "sources": hits,
        "used_retrieval": decision.retrieve,
        "used_agent": used_agent,
        "tool_calls": tool_calls or [],
        "route_distance": None
        if decision.distance == float("inf")
        else decision.distance,
        "title": title,
        "user_message": _message_dump(user_msg),
        "assistant_message": _message_dump(assistant_msg),
    }


async def _maybe_auto_title(
    session: ChatSession, question: str, settings: Settings
) -> str:
    """标题仍是默认值时生成一次；手动改名后不再覆盖。"""
    if session.title != DEFAULT_TITLE:
        return session.title
    session.title = await generate_session_title(question, settings)
    return session.title


async def _collect_agent_answer(
    question: str,
    user_id: str,
    session_factory,
    settings: Settings,
    history: str,
) -> tuple[str, list[dict]]:
    parts: list[str] = []
    calls: list[dict] = []
    async for event in run_agent(question, user_id, session_factory, settings, history):
        kind = event.get("type")
        if kind == "tool_start":
            calls.append({"name": event.get("name"), "status": "start"})
        elif kind == "tool_end":
            calls.append(
                {
                    "name": event.get("name"),
                    "status": "error" if event.get("error") else "ok",
                    "result": event.get("result") or event.get("error") or "",
                }
            )
        elif kind == "response":
            text = event.get("content") or ""
            if text:
                parts.append(text)
    return "".join(parts).strip(), calls


async def _add_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    settings: Settings | None = None,
) -> ChatMessage:
    message = ChatMessage(session_id=session_id, role=role, content=content)
    db.add(message)
    await db.flush()
    await db.refresh(message)
    if _cache_on(settings):
        await push_message(session_id, message, _cache_buffer(settings))
    return message


async def ask(
    db: AsyncSession,
    user_id: str,
    data: ChatAskRequest,
    settings: Settings,
    session_factory=None,
) -> dict:
    raw_message = data.message.strip()
    question = visible_question(raw_message)
    agent_question = referenced_notes_prompt(raw_message) or question
    if data.session_id:
        session = await get_session(db, user_id, data.session_id)
    else:
        session = await create_session(db, user_id, DEFAULT_TITLE, settings)

    usage_service.set_trace_context(
        user_id=user_id, session_id=session.id, stage="chat"
    )
    try:
        rows = await _session_messages(db, session.id, settings)
        summary = await _summary_text(db, session.id, settings)
        history_block = _history_block(rows, settings, rag_text=None)

        used_agent = False
        tool_calls: list[dict] = []
        answer = ""
        hits: list[dict] = []
        decision = RouteDecision(False, float("inf"), "pending")

        if should_use_agent(question, settings) and session_factory is not None:
            try:
                answer, tool_calls = await _collect_agent_answer(
                    agent_question, user_id, session_factory, settings, history_block
                )
                used_agent = bool(answer)
                if used_agent:
                    decision = RouteDecision(False, float("inf"), "agent")
            except Exception as exc:
                logger.warning("Agent 问答失败，回退检索: %s", exc)
                answer = ""
                tool_calls = []

        if not answer:
            hits, decision = await _retrieve_or_skip(
                question, user_id, data.top_k, settings, history_block, summary
            )
            context_hits = (
                await summarize_hits(question, hits, settings)
                if decision.retrieve
                else []
            )
            rag_text = rag_context_text(context_hits) if decision.retrieve else ""
            history_block = _history_block(rows, settings, rag_text=rag_text)
            answer = compose_answer(
                question, context_hits, used_retrieval=decision.retrieve
            )

        user_msg = await _add_message(db, session.id, "user", raw_message, settings)
        assistant_msg = await _add_message(
            db, session.id, "assistant", answer, settings
        )
        session.updated_at = assistant_msg.created_at
        await _maybe_auto_title(session, question, settings)
        await db.flush()
        await check_and_summarize(db, session.id, settings)
        await db.refresh(session)
        if _cache_on(settings):
            await invalidate_session_list(user_id)
    finally:
        usage_service.clear_trace_context()

    return _ask_payload(
        session.id,
        answer,
        hits,
        decision,
        user_msg,
        assistant_msg,
        used_agent=used_agent,
        tool_calls=tool_calls,
        title=session.title,
    )


def _sse(event: str, data: dict) -> str:
    import json

    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _fallback_tokens(text: str) -> AsyncIterator[str]:
    """没配 LLM 时把本地答案按块推出，前端仍走同一套流式 UI。"""
    step = 80
    for i in range(0, len(text), step):
        yield text[i : i + step]


async def stream_ask(
    session_factory,
    user_id: str,
    data: ChatAskRequest,
    settings: Settings,
) -> AsyncIterator[str]:
    """检索 → 流式输出 → 落库。

    StreamingResponse 会在生成器还没跑完时关闭请求级 Depends 会话，
    所以这里自己开独立 session 并 commit。
    """
    raw_message = data.message.strip()
    question = visible_question(raw_message)
    agent_question = referenced_notes_prompt(raw_message) or question
    async with session_factory() as db:
        try:
            if data.session_id:
                session = await get_session(db, user_id, data.session_id)
            else:
                session = await create_session(db, user_id, DEFAULT_TITLE, settings)

            usage_service.set_trace_context(
                user_id=user_id, session_id=session.id, stage="chat"
            )
            rows = await _session_messages(db, session.id, settings)
            summary = await _summary_text(db, session.id, settings)
            history_block = _history_block(rows, settings, rag_text=None)

            used_agent = False
            tool_calls: list[dict] = []
            agent_events: list[dict] = []
            if should_use_agent(question, settings):
                try:
                    async for event in run_agent(
                        agent_question,
                        user_id,
                        session_factory,
                        settings,
                        history_block,
                    ):
                        agent_events.append(event)
                        if event.get("type") == "tool_end":
                            tool_calls.append(
                                {
                                    "name": event.get("name"),
                                    "status": "error" if event.get("error") else "ok",
                                    "result": event.get("result")
                                    or event.get("error")
                                    or "",
                                }
                            )
                    used_agent = any(
                        event.get("type") == "response" and event.get("content")
                        for event in agent_events
                    )
                except Exception as exc:
                    logger.warning("Agent 流式失败，回退检索: %s", exc)
                    agent_events = []
                    used_agent = False

            hits: list[dict] = []
            decision = RouteDecision(
                False, float("inf"), "agent" if used_agent else "pending"
            )
            context_hits: list[dict] = []
            if not used_agent:
                hits, decision = await _retrieve_or_skip(
                    question, user_id, data.top_k, settings, history_block, summary
                )
                context_hits = (
                    await summarize_hits(question, hits, settings)
                    if decision.retrieve
                    else []
                )
                rag_text = rag_context_text(context_hits) if decision.retrieve else ""
                history_block = _history_block(rows, settings, rag_text=rag_text)

            user_msg = await _add_message(db, session.id, "user", raw_message, settings)
            await db.commit()
            await db.refresh(session)
            await db.refresh(user_msg)

            yield _sse(
                "meta",
                {
                    "session_id": session.id,
                    "sources": hits,
                    "used_retrieval": decision.retrieve,
                    "used_agent": used_agent,
                    "route_distance": None
                    if decision.distance == float("inf")
                    else decision.distance,
                    "user_message": _message_dump(user_msg),
                },
            )

            answer_parts: list[str] = []
            if used_agent:
                for event in agent_events:
                    kind = event.get("type")
                    if kind == "tool_start":
                        yield _sse("tool_start", {"name": event.get("name")})
                    elif kind == "tool_end":
                        yield _sse(
                            "tool_end",
                            {
                                "name": event.get("name"),
                                "error": event.get("error"),
                                "result": event.get("result") or "",
                            },
                        )
                    elif kind == "response":
                        text = event.get("content") or ""
                        if text:
                            answer_parts.append(text)
                            async for token in _fallback_tokens(text):
                                yield _sse("token", {"text": token})
            else:
                used_llm = get_llm_stream() is not None or bool(settings.llm_api_key)
                try:
                    if used_llm:
                        async for token in iter_llm_tokens(
                            question,
                            context_hits,
                            settings,
                            used_retrieval=decision.retrieve,
                            history=history_block,
                            summary=summary,
                        ):
                            if not token:
                                continue
                            answer_parts.append(token)
                            yield _sse("token", {"text": token})
                    if not answer_parts:
                        fallback = compose_answer(
                            question, context_hits, used_retrieval=decision.retrieve
                        )
                        async for token in _fallback_tokens(fallback):
                            answer_parts.append(token)
                            yield _sse("token", {"text": token})
                except Exception as exc:
                    logger.warning("LLM 流式失败，降级本地拼接: %s", exc)
                    answer_parts = []
                    fallback = compose_answer(
                        question, context_hits, used_retrieval=decision.retrieve
                    )
                    async for token in _fallback_tokens(fallback):
                        answer_parts.append(token)
                        yield _sse("token", {"text": token})

            answer = "".join(answer_parts)
            assistant_msg = await _add_message(
                db, session.id, "assistant", answer, settings
            )
            session.updated_at = assistant_msg.created_at
            await _maybe_auto_title(session, question, settings)
            await db.flush()
            await check_and_summarize(db, session.id, settings)
            await db.commit()
            if _cache_on(settings):
                await invalidate_session_list(user_id)
            await db.refresh(session)
            await db.refresh(assistant_msg)
            usage_service.clear_trace_context()

            yield _sse(
                "done",
                {
                    "session_id": session.id,
                    "answer": answer,
                    "used_retrieval": decision.retrieve,
                    "used_agent": used_agent,
                    "tool_calls": tool_calls,
                    "title": session.title,
                    "assistant_message": _message_dump(assistant_msg),
                },
            )
        except Exception:
            usage_service.clear_trace_context()
            await db.rollback()
            raise
