# 📋 План Организации scripts/

## 🎯 Текущая Проблема

В `scripts/` находится **87 файлов** без четкой структуры:
- Тесты (Python и PowerShell)
- Демо-скрипты
- Утилиты
- Интеграции с Qwen
- Системные скрипты
- Документация

## 🏗️ Предлагаемая Структура

```
scripts/
├── tests/                      # ✅ УЖЕ СОЗДАНО
│   ├── unit/                   # Юнит-тесты (5 файлов)
│   ├── integration/            # Интеграционные (3 файла)
│   └── verification/           # Проверка (1 файл)
│
├── demos/                      # 🆕 Демонстрационные скрипты
│   ├── autonomy/               # Демо автономности
│   ├── self-modification/      # Демо самомодификации
│   └── system/                 # Системные демо
│
├── utils/                      # 🆕 Утилиты
│   ├── backup/                 # Бэкапы
│   ├── monitoring/             # Мониторинг
│   └── system/                 # Системные утилиты
│
├── qwen/                       # 🆕 Интеграция с Qwen
│   ├── import/                 # Импорт чатов
│   ├── export/                 # Экспорт данных
│   └── api/                    # API интеграция
│
├── legacy/                     # 🆕 Устаревшие тесты
│   └── powershell-tests/       # Старые PS тесты
│
└── docs/                       # 🆕 Документация скриптов
    └── README.md
```

## 📦 Категоризация Файлов

### ✅ Тесты (Уже Структурированы)
**Местоположение:** `scripts/tests/`

**Python тесты (9 файлов) - ПЕРЕМЕЩЕНЫ:**
- ✅ test-tree-of-thought.py → tests/unit/
- ✅ test-self-modification.py → tests/unit/
- ✅ test-autonomous-optimizer.py → tests/unit/
- ✅ test-proactive-engine.py → tests/unit/
- ✅ test-knowledge-store.py → tests/unit/
- ✅ test-execution.py → tests/integration/
- ✅ test-improvements.py → tests/integration/
- ✅ test-full-system.py → tests/integration/
- ✅ verify-readme-claims.py → tests/verification/

**Python тесты (2 файла) - ОСТАВИТЬ:**
- test-web-behavior.py (специфичный тест веб-интерфейса)
- test-qwen-api-direct.py (специфичный тест Qwen API)

**PowerShell тесты (23 файла) - ПЕРЕМЕСТИТЬ В legacy/:**
- test-9-levels.ps1
- test-adaptive-learning.ps1
- test-adaptive-planning.ps1
- test-arch-engine.ps1
- test-code-generation.ps1
- test-complete-system.ps1
- test-decision-engine.ps1
- test-final-autonomous.ps1
- test-full-autonomy.ps1
- test-improved-core.ps1
- test-intelligence.ps1
- test-loop-prevention.ps1
- test-new-model.ps1
- test-predictive.ps1
- test-query.ps1
- test-qwen-history-search.ps1
- test-qwen-mcp.ps1
- test-qwen-via-mcp.ps1
- test-real-execution.ps1
- test-self-improvement.ps1
- full-system-check.ps1 (оставить в корне - активно используется)
- stress-test.ps1 (оставить в корне - активно используется)
- quick-test.ps1 (оставить в корне - активно используется)

### 🎭 Демо-скрипты (16 файлов)
**Переместить в:** `scripts/demos/`

**Autonomy Demos (4 файла) → demos/autonomy/:**
- demo-autonomy.ps1
- demo-autonomous-live.ps1
- demo-autonomous-tasks.ps1
- demo-fully-autonomous.ps1

**Self-Modification Demos (9 файлов) → demos/self-modification/:**
- demo-agenda-self-modification.ps1
- demo-code-self-modification.ps1
- demo-core-self-modification.ps1
- demo-declarative-vs-imperative.ps1
- demo-loop-prevention-live.ps1
- demo-modification-comparison.ps1
- demo-permanent-modification.ps1
- demo-real-code-modification.ps1
- demo-real-self-modification.ps1
- demo-self-healing-rollback.ps1
- demo-self-modification-simple.ps1
- demo-self-modification.ps1

**System Demos (3 файла) → demos/system/:**
- demo-full-stack.ps1
- demo-interactive-session.ps1
- demo-real-scenario.ps1
- demo-system.py
- demo-system.sh

### 🔧 Утилиты (15 файлов)
**Переместить в:** `scripts/utils/`

**Backup (3 файла) → utils/backup/:**
- backup-mongodb.ps1
- backup.ps1
- rollback.ps1

**Monitoring (3 файла) → utils/monitoring/:**
- monitor-production.ps1
- health-check.ps1
- hardware-report.py

**System (9 файлов) → utils/system/:**
- bootstrap.ps1
- system-info.sh
- system-stats.py
- wsl-system-info.sh
- ingest-docs.ps1
- create-dashboard.py
- ask-system.py
- research-autonomous-capabilities.ps1
- find-agent-models.ps1

### 🤖 Qwen Integration (12 файлов)
**Переместить в:** `scripts/qwen/`

**Import (5 файлов) → qwen/import/:**
- import-mongodb-chats-to-rag.ps1
- import-qwen-chats-to-rag.ps1
- import-qwen-export-batch.ps1
- import-qwen-export-to-rag.ps1
- setup-qwen-mongo.ps1

**Export (2 файла) → qwen/export/:**
- export-qwen-chats-to-rag.ps1
- fetch-qwen-chats.py

**API (5 файлов) → qwen/api/:**
- discover-qwen-api.ps1
- edit-qwen-config.ps1
- get-qwen-chats-via-client.py
- refresh-qwen-cookies.ps1
- refresh-qwen.ps1
- find-messages-endpoint.py

### 📝 Документация (3 файла)
**Переместить в:** `scripts/docs/`
- TESTS-INDEX.md
- VERIFY-README.md
- PUBLISH-README.md

### 🚀 Публикация (2 файла)
**Оставить в корне:**
- publish-to-github.py
- publish-to-github-cli.py

### 🗑️ Дубликаты (Удалить после проверки)
**Python тесты в корне (уже есть в tests/):**
- test-autonomous-optimizer.py
- test-execution.py
- test-full-system.py
- test-improvements.py
- test-knowledge-store.py
- test-proactive-engine.py
- test-self-modification.py
- test-tree-of-thought.py
- verify-readme-claims.py

## 📊 Итоговая Структура

```
scripts/
├── 📁 tests/                           # 9 файлов (структурировано)
│   ├── unit/ (5)
│   ├── integration/ (3)
│   └── verification/ (1)
│
├── 📁 demos/                           # 16 файлов
│   ├── autonomy/ (4)
│   ├── self-modification/ (12)
│   └── system/ (5)
│
├── 📁 utils/                           # 15 файлов
│   ├── backup/ (3)
│   ├── monitoring/ (3)
│   └── system/ (9)
│
├── 📁 qwen/                            # 12 файлов
│   ├── import/ (5)
│   ├── export/ (2)
│   └── api/ (5)
│
├── 📁 legacy/                          # 20 файлов
│   └── powershell-tests/ (20)
│
├── 📁 docs/                            # 3 файла
│   └── *.md
│
└── 📄 Корневые файлы (7)              # Активно используемые
    ├── full-system-check.ps1
    ├── stress-test.ps1
    ├── quick-test.ps1
    ├── publish-to-github.py
    ├── publish-to-github-cli.py
    ├── test-web-behavior.py
    └── test-qwen-api-direct.py
```

## 🎯 Преимущества

### До
- ❌ 87 файлов в одной папке
- ❌ Нет структуры
- ❌ Сложно найти нужный скрипт
- ❌ Дубликаты

### После
- ✅ Логическая структура по категориям
- ✅ Легко найти нужный скрипт
- ✅ Нет дубликатов
- ✅ Профессиональная организация

## 🚀 План Выполнения

### Фаза 1: Создание Структуры
```bash
mkdir scripts/demos/autonomy
mkdir scripts/demos/self-modification
mkdir scripts/demos/system
mkdir scripts/utils/backup
mkdir scripts/utils/monitoring
mkdir scripts/utils/system
mkdir scripts/qwen/import
mkdir scripts/qwen/export
mkdir scripts/qwen/api
mkdir scripts/legacy/powershell-tests
mkdir scripts/docs
```

### Фаза 2: Перемещение Файлов
- Переместить демо-скрипты
- Переместить утилиты
- Переместить Qwen интеграцию
- Переместить legacy тесты
- Переместить документацию

### Фаза 3: Удаление Дубликатов
- Удалить Python тесты из корня (уже в tests/)

### Фаза 4: Документация
- Создать README.md в каждой категории
- Обновить главный README.md
- Создать MIGRATION-GUIDE.md

### Фаза 5: Проверка
- Проверить работоспособность скриптов
- Обновить пути в документации
- Коммит и push

## ⚠️ Важно

**Не трогать:**
- scripts/tests/ (уже структурировано)
- Активно используемые скрипты в корне

**Можно удалить после проверки:**
- Дубликаты Python тестов в корне
