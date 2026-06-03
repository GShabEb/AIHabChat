"""AiHabChat — LLM-хаб с Markdown-редактором заметок.

Точка входа в приложение.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в sys.path для корректных импортов
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.application import Application


def main() -> int:
    app = Application()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())