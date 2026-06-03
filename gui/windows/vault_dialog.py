"""Диалог выбора/создания хранилища (vault)."""

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt


class VaultDialog(QDialog):
    """Диалог для выбора root-папки хранилища заметок."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._selected_path: str = ""
        self._setup_ui()

    @property
    def selected_path(self) -> str:
        return self._selected_path

    # ── UI ────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setWindowTitle("Открыть хранилище")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel("Выберите папку хранилища заметок")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title)

        # Описание
        desc = QLabel(
            "Хранилище — это папка, в которой будут храниться "
            "ваши Markdown-заметки (по аналогии с Obsidian Vault)."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; margin-bottom: 16px;")
        layout.addWidget(desc)

        # Поле пути + кнопка "Обзор"
        path_layout = QHBoxLayout()
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("Путь к папке хранилища...")
        path_layout.addWidget(self._path_edit)

        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self._on_browse)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        # Кнопки ОК / Отмена
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("Открыть")
        ok_btn.setDefault(True)
        ok_btn.setStyleSheet(
            "QPushButton { background-color: #4a9eff; color: white; "
            "padding: 6px 20px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #3a8eef; }"
        )
        ok_btn.clicked.connect(self._on_accept)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    # ── слоты ─────────────────────────────────────────────────

    def _on_browse(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку хранилища",
            "",
            QFileDialog.ShowDirsOnly,
        )
        if path:
            self._path_edit.setText(path)

    def _on_accept(self) -> None:
        path = self._path_edit.text().strip()
        if not path:
            QMessageBox.warning(self, "Ошибка", "Укажите путь к папке хранилища.")
            return

        if not Path(path).exists():
            reply = QMessageBox.question(
                self,
                "Создать папку?",
                f"Папка не существует:\n{path}\n\nСоздать?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                try:
                    Path(path).mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось создать папку:\n{e}")
                    return
            else:
                return

        self._selected_path = path
        self.accept()