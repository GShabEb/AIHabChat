"""Парсер Markdown → HTML для предпросмотра заметок."""

import re
import html
import markdown


class MermaidExtension(markdown.Extension):
    """Расширение для рендеринга блок-схем Mermaid."""

    def extendMarkdown(self, md: markdown.Markdown) -> None:
        md.preprocessors.register(MermaidPreprocessor(md), "mermaid", 175)


class MermaidPreprocessor(markdown.preprocessors.Preprocessor):
    """Препроцессор: находит блоки ```mermaid ... ``` и заменяет на HTML-заглушку."""

    MERMAID_RE = re.compile(r'^```mermaid\s*\n(.*?)^```', re.MULTILINE | re.DOTALL)

    def run(self, lines: list[str]) -> list[str]:
        text = "\n".join(lines)
        # Заменяем mermaid-блоки на div с классом mermaid
        def _replace(match):
            code = match.group(1).strip()
            # Экранируем HTML-спецсимволы
            code = html.escape(code)
            return (
                '<div class="mermaid-diagram" style="'
                'background:#f8f9fa; border:1px solid #ddd; border-radius:4px; '
                'padding:12px; margin:8px 0; font-family:monospace; white-space:pre; '
                'font-size:13px; color:#333; overflow-x:auto;">'
                f'<div style="color:#999; font-size:11px; margin-bottom:4px;">Схема Mermaid:</div>'
                f'{code}</div>'
            )
        text = self.MERMAID_RE.sub(_replace, text)
        return text.split("\n")


class MarkdownParser:
    """Конвертация Markdown в HTML с расширениями."""

    def __init__(self) -> None:
        self._extensions = [
            "fenced_code",
            "codehilite",
            "tables",
            "toc",
            "nl2br",
            "sane_lists",
            MermaidExtension(),
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
            "h1, h2, h3, h4, h5, h6 { margin-top: 16px; margin-bottom: 8px; }"
            "hr { border: none; border-top: 1px solid #ddd; margin: 16px 0; }"
            "</style></head><body>"
            f"{body}</body></html>"
        )

    def get_preview_html_dark(self, text: str) -> str:
        """Вернуть полный HTML-документ для тёмной темы."""
        body = self.to_html(text)
        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<style>"
            "body { font-family: -apple-system, 'Segoe UI', sans-serif; "
            "       margin: 16px; line-height: 1.6; color: #ddd; background: #1e1e1e; }"
            "pre { background: #2d2d2d; padding: 12px; border-radius: 4px; overflow-x: auto; }"
            "code { background: #333; padding: 2px 4px; border-radius: 3px; color: #e0e0e0; }"
            "table { border-collapse: collapse; width: 100%; }"
            "th, td { border: 1px solid #444; padding: 8px; text-align: left; }"
            "blockquote { border-left: 3px solid #555; margin: 0; padding-left: 12px; color: #999; }"
            "img { max-width: 100%; }"
            "h1, h2, h3, h4, h5, h6 { margin-top: 16px; margin-bottom: 8px; color: #e0e0e0; }"
            "hr { border: none; border-top: 1px solid #444; margin: 16px 0; }"
            "a { color: #64b5f6; }"
            "</style></head><body>"
            f"{body}</body></html>"
        )