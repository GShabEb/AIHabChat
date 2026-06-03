"""Главное окно приложения AiHabChat."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QLabel,
    QLineEdit,
    QMessageBox,
    QInputDialog,
    QStatusBar,
    QPushButton,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

from core.config.config_manager import Config
from core.vault.mermaid_util import default_mermaid_template, is_mermaid_note
from gui.themes.styles import THEME_DARK, THEME_LIGHT
from gui.widgets.chat_widget import ChatButton, ChatWidget
from gui.widgets.note_widget import NoteWidget
from gui.widgets.preview_widget import PreviewWidget
from gui.widgets.tree_widget import TreeWidget
from gui.windows.settings_window import SettingsWindow
from gui.windows.vault_dialog import VaultDialog


def _title_from_path(rel_path: str) -> str:
    filename = rel_path.split("/")[-1]
    lower = filename.lower()
    if lower.endswith(".mermaid.md"):
        return filename[:-11]
    if lower.endswith(".mermaid"):
        return filename[:-8]
    if lower.endswith(".mmd"):
        return filename[:-4]
    if lower.endswith(".md"):
        return filename[:-3]
    if "." in filename:
        return filename.rsplit(".", 1)[0]
    return filename


def _extension_for_path(rel_path: str) -> str:
    if rel_path.lower().endswith(".mermaid.md"):
        return ".mermaid.md"
    if rel_path.lower().endswith(".mermaid"):
        return ".mermaid"
    if rel_path.lower().endswith(".mmd"):
        return ".mmd"
    return ".md"


class MainWindow(QMainWindow):
    """Главное окно: сайдбар + редактор/превью + чат."""

    def __init__(self, app) -> None:
        super().__init__()
        self._app = app
        self._current_path: str = ""
        self._view_mode: str = "editor"
        self._theme: str = Config.get("theme", "light")

        self._setup_ui()
        self._setup_menu()
        self._setup_autosave()
        self._apply_theme()

        if self._app.vault.is_open:
            self.on_vault_opened()

    def on_vault_opened(self) -> None:
        if self._app.file_manager:
            self.file_tree.file_manager = self._app.file_manager
            self._app.chat_manager.set_file_manager(self._app.file_manager)
        self.setWindowTitle(f"{Config.APP_NAME} - {self._app.vault.path}")
        self.statusBar().showMessage(f"Хранилище: {self._app.vault.path}")

    def _toggle_chat_panel(self) -> None:
        visible = not self._chat_panel.isVisible()
        self._chat_panel.setVisible(visible)
        w = max(self._outer_splitter.width(), 800)
        if visible:
            self._outer_splitter.setSizes([w - 360, 360])
        else:
            self._outer_splitter.setSizes([w, 0])

    def _on_chat_file_created(self, rel_path: str) -> None:
        self.file_tree.refresh()
        self.file_tree.select_file(rel_path)
        self._on_file_selected(rel_path)
        self.statusBar().showMessage(f"Создано из чата: {rel_path}", 3000)

    def _setup_ui(self) -> None:
        self.setMinimumSize(Config.MIN_WIDTH, Config.MIN_HEIGHT)
        self.resize(Config.DEFAULT_WIDTH, Config.DEFAULT_HEIGHT)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._main_splitter = QSplitter(Qt.Horizontal)

        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        sidebar_header = QLabel("Хранилище")
        sidebar_header.setObjectName("sidebarHeader")
        sidebar_layout.addWidget(sidebar_header)

        self.file_tree = TreeWidget()
        self.file_tree.file_selected.connect(self._on_file_selected)
        self.file_tree.create_note_requested.connect(self._on_create_note)
        self.file_tree.create_folder_requested.connect(self._on_create_folder)
        self.file_tree.delete_requested.connect(self._on_delete)
        self.file_tree.file_moved.connect(self._on_file_moved)
        sidebar_layout.addWidget(self.file_tree)

        sidebar.setMinimumWidth(Config.SIDEBAR_MIN_WIDTH)
        sidebar.setMaximumWidth(Config.SIDEBAR_MAX_WIDTH)
        sidebar.setObjectName("sidebar")

        work_area = QWidget()
        work_area.setObjectName("workArea")
        work_layout = QVBoxLayout(work_area)
        work_layout.setContentsMargins(0, 0, 0, 0)
        work_layout.setSpacing(0)

        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(26)
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(6, 0, 6, 0)
        top_bar_layout.setSpacing(4)

        self._btn_editor = self._make_view_btn("Ред.")
        self._btn_preview = self._make_view_btn("Просм.")
        self._btn_split = self._make_view_btn("Сплит")
        self._btn_editor.clicked.connect(lambda: self._set_view_mode("editor"))
        self._btn_preview.clicked.connect(lambda: self._set_view_mode("preview"))
        self._btn_split.clicked.connect(lambda: self._set_view_mode("split"))

        for btn in (self._btn_editor, self._btn_preview, self._btn_split):
            top_bar_layout.addWidget(btn)

        top_bar_layout.addStretch()

        self.chat_button = ChatButton()
        top_bar_layout.addWidget(self.chat_button)

        work_layout.addWidget(top_bar)

        self._note_title = QLineEdit()
        self._note_title.setObjectName("noteTitle")
        self._note_title.setPlaceholderText("Без названия")
        self._note_title.setFixedHeight(32)
        self._note_title.editingFinished.connect(self._on_title_changed)
        work_layout.addWidget(self._note_title)

        self._work_splitter = QSplitter(Qt.Horizontal)

        self.editor = NoteWidget()
        self.editor.content_changed.connect(self._on_content_changed)
        self.editor.save_requested.connect(self._save_current)

        self.preview = PreviewWidget()

        self._work_splitter.addWidget(self.editor)
        self._work_splitter.addWidget(self.preview)

        work_layout.addWidget(self._work_splitter, stretch=1)

        self._set_view_mode("editor")

        self._outer_splitter = QSplitter(Qt.Horizontal)
        self._outer_splitter.addWidget(work_area)

        self._chat_panel = ChatWidget(self._app)
        self._chat_panel.hide()
        self._chat_panel.file_created.connect(self._on_chat_file_created)
        self._chat_panel.open_settings_requested.connect(self._on_settings)
        self._outer_splitter.addWidget(self._chat_panel)
        self._outer_splitter.setStretchFactor(0, 1)
        self._outer_splitter.setStretchFactor(1, 0)

        self.chat_button.classic_chat_requested.connect(self._toggle_chat_panel)

        self._main_splitter.addWidget(sidebar)
        self._main_splitter.addWidget(self._outer_splitter)
        self._main_splitter.setStretchFactor(0, 0)
        self._main_splitter.setStretchFactor(1, 1)
        self._main_splitter.setSizes(
            [Config.SIDEBAR_DEFAULT_WIDTH, Config.DEFAULT_WIDTH - Config.SIDEBAR_DEFAULT_WIDTH]
        )

        main_layout.addWidget(self._main_splitter)
        self.setStatusBar(QStatusBar())

    def _make_view_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFlat(True)
        btn.setFixedHeight(22)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    def _setup_menu(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")

        open_vault = QAction("Открыть хранилище...", self)
        open_vault.setShortcut("Ctrl+O")
        open_vault.triggered.connect(self._on_open_vault)
        file_menu.addAction(open_vault)

        new_note = QAction("Новая заметка", self)
        new_note.setShortcut("Ctrl+N")
        new_note.triggered.connect(lambda: self._on_create_note(""))
        file_menu.addAction(new_note)

        new_mermaid = QAction("Новая схема (Mermaid)", self)
        new_mermaid.triggered.connect(lambda: self._on_create_note("|mermaid"))
        file_menu.addAction(new_mermaid)

        new_folder = QAction("Новая папка", self)
        new_folder.triggered.connect(lambda: self._on_create_folder(""))
        file_menu.addAction(new_folder)

        file_menu.addSeparator()

        save = QAction("Сохранить", self)
        save.setShortcut("Ctrl+S")
        save.triggered.connect(self._save_current)
        file_menu.addAction(save)

        file_menu.addSeparator()

        quit_app = QAction("Выход", self)
        quit_app.setShortcut("Ctrl+Q")
        quit_app.triggered.connect(self.close)
        file_menu.addAction(quit_app)

        view_menu = menubar.addMenu("Вид")

        mode_editor = QAction("Редактор", self)
        mode_editor.triggered.connect(lambda: self._set_view_mode("editor"))
        view_menu.addAction(mode_editor)

        mode_preview = QAction("Предпросмотр", self)
        mode_preview.triggered.connect(lambda: self._set_view_mode("preview"))
        view_menu.addAction(mode_preview)

        mode_split = QAction("Разделенный", self)
        mode_split.triggered.connect(lambda: self._set_view_mode("split"))
        view_menu.addAction(mode_split)

        settings_menu = menubar.addMenu("Настройки")

        settings_action = QAction("Настройки...", self)
        settings_action.triggered.connect(self._on_settings)
        settings_menu.addAction(settings_action)

    def _setup_autosave(self) -> None:
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(Config.AUTOSAVE_INTERVAL)
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_timer.start()

    def _set_view_mode(self, mode: str) -> None:
        self._view_mode = mode
        dark = self._theme == "dark"
        style_active = (
            "QPushButton { background-color: #4a9eff; color: white; "
            "border: none; padding: 0 6px; border-radius: 3px; "
            "font-size: 11px; font-weight: bold; min-width: 0; max-height: 22px; }"
        )
        inactive_fg = "#aaaaaa" if dark else "#888888"
        inactive_hover = "#1a1a1a" if dark else "#eeeeee"
        style_inactive = (
            f"QPushButton {{ background-color: transparent; color: {inactive_fg}; "
            "border: none; padding: 0 6px; border-radius: 3px; "
            "font-size: 11px; min-width: 0; max-height: 22px; }"
            f"QPushButton:hover {{ background-color: {inactive_hover}; }}"
        )

        for btn, m in [
            (self._btn_editor, "editor"),
            (self._btn_preview, "preview"),
            (self._btn_split, "split"),
        ]:
            btn.setStyleSheet(style_active if m == mode else style_inactive)

        if mode == "editor":
            self.editor.show()
            self.preview.hide()
        elif mode == "preview":
            self.editor.hide()
            self.preview.show()
            self._update_preview()
        elif mode == "split":
            self.editor.show()
            self.preview.show()
            self._update_preview()
            w = self._work_splitter.width()
            self._work_splitter.setSizes([w // 2, w // 2])

    def _on_file_selected(self, rel_path: str) -> None:
        if not self._app.file_manager:
            return
        self._save_current()
        try:
            content = self._app.file_manager.read_file(rel_path)
        except FileNotFoundError:
            QMessageBox.warning(self, "Ошибка", f"Файл не найден:\n{rel_path}")
            return
        self._current_path = rel_path
        self.editor.load_content(rel_path, content)
        self._note_title.setText(_title_from_path(rel_path))
        if is_mermaid_note(rel_path):
            self._set_view_mode("split")
        elif self._view_mode in ("preview", "split"):
            self._update_preview()
        self.statusBar().showMessage(f"Открыт: {rel_path}")

    def _on_content_changed(self) -> None:
        if self._view_mode in ("preview", "split"):
            self._update_preview()

    def _update_preview(self) -> None:
        text = self.editor.toPlainText()
        path = self._current_path
        if self._theme == "dark":
            html = self._app.md_parser.get_preview_html_dark(text, path=path)
        else:
            html = self._app.md_parser.get_preview_html(text, path=path)
        self.preview.set_html(html)

    def _save_current(self) -> None:
        if not self._current_path or not self._app.file_manager:
            return
        content = self.editor.toPlainText()
        try:
            self._app.file_manager.write_file(self._current_path, content)
            self.editor.document().setModified(False)
            self.statusBar().showMessage(f"Сохранено: {self._current_path}", 2000)
        except OSError as e:
            QMessageBox.warning(self, "Ошибка сохранения", str(e))

    def _autosave(self) -> None:
        if self._current_path and self.editor.is_modified and self._app.file_manager:
            self._save_current()

    def _on_title_changed(self) -> None:
        if not self._current_path or not self._app.file_manager:
            return
        new_title = self._note_title.text().strip()
        if not new_title:
            return
        parts = self._current_path.rsplit("/", 1)
        ext = _extension_for_path(self._current_path)
        new_rel = f"{parts[0]}/{new_title}{ext}" if len(parts) == 2 else f"{new_title}{ext}"
        if new_rel == self._current_path:
            return
        try:
            self._app.file_manager.rename(self._current_path, new_rel)
            self._current_path = new_rel
            self.editor.current_path = new_rel
            self.file_tree.refresh()
            self.file_tree.select_file(new_rel)
            self.statusBar().showMessage(f"Переименован: {new_rel}", 2000)
        except OSError as e:
            QMessageBox.warning(self, "Ошибка переименования", str(e))

    def _on_file_moved(self, old_path: str, new_path: str) -> None:
        if self._current_path == old_path:
            self._current_path = new_path
            self.editor.current_path = new_path
            self._note_title.setText(_title_from_path(new_path))
            self.statusBar().showMessage(f"Перемещен: {old_path} -> {new_path}", 2000)

    def _require_vault(self) -> bool:
        if not self._app.file_manager:
            QMessageBox.warning(self, "Нет хранилища", "Сначала откройте хранилище (Ctrl+O)")
            return False
        return True

    def _on_create_note(self, parent_path_and_type: str) -> None:
        if not self._require_vault():
            return
        is_mermaid = False
        parent_path = parent_path_and_type
        if "|" in parent_path_and_type:
            parent_path, type_hint = parent_path_and_type.rsplit("|", 1)
            is_mermaid = type_hint == "mermaid"
        default_name = "Новая схема" if is_mermaid else "Новая заметка"
        name, ok = QInputDialog.getText(
            self, "Новая заметка" if not is_mermaid else "Новая схема",
            "Имя:", text=default_name
        )
        if not ok or not name.strip():
            return
        name = name.strip()
        ext = ".mermaid" if is_mermaid else ".md"
        rel = f"{parent_path}/{name}{ext}" if parent_path else f"{name}{ext}"
        try:
            path = self._app.file_manager.create_note(rel)
            if is_mermaid:
                self._app.file_manager.write_file(rel, default_mermaid_template())
            self.file_tree.refresh()
            rel_path = str(path.relative_to(self._app.vault.path)).replace("\\", "/")
            self._on_file_selected(rel_path)
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать:\n{e}")

    def _on_create_folder(self, parent_path: str) -> None:
        if not self._require_vault():
            return
        name, ok = QInputDialog.getText(self, "Новая папка", "Имя папки:")
        if not ok or not name.strip():
            return
        name = name.strip()
        rel = f"{parent_path}/{name}" if parent_path else name
        try:
            self._app.file_manager.create_folder(rel)
            self.file_tree.refresh()
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать папку:\n{e}")

    def _on_delete(self, rel_path: str) -> None:
        if not self._require_vault():
            return
        reply = QMessageBox.question(
            self, "Удалить?", f"Удалить {rel_path}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        try:
            self._app.file_manager.delete(rel_path)
            if self._current_path == rel_path:
                self.editor.clear_editor()
                self._current_path = ""
                self._note_title.setText("")
            self.file_tree.refresh()
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось удалить:\n{e}")

    def _on_open_vault(self) -> None:
        dialog = VaultDialog(self)
        if dialog.exec():
            self._app.open_vault(dialog.selected_path)

    def _on_settings(self) -> None:
        dialog = SettingsWindow(self)
        if dialog.exec():
            self._apply_theme()
            self.editor.apply_settings()
            if self._view_mode in ("preview", "split"):
                self._update_preview()
            self.statusBar().showMessage("Настройки применены", 2000)

    def _apply_theme(self) -> None:
        self._theme = Config.get("theme", "light")
        if self._theme == "dark":
            self.setStyleSheet(THEME_DARK)
        else:
            self.setStyleSheet(THEME_LIGHT)
        self.editor.set_theme(self._theme == "dark")
        self._set_view_mode(self._view_mode)

    def closeEvent(self, event) -> None:
        self._save_current()
        super().closeEvent(event)
