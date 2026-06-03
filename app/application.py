"""Точка входа в GUI-приложение."""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.config import Config
from app.windows.main_window import MainWindow
from core.vault import Vault
from core.file_manager import FileManager
from core.markdown_parser import MarkdownParser
from llm.chat_manager import ChatManager


class Application:
    """Главный класс приложения — инициализирует все компоненты."""

    def __init__(self) -> None:
        self._qt_app = QApplication(sys.argv)
        self._qt_app.setApplicationName(Config.APP_NAME)
        self._qt_app.setApplicationVersion(Config.APP_VERSION)
        self._qt_app.setOrganizationName(Config.ORG_NAME)

        # Ядро
        self.vault = Vault()
        self.file_manager: FileManager | None = None
        self.md_parser = MarkdownParser()
        self.chat_manager = ChatManager()

        # Главное окно
        self.main_window = MainWindow(self)

    def open_vault(self, path: str) -> None:
        """Открыть хранилище и обновить компоненты."""
        self.vault.open(path)
        self.file_manager = FileManager(self.vault.path)
        self.main_window.on_vault_opened()

    def run(self) -> int:
        """Запустить приложение."""
        self.main_window.show()
        return self._qt_app.exec()