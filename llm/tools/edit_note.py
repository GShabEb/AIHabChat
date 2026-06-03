"""Инструмент редактирования заметок (заглушка)."""

from typing import Any


EDIT_TOOL_DEFINITIONS: list[dict[str, Any]] = []


def handle_edit_tool(name: str, arguments: dict[str, Any]) -> str:
    return f"Инструмент {name} не реализован"
