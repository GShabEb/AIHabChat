"""Предпросмотр Markdown / Mermaid через QWebEngine (как Obsidian Reading view)."""

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QTextBrowser, QWidget, QVBoxLayout

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEngineSettings

    _HAS_WEBENGINE = True
except ImportError:
    _HAS_WEBENGINE = False


class PreviewWidget(QWidget):
    """Рендер HTML с mermaid.js; fallback на QTextBrowser без WebEngine."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if _HAS_WEBENGINE:
            self._view = QWebEngineView(self)
            settings = self._view.settings()
            settings.setAttribute(
                QWebEngineSettings.LocalContentCanAccessRemoteUrls, True
            )
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        else:
            self._view = QTextBrowser(self)
            self._view.setOpenExternalLinks(True)

        layout.addWidget(self._view)

    def set_html(self, html: str) -> None:
        if _HAS_WEBENGINE:
            self._view.setHtml(html, QUrl("https://local.aihabchat/"))
        else:
            self._view.setHtml(html)

    def clear_preview(self) -> None:
        if _HAS_WEBENGINE:
            self._view.setHtml("")
        else:
            self._view.clear()
