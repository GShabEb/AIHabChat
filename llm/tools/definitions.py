"""Схемы инструментов (OpenAI function calling)."""

from __future__ import annotations

from typing import Any

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "propose_create_markdown_note",
            "description": (
                "Подготовить создание Markdown-заметки (.md) в хранилище. "
                "Файл НЕ создаётся сразу — пользователь подтвердит в интерфейсе. "
                "Вызывай ТОЛЬКО после явного согласия пользователя (да/создай/ок)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Имя файла, например «План проекта.md»",
                    },
                    "content": {
                        "type": "string",
                        "description": "Полный текст заметки в Markdown",
                    },
                    "folder": {
                        "type": "string",
                        "description": "Подпапка в хранилище (необязательно)",
                        "default": "",
                    },
                },
                "required": ["filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "propose_create_mermaid_diagram",
            "description": (
                "Подготовить создание диаграммы Mermaid (.mermaid) в хранилище. "
                "Файл НЕ создаётся сразу — пользователь подтвердит в интерфейсе. "
                "Вызывай ТОЛЬКО после явного согласия пользователя. "
                "В content — только код Mermaid, без ```mermaid и без markdown."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Имя файла, например «Архитектура.mermaid»",
                    },
                    "content": {
                        "type": "string",
                        "description": "Исходник диаграммы Mermaid (graph TD, flowchart и т.д.)",
                    },
                    "folder": {
                        "type": "string",
                        "description": "Подпапка в хранилище (необязательно)",
                        "default": "",
                    },
                },
                "required": ["filename", "content"],
            },
        },
    },
]

SYSTEM_PROMPT = """Ты — ассистент в приложении AiHabChat для заметок Markdown и диаграмм Mermaid.

Обычное общение: отвечай по делу, на языке пользователя.

Создание файлов в хранилище:
1. Сначала предложи содержание и имя файла и СПРОСИ: «Создать файл?» / «Сохранить в хранилище?»
2. Только после явного согласия («да», «создай», «ок», «сохрани») вызывай инструмент propose_create_markdown_note или propose_create_mermaid_diagram.
3. Инструмент лишь готовит предложение — файл появится только после подтверждения пользователем в интерфейсе.
4. Не вызывай инструменты создания файлов в каждом ответе и не создавай файлы «молча».

Markdown-заметки: оформляй заголовками, списками, структурой.
Mermaid: валидный синтаксис (graph TD, flowchart LR и т.д.), без обёртки ``` в поле content."""
