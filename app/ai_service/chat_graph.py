"""Classification and ReAct/Plan routing live in one cancellable graph."""

import asyncio
from contextlib import aclosing
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.ai_service.plan_execute import plan_available, run_plan
from app.ai_service.query_classifier import classify_query
from app.ai_service.react_agent import get_react_streamer, run_react
from app.ai_service.runner import run_agent, should_use_agent
from app.rag.note_cards import visible_question
from app.services import usage_service


class ChatState(TypedDict):
    route: str


async def stream_chat_graph(
    question, user_id, session_factory, settings, *,
    history, summary, rag_context, enable_thinking, fallback_answer,
):
    queue: asyncio.Queue = asyncio.Queue(maxsize=128)
    finished = object()
    kwargs = dict(
        history=history, summary=summary, rag_context=rag_context,
        enable_thinking=enable_thinking,
    )

    async def classify(state):
        result = await classify_query(
            visible_question(question), settings,
            plan_available=settings.agent_enabled and plan_available(settings),
        )
        await queue.put({
            "type": "routing", "complexity": result.complexity,
            "route": result.route, "classifier_source": result.source,
        })
        await queue.put({
            "type": "thinking", "stage": "classify", "content": result.thinking_text(),
        })
        return {"route": result.route}

    async def forward(stream):
        async with aclosing(stream):
            async for event in stream:
                await queue.put(event)

    async def react(state):
        usage_service.set_trace_stage("agent")
        if settings.agent_enabled and (settings.llm_api_key or get_react_streamer()):
            await forward(run_react(question, user_id, session_factory, settings, **kwargs))
        elif should_use_agent(visible_question(question), settings):
            history_text = "\n".join(f"{m['role']}: {m['content']}" for m in history)
            await forward(run_agent(question, user_id, session_factory, settings, history_text))
        else:
            await queue.put({"type": "response", "content": fallback_answer})
        return {}

    async def plan(state):
        stream = run_plan(question, user_id, session_factory, settings, **kwargs)
        async with aclosing(stream):
            async for event in stream:
                await queue.put(event)
                if event["type"] == "plan_fallback":
                    return {"route": "react"}
        return {"route": "complete"}

    graph = StateGraph(ChatState)
    graph.add_node("classify", classify)
    graph.add_node("react", react)
    graph.add_node("plan", plan)
    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify", lambda state: "plan" if state["route"] == "plan_execute" else "react",
        {"plan": "plan", "react": "react"},
    )
    graph.add_conditional_edges(
        "plan", lambda state: state["route"],
        {"react": "react", "complete": END},
    )
    graph.add_edge("react", END)

    async def run():
        try:
            await graph.compile().ainvoke({"route": ""})
        except Exception:
            await queue.put({"type": "error", "content": "生成失败，请稍后重试"})
        finally:
            if not asyncio.current_task().cancelling():
                await queue.put(finished)

    task = asyncio.create_task(run())
    try:
        while True:
            event = await queue.get()
            if event is finished:
                break
            yield event
        await task
    finally:
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)
