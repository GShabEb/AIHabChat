"""OpenAI-совместимый HTTP-клиент для агрегаторов LLM (ClaudeHub и др.)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class LLMClientError(Exception):
    """Ошибка запроса к провайдеру."""


@dataclass
class ChatResponse:
    content: str | None
    tool_calls: list[dict[str, Any]]
    raw_message: dict[str, Any]


def normalize_api_root(base_url: str) -> str:
    """
    Привести URL провайдера к корню API (/v1).
    Примеры:
      https://api.claudehub.fun -> https://api.claudehub.fun/v1
      https://api.claudehub.fun/v1 -> без изменений
      https://app.claudehub.fun -> api.claudehub.fun/v1 (веб ≠ API)
    """
    base = (base_url or "").strip().rstrip("/")
    if not base:
        raise LLMClientError("Не указан URL провайдера")
    # ClaudeHub: сайт app.*, API api.*
    if "://app.claudehub.fun" in base:
        base = base.replace("://app.claudehub.fun", "://api.claudehub.fun")
    if base.endswith("/v1"):
        return base
    return f"{base}/v1"


def fetch_models(base_url: str, api_key: str, timeout: float = 30.0) -> list[str]:
    """GET /v1/models — список id моделей."""
    root = normalize_api_root(base_url)
    url = f"{root}/models"
    data = _request_json("GET", url, api_key, timeout=timeout)
    models: list[str] = []
    for item in data.get("data", []):
        mid = item.get("id")
        if mid:
            models.append(str(mid))
    if not models and isinstance(data.get("models"), list):
        models = [str(m) for m in data["models"]]
    if not models:
        raise LLMClientError(
            "Список моделей пуст. Проверьте URL (обычно …/v1) и API-ключ."
        )
    return sorted(models, key=str.lower)


def chat_completion(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]] | None = None,
    timeout: float = 120.0,
) -> ChatResponse:
    """POST /v1/chat/completions (без стриминга)."""
    root = normalize_api_root(base_url)
    url = f"{root}/chat/completions"
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    data = _request_json("POST", url, api_key, body=payload, timeout=timeout)
    choices = data.get("choices") or []
    if not choices:
        raise LLMClientError("Пустой ответ от API")
    message = choices[0].get("message") or {}
    tool_calls = message.get("tool_calls") or []
    return ChatResponse(
        content=message.get("content"),
        tool_calls=tool_calls,
        raw_message=message,
    )


def _request_json(
    method: str,
    url: str,
    api_key: str,
    *,
    body: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key.strip()}",
    }
    data_bytes = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        raise LLMClientError(f"HTTP {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise LLMClientError(f"Сеть: {e.reason}") from e

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise LLMClientError("Ответ не JSON — проверьте URL API") from e
