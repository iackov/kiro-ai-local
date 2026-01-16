# Инструкция: Импорт диалогов Qwen в RAG

## Проблема
Текущие куки Qwen протухли (401 Unauthorized). Нужно обновить их перед импортом.

## Решение

### Шаг 1: Обновите куки Qwen

```powershell
.\scripts\refresh-qwen-cookies.ps1
```

**Как получить свежие куки:**
1. Откройте https://chat.qwen.ai в браузере
2. Войдите в аккаунт (если не вошли)
3. Откройте DevTools (F12) → вкладка Network
4. Обновите страницу (F5)
5. Найдите любой запрос к `chat.qwen.ai`
6. Во вкладке Headers найдите `Cookie`
7. Скопируйте **ВСЁ** значение Cookie
8. Вставьте в скрипт когда попросит

### Шаг 2: Запустите импорт

```powershell
.\scripts\import-qwen-chats-to-rag.ps1
```

## Что делает скрипт

### 1. Проверяет куки
- Читает `qwen_config.json`
- Проверяет что куки не пустые

### 2. Получает список чатов
- API: `GET https://chat.qwen.ai/api/v2/chats`
- Возвращает все ваши чаты с Qwen

### 3. Получает сообщения каждого чата
- API: `GET https://chat.qwen.ai/api/v2/chats/{chat_id}/messages`
- Для каждого чата получает все сообщения

### 4. Сохраняет в файлы
- Создаёт `data/qwen-chats/chat-{id}.md`
- Формат:
  ```markdown
  # Chat: Название чата
  Date: 2026-01-16
  Model: qwen3-coder-plus
  
  ## User
  Вопрос пользователя
  
  ## Assistant
  Ответ Qwen
  ```

### 5. Загружает в RAG
- POST `http://localhost:9001/ingest`
- Разбивает на чанки
- Создаёт embeddings
- Сохраняет в ChromaDB

## После импорта

### Поиск по истории чатов:

```powershell
# Через API
$body = '{"query": "как работает RAG?", "top_k": 5}'
Invoke-RestMethod -Uri "http://localhost:9001/query" -Method Post -Body $body -ContentType "application/json"

# Через MCP Gateway
$body = '{"query": "что я спрашивал про Python?", "top_k": 3}'
Invoke-RestMethod -Uri "http://localhost:9002/query" -Method Post -Body $body -ContentType "application/json"
```

### В Kiro IDE:

```
@kiro используй rag_query чтобы найти что я обсуждал с Qwen про архитектуру
```

## Troubleshooting

### Ошибка: 401 Unauthorized
**Причина**: Куки протухли

**Решение**:
```powershell
.\scripts\refresh-qwen-cookies.ps1
```

### Ошибка: RAG API unreachable
**Причина**: RAG API не запущен

**Решение**:
```powershell
docker ps | findstr rag-api
# Если не запущен:
docker compose up -d rag-api
```

### Ошибка: No chats found
**Причина**: У вас нет чатов в Qwen или API изменился

**Решение**:
1. Проверьте что у вас есть чаты на https://chat.qwen.ai
2. Проверьте endpoint в DevTools браузера

### Ошибка: Failed to fetch messages
**Причина**: API endpoint для сообщений может отличаться

**Решение**:
1. Откройте https://chat.qwen.ai
2. Откройте любой чат
3. В DevTools → Network найдите запрос который загружает сообщения
4. Обновите endpoint в скрипте

## Альтернативный способ (если API не работает)

### Экспорт из MongoDB (если уже есть история):

```powershell
# Экспорт чатов из MongoDB
docker exec ai-mongodb mongoexport --db qwen_chats --collection chats --out /tmp/chats.json
docker cp ai-mongodb:/tmp/chats.json data/qwen-chats/

# Экспорт сообщений
docker exec ai-mongodb mongoexport --db qwen_chats --collection messages --out /tmp/messages.json
docker cp ai-mongodb:/tmp/messages.json data/qwen-chats/

# Конвертировать в markdown и загрузить в RAG
# (нужен отдельный скрипт для конвертации JSON → Markdown)
```

## Примечания

### Ограничения API:
- Qwen API может иметь rate limits
- Большое количество чатов может занять время
- Некоторые старые чаты могут быть недоступны

### Размер данных:
- Каждый чат = 1 файл
- Средний размер: 5-50 KB на чат
- 100 чатов ≈ 1-5 MB данных

### Производительность:
- Импорт 100 чатов: ~2-5 минут
- Зависит от количества сообщений
- Зависит от скорости сети

## Что дальше?

После импорта вы сможете:
1. ✅ Искать по всей истории чатов с Qwen
2. ✅ Находить старые обсуждения
3. ✅ Использовать контекст из прошлых разговоров
4. ✅ Комбинировать с новыми запросами к Qwen

**Ваша история чатов станет частью RAG базы знаний!**
