"""Стили светлой и тёмной темы — чистый белый / чёрный без серых подложек."""

THEME_LIGHT = """
QWidget { background-color: #ffffff; color: #000000; }
QMainWindow { background-color: #ffffff; }
#sidebar { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
#sidebarHeader {
    padding: 4px 8px; font-weight: bold; font-size: 12px;
    background-color: #ffffff; border-bottom: 1px solid #e0e0e0; color: #000000;
}
#workArea { background-color: #ffffff; }
#topBar {
    background-color: #ffffff; border-bottom: 1px solid #e0e0e0;
    min-height: 26px; max-height: 26px;
}
#noteTitle {
    background-color: #ffffff; color: #000000;
    border: none; border-bottom: 1px solid #e0e0e0;
    padding: 2px 12px; font-size: 18px; font-weight: 600;
    min-height: 32px; max-height: 32px;
}
QMenuBar { background-color: #ffffff; color: #000000; padding: 0; }
QMenuBar::item { padding: 4px 8px; color: #000000; }
QMenuBar::item:selected { background-color: #e8f4ff; }
QMenu { background-color: #ffffff; color: #000000; border: 1px solid #e0e0e0; }
QMenu::item:selected { background-color: #4a9eff; color: #ffffff; }
QStatusBar { background-color: #ffffff; color: #666666; border-top: 1px solid #e0e0e0; }
QTreeWidget { background-color: #ffffff; border: none; color: #000000; }
QTreeWidget::item { color: #000000; padding: 2px 0; }
QTreeWidget::item:selected { background-color: #4a9eff; color: #ffffff; }
QTreeWidget::item:hover:!selected { background-color: #f0f7ff; }
QPlainTextEdit, QTextEdit {
    background-color: #ffffff; color: #000000; border: none; padding: 8px;
    selection-background-color: #b3d7ff; selection-color: #000000;
}
QTextBrowser { background-color: #ffffff; color: #000000; border: none; }
QLineEdit { background-color: #ffffff; color: #000000; border: 1px solid #e0e0e0; }
QLabel { color: #000000; background: transparent; }
QPushButton { color: #000000; background: transparent; }
QSplitter { background-color: #ffffff; }
QSplitter::handle { background-color: #e0e0e0; width: 1px; }
QScrollBar:vertical { background: #ffffff; width: 10px; border: none; }
QScrollBar::handle:vertical { background: #cccccc; border-radius: 4px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #ffffff; height: 10px; border: none; }
QScrollBar::handle:horizontal { background: #cccccc; border-radius: 4px; min-width: 24px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QDialog { background-color: #ffffff; color: #000000; }
QGroupBox { color: #000000; border: 1px solid #e0e0e0; margin-top: 8px; padding-top: 8px; }
QTabWidget::pane { border: 1px solid #e0e0e0; background: #ffffff; }
QTabBar::tab {
    background: #ffffff; color: #000000; padding: 6px 12px;
    border: 1px solid #e0e0e0; border-bottom: none;
}
QTabBar::tab:selected { background: #ffffff; border-bottom: 2px solid #4a9eff; }
QComboBox, QSpinBox {
    background: #ffffff; color: #000000; border: 1px solid #e0e0e0; padding: 4px;
}
QComboBox QAbstractItemView {
    background: #ffffff; color: #000000; selection-background-color: #4a9eff;
}
QCheckBox { color: #000000; }
#chatPanel { background-color: #ffffff; }
#proposalCard { background-color: #f8f8f8; border: 1px solid #e0e0e0; border-radius: 6px; }
"""

THEME_DARK = """
QWidget { background-color: #000000; color: #ffffff; }
QMainWindow { background-color: #000000; }
#sidebar { background-color: #000000; border-right: 1px solid #333333; }
#sidebarHeader {
    padding: 4px 8px; font-weight: bold; font-size: 12px;
    background-color: #000000; border-bottom: 1px solid #333333; color: #ffffff;
}
#workArea { background-color: #000000; }
#topBar {
    background-color: #000000; border-bottom: 1px solid #333333;
    min-height: 26px; max-height: 26px;
}
#noteTitle {
    background-color: #000000; color: #ffffff;
    border: none; border-bottom: 1px solid #333333;
    padding: 2px 12px; font-size: 18px; font-weight: 600;
    min-height: 32px; max-height: 32px;
}
QMenuBar { background-color: #000000; color: #ffffff; padding: 0; }
QMenuBar::item { padding: 4px 8px; color: #ffffff; }
QMenuBar::item:selected { background-color: #1a1a1a; }
QMenu { background-color: #000000; color: #ffffff; border: 1px solid #333333; }
QMenu::item { color: #ffffff; }
QMenu::item:selected { background-color: #4a9eff; color: #ffffff; }
QStatusBar { background-color: #000000; color: #aaaaaa; border-top: 1px solid #333333; }
QTreeWidget { background-color: #000000; border: none; color: #ffffff; }
QTreeWidget::item { color: #ffffff; padding: 2px 0; }
QTreeWidget::item:selected { background-color: #4a9eff; color: #ffffff; }
QTreeWidget::item:hover:!selected { background-color: #1a1a1a; }
QPlainTextEdit, QTextEdit {
    background-color: #000000; color: #ffffff; border: none; padding: 8px;
    selection-background-color: #264f78; selection-color: #ffffff;
}
QTextBrowser { background-color: #000000; color: #ffffff; border: none; }
QLineEdit { background-color: #000000; color: #ffffff; border: 1px solid #333333; }
QLabel { color: #ffffff; background: transparent; }
QPushButton { color: #ffffff; background: transparent; }
QSplitter { background-color: #000000; }
QSplitter::handle { background-color: #333333; width: 1px; }
QScrollBar:vertical { background: #000000; width: 10px; border: none; }
QScrollBar::handle:vertical { background: #444444; border-radius: 4px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #000000; height: 10px; border: none; }
QScrollBar::handle:horizontal { background: #444444; border-radius: 4px; min-width: 24px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QDialog, QMessageBox, QInputDialog { background-color: #000000; color: #ffffff; }
QGroupBox { color: #ffffff; border: 1px solid #333333; margin-top: 8px; padding-top: 8px; }
QTabWidget::pane { border: 1px solid #333333; background: #000000; }
QTabBar::tab {
    background: #000000; color: #ffffff; padding: 6px 12px;
    border: 1px solid #333333; border-bottom: none;
}
QTabBar::tab:selected { background: #000000; border-bottom: 2px solid #4a9eff; }
QComboBox, QSpinBox {
    background: #000000; color: #ffffff; border: 1px solid #333333; padding: 4px;
}
QComboBox QAbstractItemView {
    background: #000000; color: #ffffff; selection-background-color: #4a9eff;
}
QCheckBox { color: #ffffff; }
#chatPanel { background-color: #000000; }
#proposalCard { background-color: #0a0a0a; border: 1px solid #333333; border-radius: 6px; }
"""
