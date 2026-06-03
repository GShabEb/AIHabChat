"""Парсер Markdown → HTML для предпросмотра заметок."""

import markdown


class MarkdownParser:
    """Конвертация Markdown в HTML с базовыми расширениями."""

    def __init__(self) -> None:
        self._extensions = [
            "fenced_code",
            "codehilite",
            "tables",
            "toc",
            "nl2br",
            "sane_lists",
        ]
        self._extension_configs = {
            "codehilite": {"css_class": "highlight"},
        }

    def to_html(self, text: str) -> str:
        """Преобразовать Markdown-строку в HTML."""
        return markdown.markdown(
            text,
            extensions=self._extensions,
            extension_configs=self._extension_configs,
        )

    def get_preview_html(self, text: str) -> str:
        """Вернуть полный HTML-документ для отображения в QTextBrowser."""
        body = self.to_html(text)
        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<style>"
            "body { font-family: -apple-system, 'Segoe UI', sans-serif; "
            "       margin: 16px; line-height: 1.6; color: #222; }"
            "pre { background: #f5f5f5; padding: 12px; border-radius: 4px; overflow-x: auto; }"
            "code { background: #f0f0f0; padding: 2px 4px; border-radius: 3px; }"
            "table { border-collapse: collapse; width: 100%; }"
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }"
            "blockquote { border-left: 3px solid #ccc; margin: 0; padding-left: 12px; color: #666; }"
            "img { max-width: 100%; }"
            "</style></head><body>"
            f"{body}</body></html>"
        )