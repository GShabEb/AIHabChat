# AiHabChat

LLM-хаб с Markdown-редактором заметок (аналог Obsidian).

## Возможности

- **Хранилище (Vault)** — выбор root-папки для заметок (как в Obsidian)
- **Дерево файлов** — навигация по заметкам в формате tree
- **Редактор Markdown** — редактирование с монопространственным шрифтом
- **Предпросмотр** — рендеринг Markdown → HTML, Mermaid-диаграммы
- **Разделённый вид** — редактор и предпросмотр рядом
- **Автосохранение** — автоматическое сохранение каждые 3 секунды
- **Классический чат** — LLM с инструментами создания заметок и диаграмм

## Структура проекта

```
AiHabChat/
├── main.py                      # Точка входа
├── requirements.txt
├── README.md
├── config/
│   ├── app_config.json          # Константы приложения
│   ├── models.json              # Метаданные LLM-провайдеров
│   └── themes.json              # Метаданные тем
├── gui/                         # GUI (PySide6)
│   ├── application.py
│   ├── themes/styles.py
│   ├── windows/                 # main_window, settings_window, vault_dialog
│   └── widgets/                 # note, tree, preview, chat
├── core/
│   ├── config/config_manager.py # Config + пользовательские настройки
│   ├── vault/                   # vault_manager, file_manager, markdown_parser
│   ├── services/                # export, sync, indexing (заготовки)
│   └── events/event_bus.py
├── llm/
│   ├── providers/               # base, claudehub, openrouter, ollama, local
│   ├── chat/chat_manager.py
│   ├── context/                 # заготовки
│   ├── memory/                  # заготовки
│   └── tools/                   # create_note, tool_manager, export
├── rp/                          # character_manager, rp_engine (заготовки)
├── mobile_api/                  # api_server, auth, routes/ (заготовки)
├── data/cache, logs, temp/
├── tests/
└── user_vaults/                 # локальные хранилища (не в git)
```

## Установка

```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
```

## Запуск

```bash
python main.py
```

## Горячие клавиши

| Комбинация | Действие |
|------------|----------|
| Ctrl+O | Открыть хранилище |
| Ctrl+N | Новая заметка |
| Ctrl+S | Сохранить |
| Ctrl+Q | Выход |

## Планы

- [ ] OpenRouter, Ollama, локальные провайдеры
- [ ] Полноценный чат (отдельное окно)
- [ ] Поиск по заметкам, индексация
- [ ] Wikilinks и обратные ссылки
- [ ] Mobile API
