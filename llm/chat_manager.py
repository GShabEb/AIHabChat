"""Менеджер чата — заготовка для будущей интеграции с LLM."""

from typing import Generator


class ChatManager:
    """
    Заготовка менеджера чата.

    В будущем будет управлять:
    - подключением к различным LLM-провайдерам
    - историей сообщений
    - режимами чата (классический / полноценный)
    - инструментами (tools) для LLM
    """

    def __init__(self) -> None:
        self._history: list[dict] = []
        self._mode: str = "classic"  # "classic" | "full"

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        if value in ("classic", "full"):
            self._mode = value

    @property
    def history(self) -> list[dict]:
        return list(self._history)

    def add_message(self, role: str, content: str) -> None:
        """Добавить сообщение в историю. role: 'user' | 'assistant' | 'system'."""
        self._history.append({"role": role, "content": content})

    def clear_history(self) -> None:
        """Очистить историю сообщений."""
        self._history.clear()

    def send(self, message: str) -> str:
        """
        Отправить сообщение и получить ответ.

        TODO: реализовать подключение к LLM-провайдерам.
        """
        self.add_message("user", message)
        # Заглушка
        response = "Чат находится в разработке. Скоро здесь появится LLM!"
        self.add_message("assistant", response)
        return response

    def send_stream(self, message: str) -> Generator[str, None, None]:
        """
        Потоковая отправка сообщения.

        TODO: реализовать стриминг от LLM-провайдера.
        """
        self.add_message("user", message)
        yield "Чат находится в разработке."
        self.add_message("assistant", "Чат находится в разработке.")