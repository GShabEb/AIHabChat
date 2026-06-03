"""Стриминг ответов LLM (заглушка)."""

from typing import Any, Iterator


def stream_chat_completion(*args: Any, **kwargs: Any) -> Iterator[str]:
    raise NotImplementedError("Streaming not implemented")
    yield ""
