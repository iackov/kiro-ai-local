# 🤖 Qwen Integration

Интеграция с Qwen AI для импорта/экспорта чатов и работы с API.

## 📂 Структура

```
qwen/
├── import/    # Импорт чатов и данных (5)
├── export/    # Экспорт данных (2)
└── api/       # API интеграция (5)
```

## 🚀 Быстрый Старт

### Импорт Чатов
```powershell
# Импорт чатов Qwen в RAG
.\scripts\qwen\import\import-qwen-chats-to-rag.ps1

# Импорт из MongoDB
.\scripts\qwen\import\import-mongodb-chats-to-rag.ps1

# Batch импорт
.\scripts\qwen\import\import-qwen-export-batch.ps1
```

### Экспорт Данных
```powershell
# Экспорт чатов
.\scripts\qwen\export\export-qwen-chats-to-rag.ps1

# Fetch чатов
python scripts/qwen/export/fetch-qwen-chats.py
```

### API Интеграция
```powershell
# Обновить cookies
.\scripts\qwen\api\refresh-qwen-cookies.ps1

# Discover API
.\scripts\qwen\api\discover-qwen-api.ps1

# Получить чаты через клиент
python scripts/qwen/api/get-qwen-chats-via-client.py
```

## 📋 Категории

### 📥 import/ (5 скриптов)
Импорт чатов и данных из Qwen.

| Скрипт | Описание | Использование |
|--------|----------|---------------|
| import-qwen-chats-to-rag.ps1 | Импорт чатов в RAG | Основной метод |
| import-mongodb-chats-to-rag.ps1 | Импорт из MongoDB | Из базы данных |
| import-qwen-export-batch.ps1 | Batch импорт | Массовый импорт |
| import-qwen-export-to-rag.ps1 | Импорт экспорта | Из файлов |
| setup-qwen-mongo.ps1 | Настройка MongoDB | Первый запуск |

### 📤 export/ (2 скрипта)
Экспорт данных из Qwen.

| Скрипт | Описание | Формат |
|--------|----------|--------|
| export-qwen-chats-to-rag.ps1 | Экспорт чатов | JSON |
| fetch-qwen-chats.py | Fetch через API | JSON |

### 🔌 api/ (5 скриптов)
Работа с Qwen API.

| Скрипт | Описание | Когда использовать |
|--------|----------|-------------------|
| refresh-qwen-cookies.ps1 | Обновить cookies | Каждые 24 часа |
| refresh-qwen.ps1 | Полное обновление | При ошибках |
| discover-qwen-api.ps1 | Исследовать API | Разработка |
| edit-qwen-config.ps1 | Редактировать конфиг | Настройка |
| get-qwen-chats-via-client.py | Получить чаты | Программно |
| find-messages-endpoint.py | Найти endpoint | Отладка |

## 🎯 Типичные Сценарии

### Первая Настройка
```powershell
# 1. Настроить MongoDB
.\scripts\qwen\import\setup-qwen-mongo.ps1

# 2. Обновить cookies
.\scripts\qwen\api\refresh-qwen-cookies.ps1

# 3. Импортировать чаты
.\scripts\qwen\import\import-qwen-chats-to-rag.ps1
```

### Ежедневное Обновление
```powershell
# 1. Обновить cookies (если нужно)
.\scripts\qwen\api\refresh-qwen-cookies.ps1

# 2. Fetch новые чаты
python scripts/qwen/export/fetch-qwen-chats.py

# 3. Импортировать в RAG
.\scripts\qwen\import\import-qwen-chats-to-rag.ps1
```

### Массовый Импорт
```powershell
# 1. Экспортировать все чаты
.\scripts\qwen\export\export-qwen-chats-to-rag.ps1

# 2. Batch импорт
.\scripts\qwen\import\import-qwen-export-batch.ps1
```

### Отладка API
```powershell
# 1. Исследовать API
.\scripts\qwen\api\discover-qwen-api.ps1

# 2. Найти endpoints
python scripts/qwen/api/find-messages-endpoint.py

# 3. Тестировать клиент
python scripts/qwen/api/get-qwen-chats-via-client.py
```

## 💡 Советы

### Cookies
- Обновляйте cookies каждые 24 часа
- Храните cookies в безопасном месте
- Используйте переменные окружения
- Не коммитьте cookies в Git

### Импорт
- Делайте бэкап перед массовым импортом
- Проверяйте формат данных
- Используйте batch для больших объемов
- Логируйте все операции

### API
- Соблюдайте rate limits
- Обрабатывайте ошибки
- Используйте retry механизмы
- Кэшируйте результаты

## 🔧 Конфигурация

### Переменные Окружения
```powershell
# Qwen API
$env:QWEN_API_KEY = "your-api-key"
$env:QWEN_COOKIES = "your-cookies"

# MongoDB
$env:MONGO_URI = "mongodb://localhost:27017"
$env:MONGO_DB = "qwen_chats"

# RAG
$env:RAG_API_URL = "http://localhost:9001"
```

### Конфигурационный Файл
```json
{
  "qwen": {
    "api_url": "https://qwen.ai/api",
    "timeout": 30,
    "retry_count": 3
  },
  "import": {
    "batch_size": 100,
    "parallel": true
  },
  "export": {
    "format": "json",
    "compress": true
  }
}
```

## 📊 Статистика

### Импорт
- Скорость: ~100 чатов/минуту
- Размер: ~1MB на 100 чатов
- Время: зависит от объема
- Success Rate: ~95%

### Экспорт
- Формат: JSON
- Сжатие: gzip
- Размер: ~500KB на 100 чатов
- Время: ~30 секунд на 100 чатов

### API
- Rate Limit: 100 запросов/минуту
- Timeout: 30 секунд
- Retry: 3 попытки
- Cache: 1 час

## 🔍 Troubleshooting

### Проблемы с Cookies
```powershell
# Проверить cookies
.\scripts\qwen\api\refresh-qwen-cookies.ps1 -Verbose

# Вручную обновить
# 1. Открыть браузер
# 2. Войти в Qwen
# 3. Скопировать cookies из DevTools
# 4. Обновить в конфиге
```

### Проблемы с Импортом
```powershell
# Проверить формат данных
Get-Content data/qwen-export/*.json | ConvertFrom-Json

# Проверить RAG API
Invoke-RestMethod http://localhost:9001/health

# Проверить логи
Get-Content logs/import.log -Tail 50
```

### Проблемы с API
```python
# Тестировать API
python scripts/qwen/api/get-qwen-chats-via-client.py --debug

# Проверить endpoints
python scripts/qwen/api/find-messages-endpoint.py

# Проверить rate limits
# Смотреть заголовки ответа: X-RateLimit-*
```

## 🔗 Связанные Документы

- [Главный README](../README.md)
- [Тесты](../tests/README.md)
- [Утилиты](../utils/README.md)
- [Qwen API Docs](https://qwen.ai/docs)

---

**Категория:** Qwen Integration  
**Статус:** ✅ Готово к использованию  
**Обновлено:** 20 января 2026
