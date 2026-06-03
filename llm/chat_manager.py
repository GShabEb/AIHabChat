"""Менеджер классического чата с LLM и инструментами vault."""

from __future__ import annotations

import json
from typing import Any, Callable

from app.config import Config
from core.file_manager import FileManager
from llm.client import LLMClientError, chat_completion, fetch_models
from llm.tools.definitions import SYSTEM_PROMPT, TOOL_DEFINITIONS
from llm.tools.executor import FileProposal, apply_proposal, handle_tool_call, parse_tool_arguments


class ChatManager:
    """История, запросы к API, цикл tool-calling, предложения файлов."""

    MAX_TOOL_ROUNDS = 6

    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []
        self._file_manager: FileManager | None = None
        self._pending_proposals: dict[str, FileProposal] = {}
        self._system_injected = False

    @property
    def history(self) -> list[dict[str, Any]]:
        return list(self._history)

    @property
    def pending_proposals(self) -> list[FileProposal]:
        return list(self._pending_proposals.values())

    def set_file_manager(self, fm: FileManager | None) -> None:
        self._file_manager = fm

    def clear_history(self) -> None:
        self._history.clear()
        self._system_injected = False
        self._pending_proposals.clear()

    def is_configured(self) -> bool:
        return bool(
            Config.get("llm_api_key", "").strip()
            and Config.get("llm_model", "").strip()
            and Config.get("llm_base_url", "").strip()
        )

    def fetch_models_list(self) -> list[str]:
        base = Config.get("llm_base_url", "https://api.claudehub.fun")
        key = Config.get("llm_api_key", "")
        models = fetch_models(base, key)
        Config.set("llm_models", models)
        return models

    def add_proposal(self, proposal: FileProposal) -> None:
        self._pending_proposals[proposal.id] = proposal

    def get_proposal(self, proposal_id: str) -> FileProposal | None:
        return self._pending_proposals.get(proposal_id)

    def confirm_proposal(self, proposal_id: str) -> str:
        proposal = self._pending_proposals.pop(proposal_id, None)
        if not proposal:
            raise ValueError("Предложение не найдено")
        if not self._file_manager:
            raise ValueError("Хранилище не открыто")
        path = apply_proposal(proposal, self._file_manager)
        self._history.append({
            "role": "user",
            "content": f"[Система] Пользователь подтвердил создание файла: {path}",
        })
        return path

    def reject_proposal(self, proposal_id: str) -> None:
        proposal = self._pending_proposals.pop(proposal_id, None)
        if proposal:
            self._history.append({
                "role": "user",
                "content": f"[Система] Пользователь отклонил создание файла: {proposal.rel_path}",
            })

    def send(
        self,
        user_message: str,
        *,
        on_status: Callable[[str], None] | None = None,
    ) -> str:
        """
        Отправить сообщение, выполнить цикл tool-calling, вернуть финальный ответ.
        """
        if not self.is_configured():
            raise LLMClientError(
                "Укажите URL провайдера, API-ключ и модель в Настройках → LLM."
            )

        self._ensure_system()
        self._history.append({"role": "user", "content": user_message})

        base = Config.get("llm_base_url", "https://api.claudehub.fun")
        key = Config.get("llm_api_key", "")
        model = Config.get("llm_model", "")

        proposals_collected: list[FileProposal] = []

        for round_i in range(self.MAX_TOOL_ROUNDS):
            if on_status:
                on_status("Думаю…" if round_i == 0 else "Обрабатываю инструменты…")

            response = chat_completion(
                base, key, model, self._build_messages(), tools=TOOL_DEFINITIONS
            )

            if response.tool_calls:
                assistant_msg: dict[str, Any] = {
                    "role": "assistant",
                    "content": response.content or "",
                    "tool_calls": response.tool_calls,
                }
                self._history.append(assistant_msg)

                for tc in response.tool_calls:
                    fn = tc.get("function") or {}
                    name = fn.get("name", "")
                    try:
                        args = parse_tool_arguments(fn.get("arguments", "{}"))
                    except json.JSONDecodeError:
                        args = {}
                    tool_text, proposal = handle_tool_call(
                        name, args, file_manager=self._file_manager
                    )
                    if proposal:
                        self._pending_proposals[proposal.id] = proposal
                        proposals_collected.append(proposal)
                    self._history.append({
                        "role": "tool",
                        "tool_call_id": tc.get("id", ""),
                        "content": tool_text,
                    })
                continue

            text = (response.content or "").strip()
            if not text and proposals_collected:
                text = (
                    "Подготовил предложение по файлу — подтвердите или отклоните "
                    "кнопками под сообщением."
                )
            if not text:
                text = "(Пустой ответ модели)"
            self._history.append({"role": "assistant", "content": text})
            return text

        raise LLMClientError("Слишком много вызовов инструментов подряд")

    def _ensure_system(self) -> None:
        if self._system_injected:
            return
        self._history.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        self._system_injected = True

    def _build_messages(self) -> list[dict[str, Any]]:
        """Сообщения для API (без лишних полей)."""
        out: list[dict[str, Any]] = []
        for msg in self._history:
            m: dict[str, Any] = {"role": msg["role"]}
            if msg.get("content") is not None:
                m["content"] = msg["content"]
            if msg.get("tool_calls"):
                m["tool_calls"] = msg["tool_calls"]
            if msg.get("tool_call_id"):
                m["tool_call_id"] = msg["tool_call_id"]
            out.append(m)
        return out
