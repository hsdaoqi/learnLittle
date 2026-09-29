"""第 36 阶段：Token 用量统计。"""

from fastapi.testclient import TestClient

from app.services.note_ai_service import set_note_ai_fn
from app.services.usage_service import estimate_tokens


def _auth(client: TestClient, username: str) -> dict:
    client.post("/api/v1/auth/register", json={"username": username, "password": "passw0rd123"})
    tokens = client.post(
        "/api/v1/auth/login", json={"username": username, "password": "passw0rd123"}
    ).json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def test_estimate_tokens_rounds_up():
    assert estimate_tokens("") == 0
    assert estimate_tokens("ab") == 1
    assert estimate_tokens("abc") == 2


def test_usage_summary_empty(client: TestClient):
    header = _auth(client, "usage_empty")
    resp = client.get("/api/v1/usage/summary", headers=header)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_calls"] == 0
    assert data["total_tokens"] == 0
    assert data["total_cost_cny"] == 0
    assert data["by_stage"] == []
    assert data["by_model"] == []


def test_note_ai_records_usage(client: TestClient):
    async def fake_complete(prompt: str) -> str:
        return "补全结果ABCD"

    set_note_ai_fn(fake_complete)
    header = _auth(client, "usage_note")
    resp = client.post(
        "/api/v1/note/autocomplete",
        json={"content": "hello world this is a prompt", "cursor_position": 5},
        headers=header,
    )
    assert resp.status_code == 200
    summary = client.get("/api/v1/usage/summary", headers=header).json()["data"]
    assert summary["total_calls"] == 1
    assert summary["total_prompt_tokens"] > 0
    assert summary["total_completion_tokens"] > 0
    assert summary["by_stage"][0]["stage"] == "note_ai"
    assert summary["total_cost_cny"] > 0


def test_usage_isolated_by_user(client: TestClient):
    async def fake_complete(prompt: str) -> str:
        return "ok"

    set_note_ai_fn(fake_complete)
    alice = _auth(client, "usage_alice")
    bob = _auth(client, "usage_bob")
    client.post(
        "/api/v1/note/autocomplete",
        json={"content": "alice prompt text", "cursor_position": 1},
        headers=alice,
    )
    alice_data = client.get("/api/v1/usage/summary", headers=alice).json()["data"]
    bob_data = client.get("/api/v1/usage/summary", headers=bob).json()["data"]
    assert alice_data["total_calls"] == 1
    assert bob_data["total_calls"] == 0


def test_usage_requires_auth(client: TestClient):
    resp = client.get("/api/v1/usage/summary")
    assert resp.status_code == 401
