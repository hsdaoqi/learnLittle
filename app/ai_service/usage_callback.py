"""Record each model invocation, including tool-loop input and provider usage."""

import json
import time

from langchain_core.callbacks import AsyncCallbackHandler

from app.services.usage_service import record_text_call


class ModelUsageCallback(AsyncCallbackHandler):
    def __init__(self, model: str, stage: str = "agent"):
        self.model = model
        self.stage = stage
        self.runs: dict = {}

    async def on_chat_model_start(self, serialized, messages, *, run_id, **kwargs):
        params = kwargs.get("invocation_params") or {}
        text = json.dumps(
            {
                "messages": [
                    [message.model_dump() for message in batch] for batch in messages
                ],
                "tools": params.get("tools") or params.get("functions") or [],
            },
            ensure_ascii=False, default=str,
        )
        self.runs[run_id] = (time.perf_counter(), text)

    async def on_llm_end(self, response, *, run_id, **kwargs):
        started, prompt = self.runs.pop(run_id, (time.perf_counter(), ""))
        usage = (response.llm_output or {}).get("token_usage") or {}
        completion = []
        metadata_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        for batch in response.generations:
            for generation in batch:
                message = getattr(generation, "message", None)
                completion.append(str(getattr(generation, "text", "")))
                if message is not None:
                    metadata = getattr(message, "usage_metadata", None) or {}
                    metadata_usage["prompt_tokens"] += metadata.get("input_tokens", 0)
                    metadata_usage["completion_tokens"] += metadata.get("output_tokens", 0)
                    if getattr(message, "tool_calls", None):
                        completion.append(json.dumps(message.tool_calls, ensure_ascii=False))
        if not usage and any(metadata_usage.values()):
            usage = metadata_usage
        await record_text_call(
            stage=self.stage, model=self.model, prompt=prompt,
            completion="".join(completion), usage_payload={"usage": usage},
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    async def on_llm_error(self, error, *, run_id, **kwargs):
        started, prompt = self.runs.pop(run_id, (time.perf_counter(), ""))
        await record_text_call(
            stage=self.stage, model=self.model, prompt=prompt,
            success=False, error=type(error).__name__,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
