"""Виджет предпросмотра Markdown → HTML."""

from PySide6.QtWidgets import QTextBrowser
from PySide6.QtCore import Qt


class PreviewWidget(QTextBrowser):
    """Предпросмотр Markdown в виде HTML."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def set_html(self, html: str) -> None:
        """Отобразить HTML-контент."""
        self.setHtml(html)

    def clear_preview(self) -> None:
        """Очистить предпросмотр."""
        self.clear()

    # ── UI ────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setOpenExternalLinks(True)
        self.setStyleSheet(
            "QTextBrowser {"
            "  background-color: #ffffff;"
            "  border: none;"
            "  padding: 8px;"
            "}"
        )