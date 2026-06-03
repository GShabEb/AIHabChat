"""Модель диалога (заглушка)."""

from typing import Any


class Conversation:
    """Один диалог с LLM — в разработке."""

    def __init__(self) -> None:
        self.messages: list[dict[str, Any]] = []
