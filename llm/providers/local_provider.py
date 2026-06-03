"""Локальный провайдер (заглушка)."""


class LocalProvider:
    """Произвольный локальный OpenAI-совместимый endpoint — в разработке."""

    def __init__(self, base_url: str = "http://127.0.0.1:8080") -> None:
        self.base_url = base_url
