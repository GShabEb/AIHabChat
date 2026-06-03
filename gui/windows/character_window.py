"""Окно персонажа / роли ассистента (заглушка)."""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel


class CharacterWindow(QDialog):
    """Настройка персонажа LLM — в разработке."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Персонаж")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Настройка персонажа ассистента — в разработке."))
