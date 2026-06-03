"""Точка входа в GUI-приложение."""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from core.config.config_manager import Config
from core.vault.file_manager import FileManager
from core.vault.markdown_parser import MarkdownParser
from core.vault.vault_manager import VaultManager
from gui.windows.main_window import MainWindow
from llm.chat.chat_manager import ChatManager


class Application:
    """Главный класс приложения — инициализирует все компоненты."""

    def __init__(self) -> None:
        self._qt_app = QApplication(sys.argv)
        self._qt_app.setApplicationName(Config.APP_NAME)
        self._qt_app.setApplicationVersion(Config.APP_VERSION)
        self._qt_app.setOrganizationName(Config.ORG_NAME)

        Config.load_settings()

        self.vault = VaultManager()
        self.file_manager: FileManager | None = None
        self.md_parser = MarkdownParser()
        self.chat_manager = ChatManager()

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
