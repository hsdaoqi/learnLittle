import asyncio
import json
from contextlib import aclosing

import pytest
from sqlalchemy import func, select

from app.ai_service.react_agent import set_react_streamer
from app.config import Settings
from app.core.task_runner import drain_background_tasks
from app.models.chat import ChatMessage, ChatSession
from app.services import query_service


def auth(client, name):
    response = client.post("/api/v1/auth/register", json={
        "username": name, "password": "passw0rd123",
    })
    assert response.status_code == 200
    user_id = response.json()["data"]["user_id"]
    tokens = client.post("/api/v1/auth/login", json={
        "username": name, "password": "passw0rd123",
    }).json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}, user_id


def query(client, headers, **payload):
    response = client.post("/api/v1/chat/query", headers=headers, json=payload)
    assert response.status_code == 200
    return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]


def test_query_rag_failure_preserves_user_message_and_final_answer(client, monkeypatch):
    headers, user_id = auth(client, "lifecycle")
    factory = client.app.state.db_session_factory
    seen = {}

    async def failed_rag(question, owner, settings):
        async with factory() as db:
            seen["saved_first"] = await db.scalar(select(func.count(ChatMessage.id)))
        raise RuntimeError("retriever unavailable")

    async def fake_react(question, owner, session_factory, settings, **kwargs):
        seen["history"] = kwargs["history"]
        yield {"type": "response", "content": "draft"}
        yield {"type": "response_replace", "content": "corrected"}
        yield {"type": "stream_done", "full_response": "corrected"}

    monkeypatch.setattr(query_service, "decide_retrieval", failed_rag)
    set_react_streamer(fake_react)
    events = query(client, headers, message="hello", idempotency_key="one")
    assert seen == {"saved_first": 1, "history": []}
    done = events[-1]
    assert done["type"] == "done"
    assert done["answer"] == done["assistant_message"]["content"] == "corrected"
    assert done["used_retrieval"] is False
    rows = client.get(
        f"/api/v1/chat/sessions/{done['session_id']}/messages", headers=headers,
    ).json()["data"]
    assert [row["content"] for row in rows] == ["hello", "corrected"]


def test_query_idempotency_replays_once_and_isolates_users(client):
    headers, _ = auth(client, "once_a")
    other, _ = auth(client, "once_b")
    calls = []

    async def fake(*args, **kwargs):
        calls.append(1)
        yield {"type": "response", "content": "answer"}

    set_react_streamer(fake)
    first = query(client, headers, message="hello", idempotency_key="same")[-1]
    second = query(client, headers, message="hello", idempotency_key="same")[-1]
    assert first["assistant_message"]["id"] == second["assistant_message"]["id"]
    assert second["replayed"] is True
    assert len(calls) == 1
    conflict = query(client, headers, message="changed", idempotency_key="same")
    assert conflict[-1]["type"] == "error"
    other_result = query(client, other, message="hello", idempotency_key="same")[-1]
    assert other_result["session_id"] != first["session_id"]
    assert len(calls) == 2
    forbidden = query(client, other, message="hello", session_id=first["session_id"])
    assert forbidden[-1]["type"] == "error"
    assert len(calls) == 2


def test_inflight_duplicate_does_not_run_agent_twice(client, monkeypatch):
    from app.schemas.chat import QueryRequest

    _, user_id = auth(client, "inflight")
    entered = asyncio.Event()
    release = asyncio.Event()
    calls = []

    async def fake(*args, **kwargs):
        calls.append(1)
        entered.set()
        await release.wait()
        yield {"type": "response", "content": "answer"}

    set_react_streamer(fake)

    async def run():
        data = QueryRequest(message="hello", idempotency_key="concurrent")
        factory = client.app.state.db_session_factory
        config = client.app.state.settings

        async def collect():
            return [event async for event in query_service.stream_query(factory, user_id, data, config)]

        first = asyncio.create_task(collect())
        await asyncio.wait_for(entered.wait(), 3)
        duplicate = await collect()
        assert '"type": "error"' in duplicate[-1]
        release.set()
        await first
        assert len(calls) == 1
        async with factory() as db:
            assert await db.scalar(select(func.count(ChatMessage.id))) == 2

    client.portal.call(run)


def test_full_sql_memory_is_not_limited_by_redis_window(client):
    headers, user_id = auth(client, "full_memory")
    factory = client.app.state.db_session_factory
    captured = []

    async def seed():
        async with factory() as db:
            session = ChatSession(user_id=user_id, title="existing")
            db.add(session)
            await db.flush()
            for i in range(30):
                db.add(ChatMessage(session_id=session.id, role="user" if i % 2 == 0 else "assistant",
                                   content=f"message-{i}"))
            await db.commit()
            return session.id

    async def fake(*args, **kwargs):
        captured.extend(kwargs["history"])
        yield {"type": "response", "content": "answer"}

    session_id = client.portal.call(seed)
    set_react_streamer(fake)
    events = query(client, headers, message="next question", session_id=session_id)
    assert events[-1]["type"] == "done"
    assert len(captured) == 30
    assert captured[0]["content"] == "message-0"


def test_slow_title_does_not_block_done_or_overwrite_manual_title(client, monkeypatch):
    headers, _ = auth(client, "title_race")
    factory = client.app.state.db_session_factory
    started = asyncio.Event()
    release = asyncio.Event()

    async def slow_title(question, settings):
        started.set()
        await release.wait()
        return "automatic-title"

    async def fake(*args, **kwargs):
        yield {"type": "response", "content": "answer"}

    monkeypatch.setattr(query_service, "generate_session_title", slow_title)
    set_react_streamer(fake)
    done = query(client, headers, message="hello")[-1]
    assert done["type"] == "done"

    async def wait_started():
        await asyncio.wait_for(started.wait(), 2)

    client.portal.call(wait_started)
    session_id = done["session_id"]
    result = client.put(f"/api/v1/chat/sessions/{session_id}/title", headers=headers,
                        json={"title": "manual-title"})
    assert result.status_code == 200

    async def finish():
        release.set()
        await drain_background_tasks()
        async with factory() as db:
            session = await db.get(ChatSession, session_id)
            assert session.title == "manual-title"
            assert session.title_manual is True

    client.portal.call(finish)


def test_titles_update_in_early_rounds_only(client, monkeypatch):
    _, user_id = auth(client, "early_title")
    factory = client.app.state.db_session_factory
    called = []

    async def title(question, settings):
        called.append(question)
        return question

    monkeypatch.setattr(query_service, "generate_session_title", title)

    async def run():
        async with factory() as db:
            session = ChatSession(user_id=user_id, title="provisional")
            db.add(session)
            await db.flush()
            session_id = session.id
            for i in range(2):
                db.add(ChatMessage(session_id=session_id, role="user", content=str(i)))
            await db.commit()
        await query_service._update_title(factory, session_id, "second-round", client.app.state.settings)
        async with factory() as db:
            assert (await db.get(ChatSession, session_id)).title == "second-round"
            for i in range(2):
                db.add(ChatMessage(session_id=session_id, role="user", content=str(i)))
            await db.commit()
        await query_service._update_title(factory, session_id, "fourth-round", client.app.state.settings)
        assert called == ["second-round"]

    client.portal.call(run)


def test_registration_requires_verified_email_by_default(client, monkeypatch):
    from app.services import email_service

    client.app.state.settings.registration_require_email = True
    response = client.post("/api/v1/auth/register", json={
        "username": "required_email", "password": "passw0rd123",
    })
    assert response.status_code == 400

    async def verify(email, code):
        return code == "123456"

    monkeypatch.setattr(email_service, "verify_code", verify)
    payload = {"username": "required_email", "password": "passw0rd123",
               "email": "test@example.com", "verification_code": "000000"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 400
    payload["verification_code"] = "123456"
    assert client.post("/api/v1/auth/register", json=payload).status_code == 200


def test_sse_token_single_use_and_not_profile_auth(client):
    from app.db.redis_client import get_redis
    from app.utils.auth_utils import decode_token

    headers, _ = auth(client, "sse_auth")
    result = client.post("/api/v1/auth/sse-token", headers=headers).json()["data"]
    assert result["expires_in"] == 60
    token = result["token"]
    payload = decode_token(token)
    assert payload["exp"] - payload["iat"] == 60
    short = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/v1/user/me", headers=short).status_code == 401
    assert query(client, short, message="hello")[-1]["type"] == "done"
    assert client.post("/api/v1/chat/query", headers=short, json={"message": "hello"}).status_code == 401
    another = client.post("/api/v1/auth/sse-token", headers=headers).json()["data"]["token"]

    async def expire():
        await get_redis().delete(f"sse_token:{decode_token(another)['jti']}")

    client.portal.call(expire)
    assert client.post("/api/v1/chat/query", headers={"Authorization": f"Bearer {another}"},
                       json={"message": "hello"}).status_code == 401


@pytest.mark.asyncio
async def test_chat_graph_cancellation_closes_model_stream():
    from app.ai_service.chat_graph import stream_chat_graph

    closed = []

    async def endless(*args, **kwargs):
        try:
            while True:
                yield {"type": "response", "content": "chunk"}
                await asyncio.sleep(0)
        finally:
            closed.append(True)

    set_react_streamer(endless)
    stream = stream_chat_graph(
        "hello", "u", None, Settings(_env_file=None, llm_api_key=""),
        history=[], summary="", rag_context="", enable_thinking=False, fallback_answer="local",
    )
    async with aclosing(stream):
        async for event in stream:
            if event["type"] == "response":
                break
    assert closed == [True]
