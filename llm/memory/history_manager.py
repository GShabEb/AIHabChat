"""Управление историей чата (заглушка)."""


class HistoryManager:
    def load(self, session_id: str) -> list:
        return []

    def save(self, session_id: str, messages: list) -> None:
        pass
