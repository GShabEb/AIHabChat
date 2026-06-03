"""Главное окно приложения AiHabChat."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QStackedWidget,
    QToolBar,
    QLabel,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QStatusBar,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction

from app.config import Config
from app.widgets.file_tree import FileTreeWidget
from app.widgets.editor import EditorWidget
from app.widgets.preview import PreviewWidget
from app.widgets.chat_button import ChatButton
from app.dialogs.vault_dialog import VaultDialog


class MainWindow(QMainWindow):
    """Главное окно: сайдбар с деревом + редактор/превью + чат."""

    def __init__(self, app) -> None:
        super().__init__()
        self._app = app  # ссылка на Application
        self._current_path: str = ""
        self._view_mode: str = "editor"  # "editor" | "preview" | "split"
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_autosave()

        # Если хранилище уже было открыто ранее
        if self._app.vault.is_open:
            self.on_vault_opened()
        else:
            self._show_welcome()

    # ── публичные методы ─────────────────────────────────────

    def on_vault_opened(self) -> None:
        """Вызывается после открытия хранилища."""
        if self._app.file_manager:
            self.file_tree.file_manager = self._app.file_manager
        self.setWindowTitle(f"{Config.APP_NAME} — {self._app.vault.path}")
        self._hide_welcome()
        self.statusBar().showMessage(f"Хранилище: {self._app.vault.path}")

    # ── UI ────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setMinimumSize(Config.MIN_WIDTH, Config.MIN_HEIGHT)
        self.resize(Config.DEFAULT_WIDTH, Config.DEFAULT_HEIGHT)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Сплиттер: сайдбар | основная область
        splitter = QSplitter(Qt.Horizontal)

        # ── Сайдбар ──
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок сайдбара
        sidebar_header = QLabel("📂 Хранилище")
        sidebar_header.setStyleSheet(
            "padding: 8px; font-weight: bold; font-size: 13px; "
            "background-color: #e8e8e8; border-bottom: 1px solid #ccc;"
        )
        sidebar_layout.addWidget(sidebar_header)

        # Дерево файлов
        self.file_tree = FileTreeWidget()
        self.file_tree.file_selected.connect(self._on_file_selected)
        self.file_tree.create_note_requested.connect(self._on_create_note)
        self.file_tree.create_folder_requested.connect(self._on_create_folder)
        self.file_tree.delete_requested.connect(self._on_delete)
        sidebar_layout.addWidget(self.file_tree)

        sidebar.setMinimumWidth(Config.SIDEBAR_MIN_WIDTH)
        sidebar.setMaximumWidth(Config.SIDEBAR_MAX_WIDTH)

        # ── Основная область (редактор + превью) ──
        work_area = QWidget()
        work_layout = QVBoxLayout(work_area)
        work_layout.setContentsMargins(0, 0, 0, 0)
        work_layout.setSpacing(0)

        # Панель вкладок редактор/превью/разделённый
        view_bar = QWidget()
        view_bar.setStyleSheet("background-color: #f0f0f0; border-bottom: 1px solid #ccc;")
        view_bar_layout = QHBoxLayout(view_bar)
        view_bar_layout.setContentsMargins(8, 4, 8, 4)

        self._btn_editor = QPushButton_("✏️ Редактор")
        self._btn_preview = QPushButton_("👁 Предпросмотр")
        self._btn_split = QPushButton_("⛶ Разделённый")
        self._btn_editor.clicked.connect(lambda: self._set_view_mode("editor"))
        self._btn_preview.clicked.connect(lambda: self._set_view_mode("preview"))
        self._btn_split.clicked.connect(lambda: self._set_view_mode("split"))

        for btn in (self._btn_editor, self._btn_preview, self._btn_split):
            view_bar_layout.addWidget(btn)
        view_bar_layout.addStretch()

        # Кнопка чата
        self.chat_button = ChatButton()
        view_bar_layout.addWidget(self.chat_button)

        work_layout.addWidget(view_bar)

        # Стек: редактор / превью / сплиттер
        self._stack = QStackedWidget()

        # Страница 0: только редактор
        self.editor = EditorWidget()
        self.editor.content_changed.connect(self._on_content_changed)
        self.editor.save_requested.connect(self._save_current)
        self._stack.addWidget(self.editor)

        # Страница 1: только превью
        self.preview = PreviewWidget()
        self._stack.addWidget(self.preview)

        # Страница 2: разделённый вид
        split_view = QSplitter(Qt.Horizontal)
        self._split_editor = EditorWidget()
        self._split_editor.content_changed.connect(self._on_content_changed)
        self._split_editor.save_requested.connect(self._save_current)
        self._split_preview = PreviewWidget()
        split_view.addWidget(self._split_editor)
        split_view.addWidget(self._split_preview)
        self._stack.addWidget(split_view)

        work_layout.addWidget(self._stack)

        # Добро пожаловать (welcome screen)
        self._welcome = QLabel()
        self._welcome.setAlignment(Qt.AlignCenter)
        self._welcome.setStyleSheet("font-size: 18px; color: #999;")
        self._welcome.setText(
            "👋 Добро пожаловать в AiHabChat!\n\n"
            "Откройте или создайте хранилище (Vault)\n"
            "через меню Файл → Открыть хранилище"
        )
        self._welcome.hide()

        # Добавляем в сплиттер
        splitter.addWidget(sidebar)
        splitter.addWidget(work_area)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([Config.SIDEBAR_DEFAULT_WIDTH, Config.DEFAULT_WIDTH - Config.SIDEBAR_DEFAULT_WIDTH])

        main_layout.addWidget(splitter)

        # Статусбар
        self.setStatusBar(QStatusBar())

        # Начальный режим
        self._set_view_mode("editor")

    def _setup_menu(self) -> None:
        menubar = self.menuBar()

        # Файл
        file_menu = menubar.addMenu("Файл")

        open_vault = QAction("Открыть хранилище...", self)
        open_vault.setShortcut("Ctrl+O")
        open_vault.triggered.connect(self._on_open_vault)
        file_menu.addAction(open_vault)

        new_note = QAction("Новая заметка", self)
        new_note.setShortcut("Ctrl+N")
        new_note.triggered.connect(lambda: self._on_create_note(""))
        file_menu.addAction(new_note)

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

        # Вид
        view_menu = menubar.addMenu("Вид")

        mode_editor = QAction("Редактор", self)
        mode_editor.triggered.connect(lambda: self._set_view_mode("editor"))
        view_menu.addAction(mode_editor)

        mode_preview = QAction("Предпросмотр", self)
        mode_preview.triggered.connect(lambda: self._set_view_mode("preview"))
        view_menu.addAction(mode_preview)

        mode_split = QAction("Разделённый", self)
        mode_split.triggered.connect(lambda: self._set_view_mode("split"))
        view_menu.addAction(mode_split)

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Главная")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("QToolBar { spacing: 4px; padding: 2px; }")
        self.addToolBar(toolbar)

        open_action = QAction("📂 Открыть", self)
        open_action.triggered.connect(self._on_open_vault)
        toolbar.addAction(open_action)

        new_action = QAction("📝 Новая", self)
        new_action.triggered.connect(lambda: self._on_create_note(""))
        toolbar.addAction(new_action)

        save_action = QAction("💾 Сохранить", self)
        save_action.triggered.connect(self._save_current)
        toolbar.addAction(save_action)

    def _setup_autosave(self) -> None:
        """Таймер автосохранения."""
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(Config.AUTOSAVE_INTERVAL)
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_timer.start()

    # ── режимы отображения ───────────────────────────────────

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
            self._stack.setCurrentIndex(0)
        elif mode == "preview":
            self._update_preview()
            self._stack.setCurrentIndex(1)
        elif mode == "split":
            self._update_split_preview()
            self._stack.setCurrentIndex(2)

    # ── работа с файлами ─────────────────────────────────────

    def _on_file_selected(self, rel_path: str) -> None:
        """Файл выбран в дереве — открыть в редакторе."""
        if not self._app.file_manager:
            return

        # Сохранить текущий
        self._save_current()

        try:
            content = self._app.file_manager.read_file(rel_path)
        except FileNotFoundError:
            QMessageBox.warning(self, "Ошибка", f"Файл не найден:\n{rel_path}")
            return

        self._current_path = rel_path
        self.editor.load_content(rel_path, content)

        # Обновить превью, если нужно
        if self._view_mode == "preview":
            self._update_preview()
        elif self._view_mode == "split":
            self._update_split_preview()

        self.statusBar().showMessage(f"Открыт: {rel_path}")

    def _on_content_changed(self) -> None:
        """Контент в редакторе изменён — обновить превью."""
        if self._view_mode == "split":
            self._update_split_preview()
        elif self._view_mode == "preview":
            self._update_preview()

    def _update_preview(self) -> None:
        """Обновить превью основным редактором."""
        html = self._app.md_parser.get_preview_html(self.editor.toPlainText())
        self.preview.set_html(html)

    def _update_split_preview(self) -> None:
        """Обновить превью в разделённом режиме."""
        # Синхронизируем тексты
        self._split_editor.load_content(self.editor.current_path, self.editor.toPlainText())
        html = self._app.md_parser.get_preview_html(self._split_editor.toPlainText())
        self._split_preview.set_html(html)

    def _save_current(self) -> None:
        """Сохранить текущую заметку."""
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
        """Автосохранение при изменениях."""
        if self._current_path and self.editor.is_modified and self._app.file_manager:
            self._save_current()

    # ── создание / удаление ──────────────────────────────────

    def _on_create_note(self, parent_path: str) -> None:
        """Создать новую заметку."""
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
            # Открыть созданную заметку
            rel_path = str(path.relative_to(self._app.vault.path)).replace("\\", "/")
            self._on_file_selected(rel_path)
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать заметку:\n{e}")

    def _on_create_folder(self, parent_path: str) -> None:
        """Создать новую папку."""
        name, ok = QInputDialog.getText(
            self, "Новая папка", "Имя папки:"
        )
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
        """Удалить файл или папку."""
        reply = QMessageBox.question(
            self,
            "Удалить?",
            f"Удалить {rel_path}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            self._app.file_manager.delete(rel_path)
            if self._current_path == rel_path:
                self.editor.clear_editor()
                self._current_path = ""
            self.file_tree.refresh()
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось удалить:\n{e}")

    # ── хранилище ────────────────────────────────────────────

    def _on_open_vault(self) -> None:
        """Открыть диалог выбора хранилища."""
        dialog = VaultDialog(self)
        if dialog.exec():
            self._app.open_vault(dialog.selected_path)

    # ── welcome ──────────────────────────────────────────────

    def _show_welcome(self) -> None:
        self._welcome.show()

    def _hide_welcome(self) -> None:
        self._welcome.hide()

    # ── закрытие ─────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        """Сохранить перед закрытием."""
        self._save_current()
        super().closeEvent(event)


# ── вспомогательная функция ──────────────────────────────────


def QPushButton_(text: str) -> "QPushButton":
    """Создать кнопку-переключатель вида."""
    from PySide6.QtWidgets import QPushButton
    btn = QPushButton(text)
    btn.setFlat(True)
    return btn