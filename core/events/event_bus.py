"""Шина событий приложения (заглушка)."""

from typing import Any, Callable


class EventBus:
    """Простая pub/sub шина — в разработке."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = {}

    def subscribe(self, event: str, handler: Callable) -> None:
        self._handlers.setdefault(event, []).append(handler)

    def publish(self, event: str, payload: Any = None) -> None:
        for handler in self._handlers.get(event, []):
            handler(payload)
