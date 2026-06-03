"""Дерево файлов хранилища — навигация по заметкам."""

from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QMenu,
)
from PySide6.QtCore import Signal, Qt

from core.file_manager import FileManager


class FileTreeWidget(QTreeWidget):
    """Дерево файлов vault с контекстным меню."""

    # Сигналы
    file_selected = Signal(str)       # относительный путь к файлу
    create_note_requested = Signal(str)  # папка, в которой создать заметку
    create_folder_requested = Signal(str)
    delete_requested = Signal(str)     # относительный путь

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._file_manager: FileManager | None = None
        self._setup_ui()

    # ── свойства ──────────────────────────────────────────────

    @property
    def file_manager(self) -> FileManager | None:
        return self._file_manager

    @file_manager.setter
    def file_manager(self, fm: FileManager) -> None:
        self._file_manager = fm
        self.refresh()

    # ── публичные методы ─────────────────────────────────────

    def refresh(self) -> None:
        """Обновить дерево файлов."""
        self.clear()
        if not self._file_manager:
            return
        tree_data = self._file_manager.walk_tree()
        self._populate(tree_data, self.invisibleRootItem())
        self.expandAll()

    def select_file(self, relative_path: str) -> None:
        """Выделить файл в дереве по пути."""
        items = self.findItems(
            relative_path.split("/")[-1],
            Qt.MatchExactly | Qt.MatchRecursive,
            0,
        )
        for item in items:
            if item.data(0, Qt.UserRole) == relative_path:
                self.setCurrentItem(item)
                self.scrollToItem(item)
                return

    # ── UI ────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setHeaderLabel("Файлы")
        self.setAnimated(True)
        self.setExpandsOnDoubleClick(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setIndentation(16)

        # Ширина колонки по содержимому
        header = self.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        # Сигналы
        self.itemClicked.connect(self._on_item_clicked)
        self.customContextMenuRequested.connect(self._on_context_menu)

    # ── построение дерева ────────────────────────────────────

    def _populate(self, data: list[dict], parent: QTreeWidgetItem) -> None:
        for entry in data:
            if entry["type"] == "folder":
                item = QTreeWidgetItem(parent, [f"📁 {entry['name']}"])
                item.setData(0, Qt.UserRole, entry.get("path", ""))
                item.setExpanded(True)
                self._populate(entry["children"], item)
            else:
                item = QTreeWidgetItem(parent, [f"📝 {entry['name']}"])
                item.setData(0, Qt.UserRole, entry["path"])

    # ── слоты ─────────────────────────────────────────────────

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        rel_path = item.data(0, Qt.UserRole)
        if rel_path and not item.text(0).startswith("📁"):
            self.file_selected.emit(rel_path)

    def _on_context_menu(self, pos) -> None:
        item = self.itemAt(pos)
        menu = QMenu(self)

        # Определяем, где создаём — в корне или в папке
        parent_path = ""
        if item and item.text(0).startswith("📁"):
            parent_path = item.data(0, Qt.UserRole) or ""

        new_note = menu.addAction("Новая заметка")
        new_folder = menu.addAction("Новая папка")
        menu.addSeparator()

        delete_action = None
        if item:
            delete_action = menu.addAction("Удалить")

        action = menu.exec(self.mapToGlobal(pos))
        if action is None:
            return

        if action == new_note:
            self.create_note_requested.emit(parent_path)
        elif action == new_folder:
            self.create_folder_requested.emit(parent_path)
        elif action == delete_action and item:
            rel = item.data(0, Qt.UserRole)
            if rel:
                self.delete_requested.emit(rel)