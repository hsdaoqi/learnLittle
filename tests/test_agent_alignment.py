import asyncio
import json
from contextlib import aclosing

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.outputs import ChatGenerationChunk

from app.ai_service import plan_execute as plan
from app.ai_service import react_agent as react
from app.ai_service.langchain_tools import build_langchain_tools
from app.ai_service.tool_registry import ToolSpec, registry
from app.config import Settings
from app.rag.chat_history import build_agent_history
from app.rag.token_budget import count_message


def settings(**kwargs):
    return Settings(_env_file=None, app_env="test", llm_api_key="", **kwargs)


def test_memory_covers_unsummarized_gap_and_preserves_roles():
    messages = [
        {"id": i, "role": "user" if i % 2 else "assistant", "content": f"message {i}"}
        for i in range(1, 41)
    ]
    messages[10]["content"] = "long message\n" * 100
    history = build_agent_history(messages[:30], settings(), question="next")
    assert len(history) == 30
    assert history[10]["content"] == messages[10]["content"]
    history = build_agent_history(
        messages, settings(), question="next", summary="first twenty", summarized_through=20,
    )
    assert len(history) == 20
    assert history[0]["content"] == "message 21"
    converted = react._history_messages(history, "summary")
    assert isinstance(converted[1], HumanMessage)
    assert isinstance(converted[2], AIMessage)


def test_history_respects_tiny_remaining_budget():
    config = settings(
        token_model_context_size=600, token_system_prompt=50,
        token_safety_margin=50, token_agent_scratchpad_reserve=400,
    )
    history = build_agent_history([{"role": "user", "content": "word " * 1000}], config)
    assert history
    assert sum(count_message(item["content"]) for item in history) + 2 <= 100


def test_legacy_zero_reserve_still_leaves_room_for_agent_tools():
    config = settings(token_agent_scratchpad_reserve=0)
    history = build_agent_history([{"role": "user", "content": "word " * 30000}], config)
    quota = config.token_model_context_size - config.token_system_prompt - config.token_safety_margin - 4000
    assert sum(count_message(item["content"]) for item in history) + 2 <= quota


def test_tool_loop_limit_still_reports_started_write_for_replay_guard():
    events, _ = react.map_langchain_event(
        {"event": "on_tool_start", "name": "update_note_tool"},
        consecutive_tool_calls=6, tool_start_times={},
    )
    assert [event["type"] for event in events] == ["tool_start", "error"]


@pytest.mark.asyncio
async def test_planning_deadline_falls_back_without_executing_tools():
    async def stalled(_):
        await asyncio.sleep(10)

    plan.set_plan_fn(stalled)
    events = [event async for event in plan.run_plan(
        "request", "u", None, settings(plan_timeout=0.01),
    )]
    assert events == [{"type": "plan_fallback", "reason": "plan_failed"}]


@pytest.mark.asyncio
async def test_classifier_deadline_falls_back_to_react(monkeypatch):
    from app.ai_service import query_classifier

    async def stalled(*args, **kwargs):
        await asyncio.sleep(10)

    monkeypatch.setattr(query_classifier, "_llm_classify", stalled)
    config = settings(classifier_timeout=0.01).model_copy(update={"llm_api_key": "test"})
    result = await query_classifier.classify_query("uncertain " * 20, config, plan_available=True)
    assert result.route == "react"
    assert result.source == "fallback"


@pytest.mark.parametrize("steps", [
    [{"step": 1, "action": "a", "depends_on": [2]}],
    [{"step": 1, "action": "a", "depends_on": [1]}],
    [{"step": 1, "action": "a"}, {"step": 1, "action": "b"}],
    [{"step": 1, "action": "a", "tool": "not_registered"}],
])
def test_plan_rejects_invalid_dependency_graph(steps):
    with pytest.raises(ValueError):
        plan.parse_plan_payload(json.dumps({"steps": steps}))


@pytest.mark.asyncio
async def test_dynamic_tools_execute_and_readonly_steps_exclude_writes():
    name = "test_dynamic_echo"
    registry.register(ToolSpec(
        name, "Echo an argument", {
            "type": "object", "properties": {"value": {"type": "string"}},
            "required": ["value"],
        }, lambda value: value, "notes", parallel_safe=True,
    ))
    try:
        tools = {tool.name: tool for tool in build_langchain_tools("u", None, read_only=True)}
        assert await tools[name].ainvoke({"value": "actual-value"}) == "actual-value"
        assert "update_note_tool" not in tools
        assert "create_note_tool" not in tools
        assert "mark_reviewed_tool" not in tools
        assert tools["what_time_is_now"].args == {}
        parsed = plan.parse_plan_payload(json.dumps({
            "steps": [{"step": 1, "action": "echo", "tool": name}],
        }))
        assert parsed.steps[0].tool == name
    finally:
        registry.unregister(name)


@pytest.mark.asyncio
async def test_plan_step_passes_real_dependency_ids_to_agent():
    captured = []

    async def fake_react(question, *args, **kwargs):
        captured.append((question, kwargs))
        if "first-search" in kwargs["extra_system"]:
            result = "note_id=real-123, review_id=42"
        else:
            assert "note_id=real-123" in question
            assert "review_id=42" in question
            result = "updated"
        yield {"type": "stream_done", "full_response": result}

    execution = plan.ExecutionPlan("goal", [
        plan.PlanStep(1, "search", "search_notes_tool"),
        plan.PlanStep(2, "update matching note", "update_note_tool", [1]),
    ])

    async def make_plan(_):
        return execution

    async def by_step(question, *args, **kwargs):
        if "步骤 1" in kwargs["extra_system"]:
            kwargs["extra_system"] += " first-search"
        async for event in fake_react(question, *args, **kwargs):
            yield event

    plan.set_plan_fn(make_plan)
    react.set_react_streamer(by_step)
    events = [event async for event in plan.run_plan("request", "u", None, settings())]
    assert events[-1]["type"] == "stream_done"
    assert captured[0][1]["read_only"] is True
    assert captured[1][1]["read_only"] is False
    assert {"note_write", "note_read"} <= set(captured[1][1]["tool_groups"])


@pytest.mark.asyncio
async def test_plan_parallel_reads_serial_writes_and_cancellation(monkeypatch):
    active = set()
    max_reads = 0

    async def step_stream(step, *args, **kwargs):
        nonlocal max_reads
        if not registry.get(step.tool).parallel_safe:
            assert not active
        active.add(step.step)
        max_reads = max(max_reads, len(active))
        try:
            yield {"type": "tool_start", "name": step.tool}
            await asyncio.sleep(0.02)
            step.result = "ok"
        finally:
            active.remove(step.step)

    execution = plan.ExecutionPlan("goal", [
        plan.PlanStep(1, "read", "search_notes_tool"),
        plan.PlanStep(2, "read", "get_note_stats_tool"),
        plan.PlanStep(3, "write", "create_note_tool"),
        plan.PlanStep(4, "write", "update_note_tool"),
    ])

    async def make_plan(_):
        return execution

    monkeypatch.setattr(plan, "_execute_step", step_stream)
    plan.set_plan_fn(make_plan)
    events = [event async for event in plan.run_plan("request", "u", None, settings())]
    assert events[-1]["type"] == "stream_done"
    assert max_reads == 2
    assert not active
    stream = plan.run_plan("request", "u", None, settings())
    async with aclosing(stream):
        async for event in stream:
            if event["type"] == "tool_start":
                break
    assert not active


@pytest.mark.asyncio
@pytest.mark.parametrize("tool,expected", [
    ("search_notes_tool", "plan_fallback"), ("create_note_tool", "error"),
])
async def test_plan_does_not_replay_after_write(monkeypatch, tool, expected):
    async def make_plan(_):
        return plan.ExecutionPlan("goal", [plan.PlanStep(1, "action", tool)])

    async def failing_step(step, *args, **kwargs):
        yield {"type": "tool_start", "name": tool}
        yield {"type": "error", "content": "failure"}

    plan.set_plan_fn(make_plan)
    monkeypatch.setattr(plan, "_execute_step", failing_step)
    events = [event async for event in plan.run_plan("request", "u", None, settings())]
    assert events[-1]["type"] == expected
    assert not (expected == "error" and any(e["type"] == "plan_fallback" for e in events))


@pytest.mark.asyncio
@pytest.mark.parametrize("tool,retry", [
    ("search_notes_tool", True), ("update_note_tool", False), ("unknown_custom_write", False),
])
async def test_react_repairs_read_failure_only(monkeypatch, tool, retry):
    calls = []

    class FakeAgent:
        async def astream_events(self, payload, **kwargs):
            calls.append(payload)
            if len(calls) == 1:
                yield {"event": "on_tool_start", "name": tool}
                raise RuntimeError("first attempt failed")
            yield {"event": "on_chat_model_stream", "data": {"chunk": AIMessageChunk(content="fixed")}}

    monkeypatch.setattr(react, "_create_chat_model", lambda *args, **kwargs: object())
    monkeypatch.setattr(react, "_create_agent", lambda *args: FakeAgent())
    events = [event async for event in react.run_langchain_react(
        "question", "u", None, settings(reflection_l1_enabled=False),
    )]
    assert len(calls) == (2 if retry else 1)
    assert events[-1]["type"] == ("stream_done" if retry else "error")
    if retry:
        assert any(event["type"] == "response_replace" for event in events)
        assert "first attempt failed" not in calls[1]["messages"][-1].content
        assert "RuntimeError" in calls[1]["messages"][-1].content


@pytest.mark.asyncio
async def test_reflection_status_is_live_and_replaces_draft(monkeypatch):
    from app.ai_service import reflection

    checked = []

    async def critique(*args):
        checked.append(True)
        return reflection.ReflectionVerdict(False, "fix")

    async def refine(*args, **kwargs):
        return "corrected"

    reflection.set_critique_fn(critique)
    monkeypatch.setattr(reflection, "refine_answer", refine)
    config = settings(reflection_min_answer_chars=1)
    stream = reflection.stream_l1_refine("q", "draft", config)
    assert (await anext(stream))["stage"] == "checking"
    assert not checked
    assert (await anext(stream))["stage"] == "refining"
    assert checked
    await stream.aclose()

    class FakeAgent:
        async def astream_events(self, *args, **kwargs):
            yield {"event": "on_chat_model_stream", "data": {"chunk": AIMessageChunk(content="draft")}}

    monkeypatch.setattr(react, "_create_chat_model", lambda *args, **kwargs: object())
    monkeypatch.setattr(react, "_create_agent", lambda *args: FakeAgent())
    events = [event async for event in react.run_langchain_react("q", "u", None, config)]
    assert {"type": "response_replace", "content": "corrected"} in events
    assert events[-1]["full_response"] == "corrected"


class ToolCallingModel(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self

    def _stream(self, messages, stop=None, run_manager=None, **kwargs):
        message = self._generate(messages).generations[0].message
        yield ChatGenerationChunk(message=AIMessageChunk(
            content=message.content, tool_calls=message.tool_calls,
            usage_metadata=message.usage_metadata,
        ))


@pytest.mark.asyncio
async def test_real_langchain_tool_loop_records_each_model_call(monkeypatch):
    from app.ai_service import usage_callback

    calls = []
    records = []
    name = "test_real_tool"

    async def execute(value):
        calls.append(value)
        return "tool-result"

    async def record(**kwargs):
        records.append(kwargs)

    registry.register(ToolSpec(name, "Echo", {
        "type": "object", "properties": {"value": {"type": "string"}}, "required": ["value"],
    }, execute, "test", parallel_safe=True))
    model = ToolCallingModel(responses=[
        AIMessage(content="", tool_calls=[
            {"name": name, "args": {"value": "real-id"}, "id": "call-1", "type": "tool_call"},
        ], usage_metadata={"input_tokens": 17, "output_tokens": 4, "total_tokens": 21}),
        AIMessage(content="final", usage_metadata={
            "input_tokens": 29, "output_tokens": 3, "total_tokens": 32,
        }),
    ], callbacks=[usage_callback.ModelUsageCallback("test-model")])
    monkeypatch.setattr(usage_callback, "record_text_call", record)
    monkeypatch.setattr(react, "_create_chat_model", lambda *args, **kwargs: model)
    try:
        events = [event async for event in react.run_langchain_react(
            "question", "u", None, settings(reflection_l1_enabled=False),
            tool_groups=["test"], history=[{"role": "user", "content": "history"}],
        )]
        assert calls == ["real-id"]
        assert events[-1] == {"type": "stream_done", "full_response": "final"}
        assert len(records) == 2
        assert records[0]["usage_payload"]["usage"]["prompt_tokens"] == 17
        assert records[1]["usage_payload"]["usage"]["completion_tokens"] == 3
        assert "history" in records[0]["prompt"]
        assert "tool-result" in records[1]["prompt"]
    finally:
        registry.unregister(name)


@pytest.mark.asyncio
async def test_classifier_uses_role_model_and_thinking(monkeypatch):
    from app.ai_service.query_classifier import _llm_classify
    from app.rag import llm

    captured = {}

    async def complete(prompt, config, **kwargs):
        captured.update(model=config.llm_model, **kwargs)
        return '{"complexity":"complex","reason":"multi-step"}'

    monkeypatch.setattr(llm, "complete_openai_compatible", complete)
    result = await _llm_classify("query", settings(
        classifier_model="small-model", classifier_enable_thinking=True,
    ), plan_available=True)
    assert result.route == "plan_execute"
    assert captured == {"model": "small-model", "enable_thinking": True, "timeout": 15.0}


@pytest.mark.asyncio
async def test_usage_stages_do_not_leak_between_parallel_steps():
    from app.services import usage_service

    usage_service.set_trace_context(user_id="u", stage="chat")

    async def branch(stage):
        usage_service.set_trace_stage(stage)
        await asyncio.sleep(0)
        return usage_service.get_trace_context()["stage"]

    try:
        assert await asyncio.gather(branch("a"), branch("b")) == ["a", "b"]
        assert usage_service.get_trace_context()["stage"] == "chat"
    finally:
        usage_service.clear_trace_context()
