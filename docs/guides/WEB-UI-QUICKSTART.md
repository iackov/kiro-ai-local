# 🚀 Web UI - Quick Start

## Открыть интерфейс

```
http://localhost:9000
```

---

## 🎯 Быстрые действия

### 1. Поиск в базе знаний
```
RAG Query → "Docker examples" → Search
```

### 2. Добавить сервис
```
Architecture Engine → "Add Postgres database" → Propose → Apply
```

### 3. Генерация кода
```
Qwen Generation → "Create Flask API" → Generate
```

### 4. Изменить ресурсы
```
Architecture Engine → "Change Redis memory to 4G" → Propose → Apply
```

---

## 📊 Разделы

| Раздел | Что делает | Кнопка |
|--------|-----------|--------|
| **System Status** | Статус сервисов | Авто-обновление |
| **RAG Query** | Поиск документов | Search |
| **Architecture Engine** | Изменение стека | Propose Change |
| **Qwen Generation** | Генерация текста | Generate |
| **RAG Statistics** | Статистика базы | Refresh Stats |
| **Architecture History** | История изменений | Refresh History |

---

## ⚡ Примеры команд

### RAG Query
```
Docker troubleshooting
Python Flask examples
Redis cache setup
MongoDB backup
Nginx configuration
```

### Architecture Engine
```
Add Postgres database service
Change Ollama memory to 16G
Remove MongoDB service
Change Redis port to 6380
Add volume /data/logs to RAG API
```

### Qwen Prompts
```
Explain Docker Compose
Create a Flask API with Redis
How to optimize Docker images?
Best practices for production deployment
```

---

## 🔧 Управление

```powershell
# Запустить
docker compose up -d web-ui

# Остановить
docker compose stop web-ui

# Логи
docker compose logs web-ui

# Перезапустить
docker compose restart web-ui
```

---

## ✅ Проверка

```powershell
# Статус
curl http://localhost:9000

# Все сервисы
docker compose ps
```

---

## 🎉 Готово!

**URL:** http://localhost:9000  
**Порт:** 9000  
**Контейнер:** ai-web-ui

**Начните с RAG Query или Architecture Engine!**
