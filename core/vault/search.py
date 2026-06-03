"""Поиск по заметкам в vault (заглушка)."""


class VaultSearch:
    """Полнотекстовый поиск по хранилищу — в разработке."""

    def __init__(self, vault_path) -> None:
        self._vault_path = vault_path

    def search(self, query: str) -> list[dict]:
        return []
