"""Главное окно приложения AiHabChat."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QToolBar,
    QLabel,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QStatusBar,
    QPushButton,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

from app.config import Config
from app.widgets.file_tree import FileTreeWidget
from app.widgets.editor import EditorWidget
from app.widgets.preview import PreviewWidget
from app.widgets.chat_button import ChatButton
from app.dialogs.vault_dialog import VaultDialog
from app.dialogs.settings_dialog import SettingsDialog


# ── Таблицы стилей ────────────────────────────────────────────

THEME_LIGHT = """
QMainWindow { background: #ffffff; }
#sidebar { background: #f5f5f5; border-right: 1px solid #ddd; }
#sidebarHeader { padding: 8px; font-weight: bold; font-size: 13px;
                 background-color: #e8e8e8; border-bottom: 1px solid #ccc; }
#topBar { background-color: #f0f0f0; border-bottom: 1px solid #ccc; }
#noteTitle { color: #222; }
QMenuBar { background: #f5f5f5; }
QToolBar { background: #f8f8f8; border-bottom: 1px solid #ddd; spacing: 4px; padding: 2px; }
QStatusBar { background: #f0f0f0; color: #555; }
QTreeWidget { background: #fafafa; border: none; }
QTreeWidget::item:selected { background: #4a9eff; color: white; }
QPlainTextEdit { background-color: #fafafa; border: none; padding: 8px; padding-left: 4px; }
QTextBrowser { background-color: #ffffff; border: none; padding: 8px; }
QLabel { color: #222; }
"""

THEME_DARK = """
QMainWindow { background: #1e1e1e; color: #ddd; }
#sidebar { background: #252526; border-right: 1px solid #444; }
#sidebarHeader { padding: 8px; font-weight: bold; font-size: 13px;
                 background-color: #333; border-bottom: 1px solid #444; color: #ddd; }
#topBar { background-color: #2d2d2d; border-bottom: 1px solid #444; }
#noteTitle { color: #ddd; }
QMenuBar { background: #2d2d2d; color: #ddd; }
QMenuBar::item:selected { background: #3a3a3a; }
QMenu { background: #2d2d2d; color: #ddd; }
QMenu::item:selected { background: #4a9eff; }
QToolBar { background: #2d2d2d; border-bottom: 1px solid #444; spacing: 4px; padding: 2px; color: #ddd; }
QStatusBar { background: #2d2d2d; color: #aaa; }
QTreeWidget { background: #252526; border: none; color: #ddd; }
QTreeWidget::item:selected { background: #4a9eff; color: white; }
QTreeWidget::item:hover { background: #3a3a3a; }
QPlainTextEdit { background-color: #1e1e1e; color: #ddd; border: none;
                 padding: 8px; padding-left: 4px; }
QTextBrowser { background-color: #1e1e1e; color: #ddd; border: none; padding: 8px; }
QLabel { color: #ddd; }
QLineEdit { color: #ddd; }
QSplitter::handle { background: #444; }
QScrollBar:vertical { background: #2d2d2d; width: 10px; }
QScrollBar::handle:vertical { background: #555; border-radius: 4px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


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
        self._setup_toolbar()
        self._setup_autosave()
        self._apply_theme()

        if self._app.vault.is_open:
            self.on_vault_opened()

    # ── публичные методы ─────────────────────────────────────

    def on_vault_opened(self) -> None:
        """Вызывается после открытия хранилища."""
        if self._app.file_manager:
            self.file_tree.file_manager = self._app.file_manager
        self.setWindowTitle(f"{Config.APP_NAME} — {self._app.vault.path}")
        self.statusBar().showMessage(f"Хранилище: {self._app.vault.path}")

    # ── UI ────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setMinimumSize(Config.MIN_WIDTH, Config.MIN_HEIGHT)
        self.resize(Config.DEFAULT_WIDTH, Config.DEFAULT_HEIGHT)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Главный сплиттер
        self._main_splitter = QSplitter(Qt.Horizontal)

        # ── Сайдбар ──
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        sidebar_header = QLabel("Хранилище")
        sidebar_header.setObjectName("sidebarHeader")
        sidebar_layout.addWidget(sidebar_header)

        self.file_tree = FileTreeWidget()
        self.file_tree.file_selected.connect(self._on_file_selected)
        self.file_tree.create_note_requested.connect(self._on_create_note)
        self.file_tree.create_folder_requested.connect(self._on_create_folder)
        self.file_tree.delete_requested.connect(self._on_delete)
        sidebar_layout.addWidget(self.file_tree)

        sidebar.setMinimumWidth(Config.SIDEBAR_MIN_WIDTH)
        sidebar.setMaximumWidth(Config.SIDEBAR_MAX_WIDTH)
        sidebar.setObjectName("sidebar")

        # ── Рабочая область ──
        work_area = QWidget()
        work_layout = QVBoxLayout(work_area)
        work_layout.setContentsMargins(0, 0, 0, 0)
        work_layout.setSpacing(0)

        # Верхняя панель: название + кнопки вида + чат
        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(8, 4, 8, 4)

        self._note_title = QLineEdit()
        self._note_title.setPlaceholderText("Название заметки...")
        self._note_title.setObjectName("noteTitle")
        self._note_title.setStyleSheet(
            "QLineEdit { border: none; font-size: 15px; font-weight: bold; "
            "padding: 4px 8px; background: transparent; }"
        )
        self._note_title.editingFinished.connect(self._on_title_changed)
        top_bar_layout.addWidget(self._note_title, 1)

        self._btn_editor = self._make_view_btn("Редактор")
        self._btn_preview = self._make_view_btn("Предпросмотр")
        self._btn_split = self._make_view_btn("Разделенный")
        self._btn_editor.clicked.connect(lambda: self._set_view_mode("editor"))
        self._btn_preview.clicked.connect(lambda: self._set_view_mode("preview"))
        self._btn_split.clicked.connect(lambda: self._set_view_mode("split"))

        for btn in (self._btn_editor, self._btn_preview, self._btn_split):
            top_bar_layout.addWidget(btn)

        self.chat_button = ChatButton()
        top_bar_layout.addWidget(self.chat_button)

        work_layout.addWidget(top_bar)

        # Рабочий сплиттер (редактор | превью)
        self._work_splitter = QSplitter(Qt.Horizontal)

        self.editor = EditorWidget()
        self.editor.content_changed.connect(self._on_content_changed)
        self.editor.save_requested.connect(self._save_current)

        self.preview = PreviewWidget()

        self._work_splitter.addWidget(self.editor)
        self._work_splitter.addWidget(self.preview)

        work_layout.addWidget(self._work_splitter)

        # Начальный режим
        self._set_view_mode("editor")

        # Добавляем в главный сплиттер
        self._main_splitter.addWidget(sidebar)
        self._main_splitter.addWidget(work_area)
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
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    # ── Меню ─────────────────────────────────────────────────

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

    # ── Тулбар ────────────────────────────────────────────────

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Главная")
        toolbar.setMovable(False)
        toolbar.setObjectName("mainToolbar")
        self.addToolBar(toolbar)

        open_action = QAction("Открыть", self)
        open_action.triggered.connect(self._on_open_vault)
        toolbar.addAction(open_action)

        new_action = QAction("Новая", self)
        new_action.triggered.connect(lambda: self._on_create_note(""))
        toolbar.addAction(new_action)

        folder_action = QAction("Папка", self)
        folder_action.triggered.connect(lambda: self._on_create_folder(""))
        toolbar.addAction(folder_action)

        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self._save_current)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(self._on_settings)
        toolbar.addAction(settings_action)

    def _setup_autosave(self) -> None:
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(Config.AUTOSAVE_INTERVAL)
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_timer.start()

    # ── Режимы отображения ───────────────────────────────────

    def _set_view_mode(self, mode: str) -> None:
        self._view_mode = mode
        style_active = (
            "QPushButton { background-color: #4a9eff; color: white; "
            "border: none; padding: 4px 10px; border-radius: 3px; font-weight: bold; }"
        )
        style_inactive = (
            "QPushButton { background-color: transparent; color: #555; "
            "border: none; padding: 4px 10px; border-radius: 3px; }"
            "QPushButton:hover { background-color: #e0e0e0; }"
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

    # ── Работа с файлами ─────────────────────────────────────

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

        # Название заметки из имени файла
        filename = rel_path.split("/")[-1]
        title = filename.rsplit(".", 1)[0] if "." in filename else filename
        self._note_title.setText(title)

        if self._view_mode in ("preview", "split"):
            self._update_preview()

        self.statusBar().showMessage(f"Открыт: {rel_path}")

    def _on_content_changed(self) -> None:
        if self._view_mode in ("preview", "split"):
            self._update_preview()

    def _update_preview(self) -> None:
        text = self.editor.toPlainText()
        if self._theme == "dark":
            html = self._app.md_parser.get_preview_html_dark(text)
        else:
            html = self._app.md_parser.get_preview_html(text)
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

    # ── Название заметки ─────────────────────────────────────

    def _on_title_changed(self) -> None:
        if not self._current_path or not self._app.file_manager:
            return

        new_title = self._note_title.text().strip()
        if not new_title:
            return

        parts = self._current_path.rsplit("/", 1)
        new_rel = f"{parts[0]}/{new_title}.md" if len(parts) == 2 else f"{new_title}.md"

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

    # ── Создание / удаление ──────────────────────────────────

    def _require_vault(self) -> bool:
        """Проверить, что хранилище открыто."""
        if not self._app.file_manager:
            QMessageBox.warning(self, "Нет хранилища",
                                "Сначала откройте хранилище (Ctrl+O)")
            return False
        return True

    def _on_create_note(self, parent_path: str) -> None:
        if not self._require_vault():
            return

        name, ok = QInputDialog.getText(
            self, "Новая заметка", "Имя заметки:", text="Новая заметка"
        )
        if not ok or not name.strip():
            return

        name = name.strip()
        rel = f"{parent_path}/{name}" if parent_path else name
        try:
            path = self._app.file_manager.create_note(rel)
            self.file_tree.refresh()
            rel_path = str(path.relative_to(self._app.vault.path)).replace("\\", "/")
            self._on_file_selected(rel_path)
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать заметку:\n{e}")

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

    # ── Хранилище ────────────────────────────────────────────

    def _on_open_vault(self) -> None:
        dialog = VaultDialog(self)
        if dialog.exec():
            self._app.open_vault(dialog.selected_path)

    # ── Настройки ────────────────────────────────────────────

    def _on_settings(self) -> None:
        dialog = SettingsDialog(self)
        if dialog.exec():
            self._apply_theme()
            self.editor.apply_settings()
            if self._view_mode in ("preview", "split"):
                self._update_preview()
            self.statusBar().showMessage("Настройки применены", 2000)

    def _apply_theme(self) -> None:
        """Применить текущую тему."""
        self._theme = Config.get("theme", "light")
        if self._theme == "dark":
            self.setStyleSheet(THEME_DARK)
        else:
            self.setStyleSheet(THEME_LIGHT)

    # ── Закрытие ─────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        self._save_current()
        super().closeEvent(event)
