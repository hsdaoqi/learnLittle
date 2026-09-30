"""第 44 阶段：深度思考只作用在主问答；分类器 / 计划独立；附件强制关闭。

enable_thinking 只发给百炼。GPT 兼容网关不传该字段，避免 400。
"""

from app.ai_service.thinking import (
    ATTACHMENT_THINKING_NOTICE,
    UNSUPPORTED_THINKING_NOTICE,
    agent_timeout,
    complete_thinking_for,
    extra_body,
    payload_thinking_fields,
    resolve_agent_thinking,
    thinking_protocol,
)
from app.ai_service.react_agent import set_react_streamer
from app.config import Settings
from fastapi.testclient import TestClient


def _settings(**kwargs) -> Settings:
    defaults = {"app_env": "test", "llm_api_key": "", "llm_stream_timeout": 60}
    defaults.update(kwargs)
    return Settings(**defaults)


def _auth(client: TestClient, username: str) -> dict:
    client.post("/api/v1/auth/register", json={"username": username, "password": "passw0rd123"})
    tokens = client.post(
        "/api/v1/auth/login", json={"username": username, "password": "passw0rd123"}
    ).json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def _read_sse(client: TestClient, headers: dict, payload: dict) -> str:
    with client.stream("POST", "/api/v1/chat/query", json=payload, headers=headers) as resp:
        assert resp.status_code == 200
        return "".join(
            chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk
            for chunk in resp.iter_text()
        )


def test_resolve_agent_thinking_plain_on_off():
    off = resolve_agent_thinking(False)
    assert off.applied is False
    assert off.reason == "off"
    assert off.sse_notice() is None

    on = resolve_agent_thinking(True)
    assert on.applied is True
    assert on.reason == "agent"
    assert on.sse_notice() is None


def test_resolve_agent_thinking_attachment_mutex():
    decision = resolve_agent_thinking(True, has_attachments=True)
    assert decision.requested is True
    assert decision.applied is False
    assert decision.reason == "attachment"
    notice = decision.sse_notice()
    assert notice is not None
    assert notice["stage"] == "attachment"
    assert ATTACHMENT_THINKING_NOTICE in notice["content"]

    ignored = resolve_agent_thinking(False, has_attachments=True)
    assert ignored.sse_notice() is None


def test_complete_roles_default_off_and_independent():
    settings = _settings()
    assert thinking_protocol(settings) == "dashscope"
    assert complete_thinking_for("classifier", settings) is False
    assert complete_thinking_for("plan", settings) is False
    assert complete_thinking_for("reflection", settings) is False
    assert complete_thinking_for("agent", settings) is False

    settings = _settings(
        classifier_enable_thinking=True,
        plan_enable_thinking=True,
        reflection_enable_thinking=True,
    )
    assert complete_thinking_for("classifier", settings) is True
    assert complete_thinking_for("plan", settings) is True
    assert complete_thinking_for("reflection", settings) is True
    assert extra_body(True, settings) == {"enable_thinking": True}
    assert extra_body(False, settings) == {"enable_thinking": False}


def test_agent_timeout_doubles_when_thinking():
    settings = _settings(llm_stream_timeout=60)
    assert agent_timeout(settings, False) == 60
    assert agent_timeout(settings, True) == 120
    assert agent_timeout(settings, True, timeout=40) == 80


def test_thinking_protocol_auto_dashscope_vs_openai_gateway():
    dash = _settings(llm_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    gpt = _settings(llm_base_url="https://sub.advanced.ccwu.cc/v1", llm_model="gpt-5.6-sol")
    assert thinking_protocol(dash) == "dashscope"
    assert thinking_protocol(gpt) == "none"
    assert extra_body(True, gpt) is None
    assert payload_thinking_fields(True, gpt) == {}
    assert payload_thinking_fields(False, dash) == {"enable_thinking": False}
    assert complete_thinking_for("classifier", _settings(
        llm_base_url="https://sub.advanced.ccwu.cc/v1",
        classifier_enable_thinking=True,
    )) is False


def test_thinking_protocol_forced_none_even_on_dashscope():
    settings = _settings(
        llm_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        llm_thinking_protocol="none",
    )
    assert thinking_protocol(settings) == "none"
    assert extra_body(True, settings) is None


def test_resolve_agent_thinking_unsupported_on_gpt_gateway():
    settings = _settings(llm_base_url="https://sub.advanced.ccwu.cc/v1")
    decision = resolve_agent_thinking(True, settings=settings)
    assert decision.requested is True
    assert decision.applied is False
    assert decision.reason == "unsupported"
    notice = decision.sse_notice()
    assert notice is not None
    assert notice["stage"] == "unsupported"
    assert UNSUPPORTED_THINKING_NOTICE in notice["content"]


def test_query_thinking_applied_without_attachments(client: TestClient):
    captured: dict = {}

    async def fake_react(question, user_id, session_factory, settings, **kwargs):
        captured["enable_thinking"] = kwargs.get("enable_thinking")
        yield {"type": "response", "content": "思考后的答案"}
        yield {"type": "stream_done", "full_response": "思考后的答案"}

    set_react_streamer(fake_react)
    try:
        headers = _auth(client, "think_on")
        body = _read_sse(
            client,
            headers,
            {"message": "搜索笔记 深度思考", "enable_thinking": True},
        )
    finally:
        set_react_streamer(None)

    assert captured.get("enable_thinking") is True
    assert ATTACHMENT_THINKING_NOTICE not in body
    assert '"enable_thinking": true' in body or '"enable_thinking":true' in body
    assert '"thinking_reason": "agent"' in body or '"thinking_reason":"agent"' in body


def test_query_thinking_disabled_when_attachment_ids(client: TestClient):
    captured: dict = {}

    async def fake_react(question, user_id, session_factory, settings, **kwargs):
        captured["enable_thinking"] = kwargs.get("enable_thinking")
        yield {"type": "response", "content": "看图回答"}
        yield {"type": "stream_done", "full_response": "看图回答"}

    set_react_streamer(fake_react)
    try:
        headers = _auth(client, "think_att")
        body = _read_sse(
            client,
            headers,
            {
                "message": "这张图是什么",
                "enable_thinking": True,
                "attachment_ids": ["att-1"],
            },
        )
    finally:
        set_react_streamer(None)

    assert captured.get("enable_thinking") is False
    assert ATTACHMENT_THINKING_NOTICE in body
    assert '"stage": "attachment"' in body or '"stage":"attachment"' in body
    assert '"enable_thinking": false' in body or '"enable_thinking":false' in body
    assert '"thinking_reason": "attachment"' in body or '"thinking_reason":"attachment"' in body
    assert '"thinking_requested": true' in body or '"thinking_requested":true' in body


def test_query_thinking_skipped_when_protocol_none(client: TestClient):
    captured: dict = {}

    async def fake_react(question, user_id, session_factory, settings, **kwargs):
        captured["enable_thinking"] = kwargs.get("enable_thinking")
        yield {"type": "response", "content": "普通回答"}
        yield {"type": "stream_done", "full_response": "普通回答"}

    set_react_streamer(fake_react)
    try:
        headers = _auth(client, "think_none")
        client.app.state.settings = client.app.state.settings.model_copy(
            update={
                "llm_base_url": "https://sub.advanced.ccwu.cc/v1",
                "llm_model": "gpt-5.6-sol",
            }
        )
        body = _read_sse(
            client,
            headers,
            {"message": "搜索笔记 深度思考", "enable_thinking": True},
        )
    finally:
        set_react_streamer(None)

    assert captured.get("enable_thinking") is False
    assert UNSUPPORTED_THINKING_NOTICE in body
    assert '"thinking_reason": "unsupported"' in body or '"thinking_reason":"unsupported"' in body
    assert '"enable_thinking": false' in body or '"enable_thinking":false' in body
