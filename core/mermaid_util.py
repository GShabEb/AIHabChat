"""Извлечение и подготовка исходников Mermaid (как в Obsidian)."""

import re
from pathlib import Path

MERMAID_STANDALONE_SUFFIXES = (".mermaid", ".mmd")
MERMAID_MARKDOWN_SUFFIX = ".mermaid.md"
MERMAID_FENCE_RE = re.compile(
    r"^```mermaid\s*\n(.*?)^```",
    re.MULTILINE | re.DOTALL,
)


def is_standalone_mermaid_file(path: str) -> bool:
    """Файл с чистым кодом диаграммы (.mermaid / .mmd)."""
    lower = path.lower()
    return lower.endswith(MERMAID_STANDALONE_SUFFIXES)


def is_mermaid_note(path: str) -> bool:
    """Любая заметка с диаграммой: отдельный файл или .mermaid.md."""
    lower = path.lower()
    return (
        is_standalone_mermaid_file(path)
        or lower.endswith(MERMAID_MARKDOWN_SUFFIX)
    )


def extract_mermaid_source(text: str, path: str = "") -> str | None:
    """
    Вернуть код диаграммы без обёртки ```mermaid.
    Для обычного .md — None, если блоков нет.
    """
    if is_standalone_mermaid_file(path):
        return text.strip() or None

    match = MERMAID_FENCE_RE.search(text)
    if match:
        return match.group(1).strip() or None

    if path.lower().endswith(MERMAID_MARKDOWN_SUFFIX):
        stripped = text.strip()
        if stripped and "```" not in stripped:
            return stripped

    return None


def default_mermaid_template() -> str:
    """Шаблон новой диаграммы (raw, без fence — как Obsidian Mermaid View)."""
    return "graph TD\n    A[Начало] --> B[Конец]\n"
