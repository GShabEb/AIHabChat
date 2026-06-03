import json
from pathlib import Path

from gui.themes.styles import THEME_DARK, THEME_LIGHT

_THEMES_JSON = Path(__file__).resolve().parent.parent.parent / "config" / "themes.json"


def load_theme_metadata() -> dict:
    if _THEMES_JSON.exists():
        return json.loads(_THEMES_JSON.read_text(encoding="utf-8"))
    return {"themes": [], "default": "light"}


def get_stylesheet(theme_id: str) -> str:
    if theme_id == "dark":
        return THEME_DARK
    return THEME_LIGHT


__all__ = ["THEME_LIGHT", "THEME_DARK", "load_theme_metadata", "get_stylesheet"]
