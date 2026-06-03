"""Глобальная конфигурация и пользовательские настройки приложения."""

import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".aihabchat" / "settings.json"


class Config:
    """Константы и настройки приложения."""

    APP_NAME = "AiHabChat"
    APP_VERSION = "0.2.0"
    ORG_NAME = "AiHabChat"

    # Размеры окна по умолчанию
    DEFAULT_WIDTH = 1200
    DEFAULT_HEIGHT = 800
    MIN_WIDTH = 800
    MIN_HEIGHT = 600

    # Ширина боковой панели с деревом файлов
    SIDEBAR_MIN_WIDTH = 180
    SIDEBAR_DEFAULT_WIDTH = 250
    SIDEBAR_MAX_WIDTH = 400

    # Поддерживаемые расширения
    NOTE_EXTENSIONS = {".md", ".txt", ".markdown"}

    # Путь к ресурсам
    RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"

    # Интервал автосохранения (мс)
    AUTOSAVE_INTERVAL = 3000

    # ── пользовательские настройки ────────────────────────────

    _settings: dict = {}

    @classmethod
    def load_settings(cls) -> dict:
        """Загрузить настройки из файла."""
        if CONFIG_FILE.exists():
            try:
                cls._settings = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                cls._settings = {}
        else:
            cls._settings = {}

        # значения по умолчанию
        cls._settings.setdefault("theme", "light")
        cls._settings.setdefault("tab_size", 4)
        cls._settings.setdefault("show_line_numbers", True)
        cls._settings.setdefault("show_md_hints", True)
        cls._settings.setdefault("live_preview", True)
        cls._settings.setdefault("llm_base_url", "https://api.claudehub.fun")
        url = cls._settings.get("llm_base_url", "")
        if "://app.claudehub.fun" in url:
            cls._settings["llm_base_url"] = url.replace(
                "://app.claudehub.fun", "://api.claudehub.fun"
            )
        cls._settings.setdefault("llm_api_key", "")
        cls._settings.setdefault("llm_model", "")
        cls._settings.setdefault("llm_models", [])
        return cls._settings

    @classmethod
    def save_settings(cls) -> None:
        """Сохранить настройки в файл."""
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(cls._settings, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def get(cls, key: str, default=None):
        return cls._settings.get(key, default)

    @classmethod
    def set(cls, key: str, value) -> None:
        cls._settings[key] = value
        cls.save_settings()