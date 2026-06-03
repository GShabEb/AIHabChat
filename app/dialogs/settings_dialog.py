"""Диалог настроек приложения."""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QPushButton,
    QGroupBox,
    QTextBrowser,
    QFormLayout,
    QLineEdit,
    QMessageBox,
)
from PySide6.QtCore import Qt, QThread, Signal

from app.config import Config
from llm.client import LLMClientError, fetch_models


# ── шпаргалка Markdown ────────────────────────────────────────

MD_CHEATSHEET = """
<h2 style='margin-top:0'>Шпаргалка Markdown</h2>
<table style='width:100%; border-collapse:collapse'>
<tr><th style='padding:6px; border:1px solid #ddd; text-align:left'>Форматирование</th>
    <th style='padding:6px; border:1px solid #ddd; text-align:left'>Синтаксис</th></tr>
<tr><td style='padding:6px; border:1px solid #ddd'><b>Жирный</b></td>
    <td style='padding:6px; border:1px solid #ddd'><code>**текст**</code> или <code>__текст__</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'><i>Курсив</i></td>
    <td style='padding:6px; border:1px solid #ddd'><code>*текст*</code> или <code>_текст_</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'><b><i>Жирный курсив</i></b></td>
    <td style='padding:6px; border:1px solid #ddd'><code>***текст***</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'><s>Зачёркнутый</s></td>
    <td style='padding:6px; border:1px solid #ddd'><code>~~текст~~</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>Подчёркнутый</td>
    <td style='padding:6px; border:1px solid #ddd'><u>HTML:</u> <code><u>текст</u></code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'><code>Код (inline)</code></td>
    <td style='padding:6px; border:1px solid #ddd'><code>`код`</code></td></tr>
</table>
<br>
<table style='width:100%; border-collapse:collapse'>
<tr><th style='padding:6px; border:1px solid #ddd; text-align:left'>Заголовки</th>
    <th style='padding:6px; border:1px solid #ddd; text-align:left'>Синтаксис</th></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>H1</td>
    <td style='padding:6px; border:1px solid #ddd'><code># Заголовок</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>H2</td>
    <td style='padding:6px; border:1px solid #ddd'><code>## Заголовок</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>H3</td>
    <td style='padding:6px; border:1px solid #ddd'><code>### Заголовок</code></td></tr>
</table>
<br>
<table style='width:100%; border-collapse:collapse'>
<tr><th style='padding:6px; border:1px solid #ddd; text-align:left'>Списки</th>
    <th style='padding:6px; border:1px solid #ddd; text-align:left'>Синтаксис</th></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>Маркированный</td>
    <td style='padding:6px; border:1px solid #ddd'><code>- элемент</code> или <code>* элемент</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>Нумерованный</td>
    <td style='padding:6px; border:1px solid #ddd'><code>1. элемент</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>Чекбокс</td>
    <td style='padding:6px; border:1px solid #ddd'><code>- [ ] задача</code> / <code>- [x] готово</code></td></tr>
</table>
<br>
<table style='width:100%; border-collapse:collapse'>
<tr><th style='padding:6px; border:1px solid #ddd; text-align:left'>Другое</th>
    <th style='padding:6px; border:1px solid #ddd; text-align:left'>Синтаксис</th></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>Ссылка</td>
    <td style='padding:6px; border:1px solid #ddd'><code>[текст](URL)</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>Изображение</td>
    <td style='padding:6px; border:1px solid #ddd'><code>![alt](URL)</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>Цитата</td>
    <td style='padding:6px; border:1px solid #ddd'><code>> цитата</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>Горизонтальная линия</td>
    <td style='padding:6px; border:1px solid #ddd'><code>---</code> или <code>***</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>Блок кода</td>
    <td style='padding:6px; border:1px solid #ddd'><code>```язык<br>код<br>```</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>Таблица</td>
    <td style='padding:6px; border:1px solid #ddd'><code>| A | B |<br>|---|---|<br>| 1 | 2 |</code></td></tr>
<tr><td style='padding:6px; border:1px solid #ddd'>Блок-схема</td>
    <td style='padding:6px; border:1px solid #ddd'><code>```mermaid<br>graph TD<br>A-->B<br>```</code></td></tr>
</table>
"""


class _ModelsFetchWorker(QThread):
    ok = Signal(list)
    err = Signal(str)

    def __init__(self, base_url: str, api_key: str) -> None:
        super().__init__()
        self._base = base_url
        self._key = api_key

    def run(self) -> None:
        try:
            models = fetch_models(self._base, self._key)
            self.ok.emit(models)
        except LLMClientError as e:
            self.err.emit(str(e))
        except Exception as e:
            self.err.emit(str(e))


class SettingsDialog(QDialog):
    """Диалог настроек: оформление, редактор, шпаргалка MD."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._load_current()

    # ── UI ────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setWindowTitle("Настройки")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Вкладки
        tabs = QTabWidget()
        tabs.addTab(self._create_general_tab(), "Оформление")
        tabs.addTab(self._create_editor_tab(), "Редактор")
        tabs.addTab(self._create_llm_tab(), "LLM")
        tabs.addTab(self._create_cheatsheet_tab(), "Шпаргалка MD")
        self._models_worker: _ModelsFetchWorker | None = None
        layout.addWidget(tabs)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Сохранить")
        save_btn.setDefault(True)
        save_btn.setStyleSheet(
            "QPushButton { background-color: #4a9eff; color: white; "
            "padding: 6px 20px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background-color: #3a8eef; }"
        )
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    # ── вкладка: Оформление ──────────────────────────────────

    def _create_general_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Тема
        theme_group = QGroupBox("Тема оформления")
        theme_layout = QFormLayout(theme_group)
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["Светлая", "Тёмная"])
        theme_layout.addRow("Тема:", self._theme_combo)
        layout.addWidget(theme_group)

        layout.addStretch()
        return widget

    # ── вкладка: Редактор ────────────────────────────────────

    def _create_editor_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Редактор
        editor_group = QGroupBox("Настройки редактора")
        editor_layout = QFormLayout(editor_group)

        self._tab_spin = QSpinBox()
        self._tab_spin.setRange(1, 8)
        self._tab_spin.setSuffix(" пробелов")
        editor_layout.addRow("Размер табуляции:", self._tab_spin)

        self._line_numbers_check = QCheckBox("Показать нумерацию строк")
        editor_layout.addRow(self._line_numbers_check)

        self._live_preview_check = QCheckBox("Живой предпросмотр (обновлять при вводе)")
        editor_layout.addRow(self._live_preview_check)

        layout.addWidget(editor_group)

        layout.addStretch()
        return widget

    # ── вкладка: LLM ─────────────────────────────────────────

    def _create_llm_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Провайдер LLM (OpenAI-совместимый API)")
        form = QFormLayout(group)

        self._llm_url = QLineEdit()
        self._llm_url.setPlaceholderText("https://api.claudehub.fun")
        form.addRow("URL агрегатора:", self._llm_url)

        self._llm_key = QLineEdit()
        self._llm_key.setEchoMode(QLineEdit.Password)
        self._llm_key.setPlaceholderText("API-ключ")
        form.addRow("API-ключ:", self._llm_key)

        model_row = QHBoxLayout()
        self._llm_model = QComboBox()
        self._llm_model.setEditable(False)
        self._llm_model.setMinimumWidth(220)
        model_row.addWidget(self._llm_model, stretch=1)

        self._fetch_models_btn = QPushButton("Загрузить модели")
        self._fetch_models_btn.clicked.connect(self._on_fetch_models)
        model_row.addWidget(self._fetch_models_btn)
        form.addRow("Модель:", model_row)

        layout.addWidget(group)

        hint = QLabel(
            "Сначала укажите URL и API-ключ, нажмите «Загрузить модели», "
            "затем выберите модель из списка. "
            "ClaudeHub API: https://api.claudehub.fun "
            "(клиент добавит /v1 автоматически). "
            "Не используйте app.claudehub.fun — это только сайт."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(hint)

        self._llm_status = QLabel("")
        self._llm_status.setWordWrap(True)
        self._llm_status.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self._llm_status)

        layout.addStretch()
        return widget

    def _fill_model_combo(self, models: list[str], selected: str = "") -> None:
        self._llm_model.clear()
        self._llm_model.addItems(models)
        if selected:
            idx = self._llm_model.findText(selected)
            if idx >= 0:
                self._llm_model.setCurrentIndex(idx)
            else:
                self._llm_model.insertItem(0, selected)
                self._llm_model.setCurrentIndex(0)

    def _on_fetch_models(self) -> None:
        base = self._llm_url.text().strip()
        key = self._llm_key.text().strip()
        if not base or not key:
            QMessageBox.warning(
                self, "LLM", "Укажите URL агрегатора и API-ключ."
            )
            return
        self._fetch_models_btn.setEnabled(False)
        self._llm_status.setText("Загрузка списка моделей…")
        self._models_worker = _ModelsFetchWorker(base, key)
        self._models_worker.ok.connect(self._on_models_loaded)
        self._models_worker.err.connect(self._on_models_error)
        self._models_worker.finished.connect(
            lambda: self._fetch_models_btn.setEnabled(True)
        )
        self._models_worker.start()

    def _on_models_loaded(self, models: list[str]) -> None:
        Config.set("llm_models", models)
        sel = self._llm_model.currentText() or Config.get("llm_model", "")
        self._fill_model_combo(models, sel)
        self._llm_status.setText(f"Загружено моделей: {len(models)}")

    def _on_models_error(self, err: str) -> None:
        self._llm_status.setText(f"Ошибка: {err}")

    # ── вкладка: Шпаргалка MD ────────────────────────────────

    def _create_cheatsheet_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(MD_CHEATSHEET)
        layout.addWidget(browser)

        return widget

    # ── загрузка / сохранение ────────────────────────────────

    def _load_current(self) -> None:
        """Загрузить текущие настройки в виджеты."""
        theme = Config.get("theme", "light")
        self._theme_combo.setCurrentIndex(0 if theme == "light" else 1)
        self._tab_spin.setValue(Config.get("tab_size", 4))
        self._line_numbers_check.setChecked(Config.get("show_line_numbers", True))
        self._live_preview_check.setChecked(Config.get("live_preview", True))

        url = Config.get("llm_base_url", "https://api.claudehub.fun")
        if "://app.claudehub.fun" in url:
            url = url.replace("://app.claudehub.fun", "://api.claudehub.fun")
        self._llm_url.setText(url)
        self._llm_key.setText(Config.get("llm_api_key", ""))
        cached = Config.get("llm_models", []) or []
        if cached:
            self._fill_model_combo(cached, Config.get("llm_model", ""))
        elif Config.get("llm_model"):
            self._fill_model_combo([Config.get("llm_model")], Config.get("llm_model"))

    def _on_save(self) -> None:
        """Сохранить настройки."""
        Config.set("theme", "light" if self._theme_combo.currentIndex() == 0 else "dark")
        Config.set("tab_size", self._tab_spin.value())
        Config.set("show_line_numbers", self._line_numbers_check.isChecked())
        Config.set("live_preview", self._live_preview_check.isChecked())
        Config.set("llm_base_url", self._llm_url.text().strip())
        Config.set("llm_api_key", self._llm_key.text().strip())
        Config.set("llm_model", self._llm_model.currentText().strip())
        self.accept()