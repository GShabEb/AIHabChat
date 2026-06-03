"""Дерево файлов хранилища — навигация по заметкам с drag-and-drop."""

from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QMenu,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDrag

from core.vault.file_manager import FileManager


class TreeWidget(QTreeWidget):
    """Дерево файлов vault с контекстным меню и drag-and-drop."""

    file_selected = Signal(str)
    create_note_requested = Signal(str)
    create_folder_requested = Signal(str)
    delete_requested = Signal(str)
    file_moved = Signal(str, str)

    MIME_TYPE = "application/x-aihabchat-file"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._file_manager: FileManager | None = None
        self._drag_item: QTreeWidgetItem | None = None
        self._setup_ui()

    @property
    def file_manager(self) -> FileManager | None:
        return self._file_manager

    @file_manager.setter
    def file_manager(self, fm: FileManager) -> None:
        self._file_manager = fm
        self.refresh()

    def refresh(self) -> None:
        self.clear()
        if not self._file_manager:
            return
        tree_data = self._file_manager.walk_tree()
        self._populate(tree_data, self.invisibleRootItem())
        self.expandAll()

    def select_file(self, relative_path: str) -> None:
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

    def is_folder_item(self, item: QTreeWidgetItem) -> bool:
        return item.text(0).startswith("\U0001f4c1")

    def _setup_ui(self) -> None:
        self.setHeaderLabel("Файлы")
        self.setAnimated(True)
        self.setExpandsOnDoubleClick(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setIndentation(16)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        header = self.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.itemClicked.connect(self._on_item_clicked)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def _populate(self, data: list[dict], parent: QTreeWidgetItem) -> None:
        for entry in data:
            if entry["type"] == "folder":
                folder_path = entry.get("path", "")
                item = QTreeWidgetItem(parent, [f"\U0001f4c1 {entry['name']}"])
                item.setData(0, Qt.UserRole, folder_path)
                item.setExpanded(True)
                item.setFlags(item.flags() | Qt.ItemIsDropEnabled)
                self._populate(entry["children"], item)
            else:
                name = entry["name"]
                icon = "\U0001f4dd" if name.endswith(".md") else "\U0001f4ca"
                item = QTreeWidgetItem(parent, [f"{icon} {name}"])
                item.setData(0, Qt.UserRole, entry["path"])
                item.setFlags(item.flags() & ~Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled)

    def startDrag(self, supportedActions) -> None:
        item = self.currentItem()
        if not item:
            return
        rel_path = item.data(0, Qt.UserRole)
        if not rel_path:
            return
        self._drag_item = item
        from PySide6.QtCore import QMimeData
        mime_data = QMimeData()
        mime_data.setData(self.MIME_TYPE, rel_path.encode("utf-8"))
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(Qt.MoveAction)

    def dropEvent(self, event) -> None:
        if not self._file_manager:
            super().dropEvent(event)
            return
        mime_data = event.mimeData()
        if not mime_data.hasFormat(self.MIME_TYPE):
            super().dropEvent(event)
            return
        src_path = bytes(mime_data.data(self.MIME_TYPE)).decode("utf-8")
        if not src_path:
            super().dropEvent(event)
            return
        target_item = self.itemAt(event.pos())
        if target_item and self.is_folder_item(target_item):
            target_folder = target_item.data(0, Qt.UserRole) or ""
        else:
            target_folder = ""
        if src_path == target_folder or (target_folder and target_folder.startswith(src_path + "/")):
            event.ignore()
            return
        filename = src_path.split("/")[-1]
        new_path = f"{target_folder}/{filename}" if target_folder else filename
        if new_path == src_path:
            event.ignore()
            return
        try:
            self._file_manager.rename(src_path, new_path)
            self.file_moved.emit(src_path, new_path)
            self.refresh()
            event.accept()
        except OSError:
            event.ignore()

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasFormat(self.MIME_TYPE):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasFormat(self.MIME_TYPE):
            event.acceptProposedAction()
            item = self.itemAt(event.pos())
            if item and self.is_folder_item(item):
                self.setCurrentItem(item)
        else:
            super().dragMoveEvent(event)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        rel_path = item.data(0, Qt.UserRole)
        if rel_path and not self.is_folder_item(item):
            self.file_selected.emit(rel_path)
        elif self.is_folder_item(item):
            if item.isExpanded():
                self.collapseItem(item)
            else:
                self.expandItem(item)

    def _on_context_menu(self, pos) -> None:
        item = self.itemAt(pos)
        menu = QMenu(self)
        parent_path = ""
        if item and self.is_folder_item(item):
            parent_path = item.data(0, Qt.UserRole) or ""
        new_note = menu.addAction("Новая заметка (.md)")
        new_mermaid = menu.addAction("Новая схема (.mermaid)")
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
        elif action == new_mermaid:
            self.create_note_requested.emit(parent_path + "|mermaid")
        elif action == new_folder:
            self.create_folder_requested.emit(parent_path)
        elif action == delete_action and item:
            rel = item.data(0, Qt.UserRole)
            if rel:
                self.delete_requested.emit(rel)


FileTreeWidget = TreeWidget
