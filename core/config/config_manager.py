"""Глобальная конфигурация и пользовательские настройки приложения."""

import json
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_APP_CONFIG_PATH = _PROJECT_ROOT / "config" / "app_config.json"
_USER_SETTINGS_FILE = Path.home() / ".aihabchat" / "settings.json"


def _load_app_config() -> dict:
    if _APP_CONFIG_PATH.exists():
        return json.loads(_APP_CONFIG_PATH.read_text(encoding="utf-8"))
    return {}


_APP = _load_app_config()


class Config:
    """Константы и настройки приложения."""

    APP_NAME = _APP.get("app_name", "AiHabChat")
    APP_VERSION = _APP.get("app_version", "0.2.0")
    ORG_NAME = _APP.get("org_name", "AiHabChat")

    DEFAULT_WIDTH = _APP.get("default_width", 1200)
    DEFAULT_HEIGHT = _APP.get("default_height", 800)
    MIN_WIDTH = _APP.get("min_width", 800)
    MIN_HEIGHT = _APP.get("min_height", 600)

    SIDEBAR_MIN_WIDTH = _APP.get("sidebar_min_width", 180)
    SIDEBAR_DEFAULT_WIDTH = _APP.get("sidebar_default_width", 250)
    SIDEBAR_MAX_WIDTH = _APP.get("sidebar_max_width", 400)

    NOTE_EXTENSIONS = set(_APP.get("note_extensions", [".md", ".txt", ".markdown"]))

    RESOURCES_DIR = _PROJECT_ROOT / "resources"

    AUTOSAVE_INTERVAL = _APP.get("autosave_interval", 3000)

    _settings: dict = {}

    @classmethod
    def load_settings(cls) -> dict:
        """Загрузить настройки из файла."""
        if _USER_SETTINGS_FILE.exists():
            try:
                cls._settings = json.loads(
                    _USER_SETTINGS_FILE.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError):
                cls._settings = {}
        else:
            cls._settings = {}

        cls._settings.setdefault("theme", "light")
        cls._settings.setdefault("tab_size", 4)
        cls._settings.setdefault("show_line_numbers", True)
        cls._settings.setdefault("show_md_hints", True)
        cls._settings.setdefault("live_preview", True)
        cls._settings.setdefault(
            "llm_base_url", _APP.get("default_llm_base_url", "https://api.claudehub.fun")
        )
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
        _USER_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _USER_SETTINGS_FILE.write_text(
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
