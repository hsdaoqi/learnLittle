"""Token 预算：给系统提示、检索切片、当前问题和历史各留配额。

计数对齐原项目 TokenCounter：tiktoken cl100k_base，加载失败则 len(text)//2。
历史配额 = 窗口总容量 - 固定预留 - 检索占用。尚未检索时按 RAG 上限预留，检索后按实际。

原项目 allocate() 把 rag_context_max 算进固定项后又减一次实际 RAG，这里只减一次。
摘要压缩、Agent scratchpad、图片 token 下一阶段再加。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.config import Settings

logger = logging.getLogger(__name__)

_OVERHEAD_PER_MESSAGE = 4
_SEQUENCE_OVERHEAD = 2


class TokenCounter:
    """基于 tiktoken 的计数器；编码器按名称缓存，失败则字符估算。"""

    _encoders: dict = {}

    @classmethod
    def get_encoder(cls, model_name: str = "cl100k_base"):
        if model_name not in cls._encoders:
            try:
                import tiktoken

                cls._encoders[model_name] = tiktoken.get_encoding(model_name)
            except Exception as exc:
                logger.warning("tiktoken 加载失败，回退到字符估算: %s", exc)
                cls._encoders[model_name] = None
        return cls._encoders[model_name]

    @classmethod
    def reset_encoders(cls) -> None:
        cls._encoders.clear()

    @classmethod
    def count(cls, text: str, model_name: str = "cl100k_base") -> int:
        if not text:
            return 0
        encoder = cls.get_encoder(model_name)
        if encoder:
            return len(encoder.encode(text))
        return max(1, len(text) // 2)

    @classmethod
    def count_messages(cls, messages: list, model_name: str = "cl100k_base") -> int:
        total = 0
        for msg in messages:
            total += _OVERHEAD_PER_MESSAGE
            if hasattr(msg, "content"):
                content = msg.content or ""
            elif isinstance(msg, dict):
                content = msg.get("content", "") or ""
            else:
                content = str(msg)
            total += cls.count(content, model_name)
        total += _SEQUENCE_OVERHEAD
        return total


def count_text(text: str) -> int:
    return TokenCounter.count(text)


def count_message(content: str) -> int:
    return TokenCounter.count(content) + _OVERHEAD_PER_MESSAGE


def count_messages(messages: list) -> int:
    return TokenCounter.count_messages(messages)


@dataclass(frozen=True)
class TokenBudget:
    model_context_size: int = 32768
    system_prompt: int = 500
    rag_context_max: int = 2000
    current_input_estimate: int = 300
    safety_margin: int = 1000
    history_min_tokens: int = 500
    agent_scratchpad_reserve: int = 0
    summary_reserve: int = 0

    @classmethod
    def from_settings(cls, settings: Settings) -> "TokenBudget":
        return cls(
            model_context_size=settings.token_model_context_size,
            system_prompt=settings.token_system_prompt,
            rag_context_max=settings.token_rag_context_max,
            current_input_estimate=settings.token_current_input_estimate,
            safety_margin=settings.token_safety_margin,
            history_min_tokens=settings.token_history_min,
            agent_scratchpad_reserve=settings.token_agent_scratchpad_reserve,
            summary_reserve=settings.token_summary_reserve,
        )

    @property
    def fixed_budget(self) -> int:
        return (
                self.system_prompt
                + self.current_input_estimate
                + self.safety_margin
                + self.agent_scratchpad_reserve
                + self.summary_reserve
        )

    def rag_tokens(self, rag_text: str | None) -> int:
        """检索占用。None 表示尚未检索，按上限预留。"""
        if rag_text is None:
            return self.rag_context_max
        return min(TokenCounter.count(rag_text), self.rag_context_max)

    def history_quota(self, rag_text: str | None = None) -> int:
        remaining = self.model_context_size - self.fixed_budget - self.rag_tokens(rag_text)
        return max(self.history_min_tokens, remaining)
