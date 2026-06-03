"""Глобальная конфигурация приложения."""

from pathlib import Path


class Config:
    """Константы и настройки приложения."""

    APP_NAME = "AiHabChat"
    APP_VERSION = "0.1.0"
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