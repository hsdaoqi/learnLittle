"""上下文 Token 计数；实际历史配额由 chat_history.build_agent_history 计算。"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_OVERHEAD_PER_MESSAGE = 4


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


def count_message(content: str) -> int:
    return TokenCounter.count(content) + _OVERHEAD_PER_MESSAGE
