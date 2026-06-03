"""Кнопка чата с выпадающим меню режимов."""

from PySide6.QtWidgets import QPushButton, QMenu
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QAction


class ChatButton(QPushButton):
    """
    Кнопка чата с двумя режимами:
    - Классический чат (боковая панель)
    - Полноценный чат (отдельное окно)

    Клик — классический чат; в меню — полноценный (позже).
    """

    classic_chat_requested = Signal()
    full_chat_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()

    # ── UI ────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setText("💬 Чат")
        self.setFixedSize(72, 22)
        self.setStyleSheet(
            "QPushButton {"
            "  background-color: #4a9eff;"
            "  color: white;"
            "  border: none;"
            "  border-radius: 6px;"
            "  font-weight: bold;"
            "  font-size: 11px;"
            "  padding: 0 8px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #3a8eef;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #2a7edf;"
            "}"
        )

        # Меню режимов
        self._menu = QMenu(self)

        classic_action = QAction("💬 Классический чат", self)
        classic_action.triggered.connect(self._on_classic)
        self._menu.addAction(classic_action)

        full_action = QAction("🖥 Полноценный чат", self)
        full_action.triggered.connect(self._on_full)
        self._menu.addAction(full_action)

        self.setMenu(self._menu)

        # Прямой клик — классический режим
        self.clicked.connect(self._on_classic)

    # ── слоты ─────────────────────────────────────────────────

    def _on_classic(self) -> None:
        self.classic_chat_requested.emit()

    def _on_full(self) -> None:
        self.full_chat_requested.emit()
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "В разработке",
            "Полноценный чат (отдельное окно) появится в следующей версии.",
        )