"""Долговременная память LLM (заглушка)."""


class MemoryManager:
    def remember(self, key: str, value: str) -> None:
        pass

    def recall(self, key: str) -> str | None:
        return None
