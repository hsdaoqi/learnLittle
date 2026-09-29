"""把注册表里的工具转成 LangChain StructuredTool。

绑定当前用户的闭包仍走 bind_user_tools；这里只做 schema / 名称映射。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field, create_model

from app.ai_service.tool_registry import ToolSpec, registry
from app.ai_service.tools import bind_user_tools

_JSON_TYPES = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
}


def json_schema_to_model(name: str, schema: dict | None) -> type[BaseModel]:
    """把 OpenAI function parameters 转成 Pydantic 模型，给 StructuredTool 用。"""
    schema = schema or {}
    props = schema.get("properties") or {}
    required = set(schema.get("required") or [])
    fields: dict[str, Any] = {}
    for key, spec in props.items():
        spec = spec or {}
        py_type = _JSON_TYPES.get(spec.get("type"), str)
        description = spec.get("description") or ""
        if key in required:
            fields[key] = (py_type, Field(description=description))
        else:
            fields[key] = (py_type | None, Field(default=None, description=description))
    model_name = "".join(part.capitalize() for part in name.split("_")) + "Args"
    if not fields:
        return create_model(model_name)
    return create_model(model_name, **fields)


def spec_to_langchain_tool(spec: ToolSpec, bound: dict[str, Callable[..., Any]]):
    from langchain_core.tools import StructuredTool

    fn = bound.get(spec.name)
    schema = spec.parameters or {}
    props = schema.get("properties") or {}

    if not props:

        async def _run(_fn=fn, _name=spec.name) -> str:
            if _fn is None:
                return f"未知工具: {_name}"
            return await _fn()

        return StructuredTool.from_function(
            name=spec.name,
            description=spec.description,
            coroutine=_run,
        )

    model = json_schema_to_model(spec.name, schema)

    async def _run(_fn=fn, _name=spec.name, **kwargs: Any) -> str:
        if _fn is None:
            return f"未知工具: {_name}"
        cleaned = {key: value for key, value in kwargs.items() if value is not None}
        return await _fn(**cleaned)

    return StructuredTool.from_function(
        name=spec.name,
        description=spec.description,
        coroutine=_run,
        args_schema=model,
    )


def build_langchain_tools(
    user_id: str, session_factory, groups: list[str] | None = None
):
    bound = bind_user_tools(user_id, session_factory)
    return [spec_to_langchain_tool(spec, bound) for spec in registry.resolve(groups)]
