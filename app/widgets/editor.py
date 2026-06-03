"""Текстовый редактор Markdown-заметок с нумерацией строк и подсветкой."""

from PySide6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout
from PySide6.QtCore import Signal, Qt, QRect, QSize
from PySide6.QtGui import (
    QFont,
    QKeySequence,
    QShortcut,
    QPainter,
    QColor,
    QTextFormat,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
)

from app.config import Config


# ── Подсветка синтаксиса Markdown ────────────────────────────

class MarkdownHighlighter(QSyntaxHighlighter):
    """Базовая подсветка синтаксиса Markdown."""

    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)
        self._rules: list[tuple] = []
        self._init_rules()

    def _init_rules(self) -> None:
        # Форматы
        heading = QTextCharFormat()
        heading.setForeground(QColor("#1a73e8"))
        heading.setFontWeight(QFont.Bold)

        bold = QTextCharFormat()
        bold.setFontWeight(QFont.Bold)
        bold.setForeground(QColor("#333"))

        italic = QTextCharFormat()
        italic.setFontItalic(True)
        italic.setForeground(QColor("#555"))

        code_inline = QTextCharFormat()
        code_inline.setForeground(QColor("#c7254e"))
        code_inline.setBackground(QColor("#f9f2f4"))

        code_block = QTextCharFormat()
        code_block.setForeground(QColor("#2e7d32"))
        code_block.setBackground(QColor("#f5f5f5"))

        strikethrough = QTextCharFormat()
        strikethrough.setFontStrikeOut(True)
        strikethrough.setForeground(QColor("#999"))

        link = QTextCharFormat()
        link.setForeground(QColor("#1565c0"))
        link.setFontUnderline(True)

        hr = QTextCharFormat()
        hr.setForeground(QColor("#bbb"))

        blockquote = QTextCharFormat()
        blockquote.setForeground(QColor("#795548"))

        import re
        self._rules = [
            (re.compile(r'^(#{1,6}\s.*)$', re.MULTILINE), heading),
            (re.compile(r'\*\*(.+?)\*\*'), bold),
            (re.compile(r'__(.+?)__'), bold),
            (re.compile(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)'), italic),
            (re.compile(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)'), italic),
            (re.compile(r'~~(.+?)~~'), strikethrough),
            (re.compile(r'`([^`]+)`'), code_inline),
            (re.compile(r'^```[\s\S]*?^```', re.MULTILINE), code_block),
            (re.compile(r'\[(.+?)\]\((.+?)\)'), link),
            (re.compile(r'^---+$', re.MULTILINE), hr),
            (re.compile(r'^\*\*\*+$', re.MULTILINE), hr),
            (re.compile(r'^>\s?.*$', re.MULTILINE), blockquote),
        ]

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, fmt)


# ── Панель нумерации строк ───────────────────────────────────

class LineNumberArea(QWidget):
    """Виджет боковой панели с номерами строк."""

    def __init__(self, editor: "EditorWidget") -> None:
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:
        self._editor.line_number_area_paint_event(event)


# ── Редактор ─────────────────────────────────────────────────

class EditorWidget(QPlainTextEdit):
    """Редактор Markdown с нумерацией строк, подсветкой, настраиваемой табуляцией."""

    content_changed = Signal()
    save_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._current_path: str = ""
        self._show_line_numbers: bool = Config.get("show_line_numbers", True)
        self._tab_size: int = Config.get("tab_size", 4)

        # Панель номеров строк
        self._line_number_area = LineNumberArea(self)

        # Подсветка синтаксиса
        self._highlighter = MarkdownHighlighter(self.document())

        self._setup_ui()
        self._update_line_number_area_width()

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

    def apply_settings(self) -> None:
        """Применить настройки из Config."""
        self._tab_size = Config.get("tab_size", 4)
        self._show_line_numbers = Config.get("show_line_numbers", True)
        self.setTabStopDistance(self._tab_size * self.fontMetrics().averageCharWidth())
        self._update_line_number_area_width()
        self._line_number_area.update()

    # ── UI ────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        # Шрифт
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        # Табуляция
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.setTabStopDistance(self._tab_size * self.fontMetrics().averageCharWidth())

        # Стиль управляется через тему в MainWindow

        # Сигналы
        self.textChanged.connect(self._on_text_changed)
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)

        # Горячие клавиши
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_requested.emit)

    # ── нумерация строк ──────────────────────────────────────

    def line_number_area_width(self) -> int:
        if not self._show_line_numbers:
            return 0
        digits = max(1, len(str(self.blockCount())))
        space = 8 + self.fontMetrics().horizontalAdvance('9') * digits + 4
        return space

    def _update_line_number_area_width(self) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(
                0, rect.y(), self._line_number_area.width(), rect.height()
            )
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width()

    def line_number_area_paint_event(self, event) -> None:
        if not self._show_line_numbers:
            return

        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor("#f0f0f0"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#999"))
                painter.setFont(self.font())
                painter.drawText(
                    0, int(top), self._line_number_area.width() - 4,
                    self.fontMetrics().height(),
                    Qt.AlignRight | Qt.AlignVCenter,
                    number,
                )
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    # ── resize ────────────────────────────────────────────────

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    # ── Tab → пробелы ────────────────────────────────────────

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Tab:
            # Заменяем Tab на пробелы
            cursor = self.textCursor()
            cursor.insertText(" " * self._tab_size)
        elif event.key() == Qt.Key_Return:
            # Автоотступ: сохраняем отступ предыдущей строки
            cursor = self.textCursor()
            line = cursor.block().text()
            indent = ""
            for ch in line:
                if ch in (" ", "\t"):
                    indent += ch
                else:
                    break
            # Для списков — добавляем маркер
            stripped = line.lstrip()
            if stripped.startswith("- ") or stripped.startswith("* "):
                indent += "  "
            elif len(stripped) > 2 and stripped[0].isdigit() and stripped[1] == '.':
                indent += "   "
            super().keyPressEvent(event)
            cursor.insertText(indent)
        else:
            super().keyPressEvent(event)

    # ── слоты ─────────────────────────────────────────────────

    def _on_text_changed(self) -> None:
        self.content_changed.emit()