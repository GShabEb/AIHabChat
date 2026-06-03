"""Боковая панель классического чата."""

from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QScrollArea,
    QLabel,
    QFrame,
    QMessageBox,
)

from llm.client import LLMClientError
from llm.tools.executor import FileProposal


class _ChatWorker(QThread):
    finished_ok = Signal(str, list)
    finished_err = Signal(str)

    def __init__(self, chat_manager, text: str) -> None:
        super().__init__()
        self._cm = chat_manager
        self._text = text

    def run(self) -> None:
        try:
            before_ids = {p.id for p in self._cm.pending_proposals}
            reply = self._cm.send(self._text)
            new_props = [
                p for p in self._cm.pending_proposals if p.id not in before_ids
            ]
            self.finished_ok.emit(reply, new_props)
        except LLMClientError as e:
            self.finished_err.emit(str(e))
        except Exception as e:
            self.finished_err.emit(f"Ошибка: {e}")


class _ProposalCard(QFrame):
    confirmed = Signal(str)
    rejected = Signal(str)

    def __init__(self, proposal: FileProposal, parent=None) -> None:
        super().__init__(parent)
        self._id = proposal.id
        self.setObjectName("proposalCard")
        self.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        title = QLabel(f"📄 {proposal.summary}")
        title.setWordWrap(True)
        layout.addWidget(title)

        preview = QLabel(proposal.content[:400] + ("…" if len(proposal.content) > 400 else ""))
        preview.setWordWrap(True)
        preview.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(preview)

        ask = QLabel("Создать этот файл в хранилище?")
        ask.setWordWrap(True)
        layout.addWidget(ask)

        row = QHBoxLayout()
        yes_btn = QPushButton("Создать")
        yes_btn.setStyleSheet(
            "QPushButton { background: #2e7d32; color: white; padding: 4px 12px; "
            "border: none; border-radius: 4px; }"
        )
        no_btn = QPushButton("Отмена")
        no_btn.setStyleSheet(
            "QPushButton { background: transparent; color: #888; padding: 4px 12px; }"
        )
        yes_btn.clicked.connect(lambda: self.confirmed.emit(self._id))
        no_btn.clicked.connect(lambda: self.rejected.emit(self._id))
        row.addWidget(yes_btn)
        row.addWidget(no_btn)
        row.addStretch()
        layout.addLayout(row)


class ChatPanel(QWidget):
    """Классический чат: история, ввод, карточки подтверждения файлов."""

    file_created = Signal(str)
    open_settings_requested = Signal()

    def __init__(self, app, parent=None) -> None:
        super().__init__(parent)
        self._app = app
        self._worker: _ChatWorker | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("chatPanel")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("💬 Чат")
        header.setObjectName("sidebarHeader")
        header.setFixedHeight(28)
        layout.addWidget(header)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._messages_host = QWidget()
        self._messages_layout = QVBoxLayout(self._messages_host)
        self._messages_layout.setContentsMargins(8, 8, 8, 8)
        self._messages_layout.setSpacing(8)
        self._messages_layout.addStretch()
        self._scroll.setWidget(self._messages_host)
        layout.addWidget(self._scroll, stretch=1)

        input_row = QHBoxLayout()
        input_row.setContentsMargins(8, 8, 8, 8)
        self._input = QTextEdit()
        self._input.setPlaceholderText("Сообщение… (Enter — отправить, Shift+Enter — строка)")
        self._input.setMaximumHeight(80)
        self._input.setAcceptRichText(False)
        input_row.addWidget(self._input)

        btn_col = QVBoxLayout()
        self._send_btn = QPushButton("Отпр.")
        self._send_btn.setStyleSheet(
            "QPushButton { background: #4a9eff; color: white; padding: 6px 10px; "
            "border: none; border-radius: 4px; font-weight: bold; }"
        )
        self._send_btn.clicked.connect(self._on_send)
        self._clear_btn = QPushButton("Очист.")
        self._clear_btn.setFlat(True)
        self._clear_btn.clicked.connect(self._on_clear)
        btn_col.addWidget(self._send_btn)
        btn_col.addWidget(self._clear_btn)
        input_row.addLayout(btn_col)
        layout.addLayout(input_row)

        self._status = QLabel("")
        self._status.setContentsMargins(8, 0, 8, 6)
        self._status.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self._status)

    def keyPressEvent(self, event) -> None:
        if (
            event.key() in (Qt.Key_Return, Qt.Key_Enter)
            and event.modifiers() & Qt.ShiftModifier == 0
            and self._input.hasFocus()
        ):
            self._on_send()
            event.accept()
            return
        super().keyPressEvent(event)

    def _on_clear(self) -> None:
        self._app.chat_manager.clear_history()
        while self._messages_layout.count() > 1:
            item = self._messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._append_system("История очищена.")

    def _on_send(self) -> None:
        text = self._input.toPlainText().strip()
        if not text:
            return
        if self._worker and self._worker.isRunning():
            return

        if not self._app.chat_manager.is_configured():
            QMessageBox.warning(
                self,
                "Настройки LLM",
                "Укажите URL провайдера, API-ключ и модель\n"
                "в меню Настройки → вкладка «LLM».",
            )
            self.open_settings_requested.emit()
            return

        self._input.clear()
        self._append_message("user", text)
        self._set_busy(True)

        self._worker = _ChatWorker(self._app.chat_manager, text)
        self._worker.finished_ok.connect(self._on_reply)
        self._worker.finished_err.connect(self._on_error)
        self._worker.start()

    def _on_reply(self, text: str, proposals: list) -> None:
        self._set_busy(False)
        self._append_message("assistant", text)
        for p in proposals:
            self._append_proposal(p)

    def _on_error(self, err: str) -> None:
        self._set_busy(False)
        self._append_system(f"⚠ {err}")

    def _set_busy(self, busy: bool) -> None:
        self._send_btn.setEnabled(not busy)
        self._status.setText("Отправка…" if busy else "")

    def _append_message(self, role: str, text: str) -> None:
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if role == "user":
            bubble.setStyleSheet(
                "background: #4a9eff; color: white; padding: 8px 10px; "
                "border-radius: 8px; margin-left: 24px;"
            )
            bubble.setAlignment(Qt.AlignRight)
        else:
            bubble.setStyleSheet(
                "background: #2a2a2a; color: #eee; padding: 8px 10px; "
                "border-radius: 8px; margin-right: 24px;"
            )
        self._insert_widget(bubble)

    def _append_system(self, text: str) -> None:
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #888; font-size: 11px; padding: 4px;")
        self._insert_widget(lbl)

    def _append_proposal(self, proposal: FileProposal) -> None:
        card = _ProposalCard(proposal)
        card.confirmed.connect(self._on_proposal_confirmed)
        card.rejected.connect(self._on_proposal_rejected)
        self._insert_widget(card)

    def _insert_widget(self, widget: QWidget) -> None:
        idx = self._messages_layout.count() - 1
        self._messages_layout.insertWidget(idx, widget)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self) -> None:
        bar = self._scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _on_proposal_confirmed(self, proposal_id: str) -> None:
        try:
            path = self._app.chat_manager.confirm_proposal(proposal_id)
            self._append_system(f"✓ Создан файл: {path}")
            self.file_created.emit(path)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def _on_proposal_rejected(self, proposal_id: str) -> None:
        self._app.chat_manager.reject_proposal(proposal_id)
        self._append_system("Создание файла отменено.")
