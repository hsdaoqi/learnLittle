import json

from app.ai_service.react_agent import set_react_streamer
from app.services import chat_service, query_service


def auth(client, name):
    result = client.post(
        "/api/v1/auth/register", json={"username": name, "password": "passw0rd123"},
    )
    assert result.status_code == 200
    token = client.post(
        "/api/v1/auth/login", json={"username": name, "password": "passw0rd123"},
    ).json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}, result.json()["data"]["user_id"]


def query(client, headers, **payload):
    response = client.post("/api/v1/chat/query", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    return [
        json.loads(line[6:])
        for line in response.text.splitlines() if line.startswith("data: ")
    ]


def test_chat_routes_have_one_query_entry(client):
    paths = client.app.openapi()["paths"]
    chat_paths = {path for path in paths if path.startswith("/api/v1/chat/")}
    assert chat_paths == {
        "/api/v1/chat/query",
        "/api/v1/chat/sessions",
        "/api/v1/chat/sessions/{session_id}/title",
        "/api/v1/chat/sessions/{session_id}",
        "/api/v1/chat/sessions/{session_id}/messages",
    }
    headers, _ = auth(client, "retired_routes")
    for path in ("ask", "stream"):
        response = client.post(
            f"/api/v1/chat/{path}", headers=headers, json={"message": "hello"},
        )
        assert response.status_code == 404
    for name in ("ask", "stream_ask", "stream_query"):
        assert not hasattr(chat_service, name)


def test_chat_router_calls_query_service_directly(client, monkeypatch):
    headers, user_id = auth(client, "direct_query")
    captured = {}

    async def fake(factory, owner, data, settings):
        captured.update(
            factory=factory, owner=owner, message=data.message, settings=settings,
        )
        yield 'data: {"type": "response", "content": "answer"}\n\n'
        yield 'data: {"type": "done", "answer": "answer"}\n\n'

    monkeypatch.setattr(query_service, "stream_query", fake)
    events = query(client, headers, message="hello")
    assert events[-1] == {"type": "done", "answer": "answer"}
    assert captured == {
        "factory": client.app.state.db_session_factory,
        "owner": user_id,
        "message": "hello",
        "settings": client.app.state.settings,
    }


def test_query_preserves_session_crud_and_user_isolation(client):
    headers, _ = auth(client, "session_owner")
    other, _ = auth(client, "session_other")

    async def fake(*args, **kwargs):
        yield {"type": "response", "content": "answer"}

    set_react_streamer(fake)
    done = query(client, headers, message="hello")[-1]
    assert done["type"] == "done"
    session_id = done["session_id"]
    base = f"/api/v1/chat/sessions/{session_id}"

    sessions = client.get("/api/v1/chat/sessions", headers=headers).json()["data"]
    assert [session["id"] for session in sessions] == [session_id]
    assert client.get("/api/v1/chat/sessions", headers=other).json()["data"] == []
    messages = client.get(f"{base}/messages", headers=headers).json()["data"]
    assert [item["content"] for item in messages] == ["hello", "answer"]

    assert client.get(f"{base}/messages", headers=other).status_code == 404
    assert client.put(f"{base}/title", headers=other, json={"title": "bad"}).status_code == 404
    assert client.delete(base, headers=other).status_code == 404
    renamed = client.put(f"{base}/title", headers=headers, json={"title": "manual"})
    assert renamed.status_code == 200
    assert renamed.json()["data"]["title"] == "manual"
    sessions = client.get("/api/v1/chat/sessions", headers=headers).json()["data"]
    assert sessions[0]["title"] == "manual"
    assert client.delete(base, headers=headers).status_code == 200
    assert client.get("/api/v1/chat/sessions", headers=headers).json()["data"] == []
    assert client.get(f"{base}/messages", headers=headers).status_code == 404


def test_local_fallback_preserves_sources_and_does_not_claim_no_llm():
    answer = query_service.compose_answer(
        "question", [{"source": "note", "filename": "title", "content": "body"}],
    )
    assert "[1] [笔记] title" in answer
    assert "body" in answer
    assert "尚未接入大模型" not in answer
    assert "没有检索资料" in query_service.compose_answer("hello", [], used_retrieval=False)
    assert "没有检索到" in query_service.compose_answer("hello", [])
    event = query_service._sse_data({"type": "response", "content": "中文"})
    assert json.loads(event.removeprefix("data: "))["content"] == "中文"


def test_query_without_model_still_executes_local_tool(client):
    headers, _ = auth(client, "local_tool_cleanup")
    events = query(client, headers, message="现在几点")
    starts = [event for event in events if event["type"] == "tool_start"]
    ends = [event for event in events if event["type"] == "tool_end"]
    assert starts == [{"type": "tool_start", "name": "what_time_is_now"}]
    assert ends[0]["name"] == "what_time_is_now"
    assert not ends[0].get("error")
    assert events[-1]["type"] == "done"
    assert events[-1]["answer"] == ends[0]["result"]
    summary = client.get("/api/v1/usage/summary", headers=headers).json()["data"]
    assert summary["total_calls"] == 0


def test_auxiliary_completion_still_records_provider_usage(client, monkeypatch):
    import httpx

    from app.rag.llm import complete_openai_compatible
    from app.services import usage_service

    headers, user_id = auth(client, "aux_usage_cleanup")

    async def fake_post(self, url, **kwargs):
        assert url.endswith("/chat/completions")
        assert kwargs["json"]["stream"] is False
        return httpx.Response(200, json={
            "choices": [{"message": {"content": "title"}}],
            "usage": {"prompt_tokens": 13, "completion_tokens": 2, "total_tokens": 15},
        })

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    async def complete():
        usage_service.set_trace_context(user_id=user_id, stage="title")
        try:
            return await complete_openai_compatible("prompt", client.app.state.settings)
        finally:
            usage_service.clear_trace_context()

    assert client.portal.call(complete) == "title"
    summary = client.get("/api/v1/usage/summary", headers=headers).json()["data"]
    assert summary["total_calls"] == 1
    assert summary["total_prompt_tokens"] == 13
    assert summary["total_completion_tokens"] == 2
    assert summary["total_tokens"] == 15
    assert summary["by_stage"] == [{
        "stage": "title", "calls": 1, "prompt_tokens": 13, "completion_tokens": 2,
    }]
