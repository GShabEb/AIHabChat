"""Работа с файловой системой внутри vault: чтение, запись, список файлов."""

import shutil
from pathlib import Path


def _is_note_file(path: Path) -> bool:
    """Поддерживаемые заметки: md, mermaid, mmd."""
    name = path.name.lower()
    if name.endswith(".mermaid.md") or name.endswith(".mermaid") or name.endswith(".mmd"):
        return True
    return path.suffix.lower() in {".md", ".txt", ".markdown"}


class FileManager:
    """Менеджер файлов хранилища."""

    SUPPORTED_EXTENSIONS = {".md", ".txt", ".markdown", ".mermaid", ".mmd"}

    def __init__(self, vault_path: Path) -> None:
        self._root = vault_path

    def read_file(self, relative_path: str) -> str:
        """Прочитать текстовый файл из хранилища."""
        full = self._resolve(relative_path)
        if not full.is_file():
            raise FileNotFoundError(full)
        return full.read_text(encoding="utf-8")

    def write_file(self, relative_path: str, content: str) -> None:
        """Записать текстовый файл в хранилище."""
        full = self._resolve(relative_path)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")

    def create_note(self, relative_path: str) -> Path:
        """Создать пустую заметку. Без расширения — добавляет .md."""
        lower = relative_path.lower()
        has_ext = (
            lower.endswith(".md")
            or lower.endswith(".mermaid")
            or lower.endswith(".mmd")
            or lower.endswith(".txt")
            or lower.endswith(".markdown")
        )
        if not has_ext:
            relative_path += ".md"
        full = self._resolve(relative_path)
        full.parent.mkdir(parents=True, exist_ok=True)
        if not full.exists():
            full.write_text("", encoding="utf-8")
        return full

    def create_folder(self, relative_path: str) -> Path:
        """Создать папку внутри хранилища."""
        full = self._resolve(relative_path)
        full.mkdir(parents=True, exist_ok=True)
        return full

    def delete(self, relative_path: str) -> None:
        """Удалить файл или папку (включая непустую)."""
        full = self._resolve(relative_path)
        if full.is_file():
            full.unlink()
        elif full.is_dir():
            shutil.rmtree(full)

    def rename(self, old_rel: str, new_rel: str) -> None:
        """Переименовать / переместить файл или папку."""
        old = self._resolve(old_rel)
        new = self._resolve(new_rel)
        new.parent.mkdir(parents=True, exist_ok=True)
        old.rename(new)

    def list_files(self, relative_dir: str = "") -> list[Path]:
        """Список файлов (включая вложенные) в директории."""
        target = self._resolve(relative_dir)
        if not target.is_dir():
            return []
        return sorted(p for p in target.rglob("*") if p.is_file() and _is_note_file(p))

    def walk_tree(self, relative_dir: str = "") -> list[dict]:
        """
        Вернуть дерево вида:
        [
            {"name": "Папка", "type": "folder", "children": [...]},
            {"name": "Заметка.md", "type": "file", "path": "relative/path.md"},
        ]
        """
        target = self._resolve(relative_dir)
        if not target.is_dir():
            return []
        return self._build_tree(target)

    def _resolve(self, relative_path: str) -> Path:
        full = (self._root / relative_path).resolve()
        if not str(full).startswith(str(self._root)):
            raise ValueError("Путь выходит за пределы хранилища")
        return full

    def _build_tree(self, directory: Path) -> list[dict]:
        items: list[dict] = []
        try:
            entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            return items

        for entry in entries:
            rel = entry.relative_to(self._root)
            if entry.is_dir():
                children = self._build_tree(entry)
                items.append({
                    "name": entry.name,
                    "type": "folder",
                    "path": str(rel).replace("\\", "/"),
                    "children": children,
                })
            elif _is_note_file(entry):
                items.append({
                    "name": entry.name,
                    "type": "file",
                    "path": str(rel).replace("\\", "/"),
                })
        return items
