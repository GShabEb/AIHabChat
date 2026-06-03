"""Текстовый редактор Markdown-заметок."""

from PySide6.QtWidgets import QPlainTextEdit, QWidget
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QKeySequence, QShortcut


class EditorWidget(QPlainTextEdit):
    """Редактор Markdown с подсветкой и автосохранением."""

    content_changed = Signal()           # контент был изменён
    save_requested = Signal()            # Ctrl+S

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._current_path: str = ""
        self._modified: bool = False
        self._setup_ui()

    # ── свойства ──────────────────────────────────────────────

    @property
    def current_path(self) -> str:
        return self._current_path

    @current_path.setter
    def current_path(self, path: str) -> None:
        self._current_path = path

    @property
    def is_modified(self) -> bool:
        return self.document().isModified()

    # ── публичные методы ─────────────────────────────────────

    def load_content(self, path: str, text: str) -> None:
        """Загрузить текст заметки в редактор."""
        self._current_path = path
        self.setPlainText(text)
        self.document().setModified(False)

    def clear_editor(self) -> None:
        """Очистить редактор."""
        self._current_path = ""
        self.clear()
        self.document().setModified(False)

    # ── UI ────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        # Шрифт
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        # Отступы
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.setTabStopDistance(20)

        # Стиль
        self.setStyleSheet(
            "QPlainTextEdit {"
            "  background-color: #fafafa;"
            "  border: none;"
            "  padding: 8px;"
            "}"
        )

        # Сигналы
        self.textChanged.connect(self._on_text_changed)

        # Горячие клавиши
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_requested.emit)

    # ── слоты ─────────────────────────────────────────────────

    def _on_text_changed(self) -> None:
        self.content_changed.emit()