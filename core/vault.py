"""Управление хранилищем (vault) — выбор, создание, хранение пути root-папки."""

import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".aihabchat" / "config.json"


class Vault:
    """Представляет хранилище заметок (root-папку пользователя)."""

    def __init__(self) -> None:
        self._path: Path | None = None
        self._load_config()

    # ── свойства ──────────────────────────────────────────────

    @property
    def path(self) -> Path | None:
        return self._path

    @property
    def is_open(self) -> bool:
        return self._path is not None and self._path.exists()

    # ── публичные методы ─────────────────────────────────────

    def open(self, path: str | Path) -> None:
        """Установить root-папку хранилища."""
        self._path = Path(path).resolve()
        self._path.mkdir(parents=True, exist_ok=True)
        self._save_config()

    def close(self) -> None:
        """Закрыть хранилище."""
        self._path = None
        self._save_config()

    # ── приватные методы ─────────────────────────────────────

    def _load_config(self) -> None:
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                vault_path = data.get("vault_path")
                if vault_path and Path(vault_path).exists():
                    self._path = Path(vault_path)
            except (json.JSONDecodeError, OSError):
                pass

    def _save_config(self) -> None:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        data: dict = {"vault_path": str(self._path) if self._path else None}
        CONFIG_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )