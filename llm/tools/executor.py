"""Выполнение tool-call: предложения файлов и запись в vault."""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from typing import Any

from core.file_manager import FileManager


@dataclass
class FileProposal:
    """Ожидает подтверждения пользователя."""

    id: str
    kind: str  # markdown | mermaid
    rel_path: str
    content: str
    summary: str


def _sanitize_filename(name: str, ext: str) -> str:
    name = name.strip().replace("\\", "/").split("/")[-1]
    if not name.lower().endswith(ext):
        name = f"{name}{ext}"
    name = re.sub(r'[<>:"|?*]', "_", name)
    return name or f"note{ext}"


def _join_path(folder: str, filename: str) -> str:
    folder = folder.strip().strip("/").replace("\\", "/")
    if folder:
        return f"{folder}/{filename}"
    return filename


def parse_tool_arguments(raw: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    return json.loads(raw or "{}")


def handle_tool_call(
    name: str,
    arguments: dict[str, Any],
    *,
    file_manager: FileManager | None,
) -> tuple[str, FileProposal | None]:
    """
    Обработать вызов инструмента.
    Возвращает (текст для LLM, предложение или None).
    """
    if not file_manager:
        return "Ошибка: хранилище не открыто. Попроси пользователя открыть vault (Ctrl+O).", None

    folder = str(arguments.get("folder") or "").strip()
    filename = str(arguments.get("filename") or "").strip()
    content = str(arguments.get("content") or "")

    if name == "propose_create_markdown_note":
        fname = _sanitize_filename(filename, ".md")
        rel = _join_path(folder, fname)
        proposal = FileProposal(
            id=str(uuid.uuid4()),
            kind="markdown",
            rel_path=rel,
            content=content,
            summary=f"Markdown: {rel}",
        )
        return (
            "Предложение отправлено пользователю. "
            "Дождись подтверждения в интерфейсе — файл пока не создан.",
            proposal,
        )

    if name == "propose_create_mermaid_diagram":
        fname = _sanitize_filename(filename, ".mermaid")
        body = content.strip()
        if body.startswith("```"):
            body = re.sub(r"^```mermaid\s*\n?", "", body, flags=re.IGNORECASE)
            body = re.sub(r"\n?```\s*$", "", body)
        rel = _join_path(folder, fname)
        proposal = FileProposal(
            id=str(uuid.uuid4()),
            kind="mermaid",
            rel_path=rel,
            content=body.strip() + "\n",
            summary=f"Mermaid: {rel}",
        )
        return (
            "Предложение диаграммы отправлено пользователю. "
            "Дождись подтверждения в интерфейсе.",
            proposal,
        )

    return f"Неизвестный инструмент: {name}", None


def apply_proposal(proposal: FileProposal, file_manager: FileManager) -> str:
    """Создать файл после подтверждения пользователя."""
    file_manager.create_note(proposal.rel_path)
    file_manager.write_file(proposal.rel_path, proposal.content)
    return proposal.rel_path
