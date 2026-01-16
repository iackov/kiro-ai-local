# Architecture Modification Engine

## Обзор

Architecture Engine — это самомодифицирующийся компонент системы, который принимает natural-language промпты и автоматически изменяет архитектуру стека.

## Философия

Система рассматривает свою архитектуру как **данные**, которые можно модифицировать через рефлексивный, управляемый пользователем процесс. Это воплощение **embodied intelligence** — система рассуждает о своей собственной структуре.

## Возможности

### 1. Natural Language Parsing

Понимает промпты вида:
- "Add a reranker based on BGE-Reranker-v2-Mini"
- "Switch vector DB to Qdrant"
- "Remove Redis cache"
- "Scale RAG API to 3 replicas"

### 2. Idempotent Changes

Генерирует идемпотентные изменения:
- Docker Compose patches
- Config diffs
- Version snapshots

### 3. User Confirmation

По умолчанию требует подтверждения:
- Показывает diff перед применением
- Сохраняет версию для отката
- Применяет только после одобрения

### 4. Version History

Ведёт версионированную историю:
- Git-backed или Merkle-tree log
- Точка восстановления для каждого изменения
- Полный аудит всех модификаций

## API Endpoints

### POST /modify

Модифицировать архитектуру по natural language промпту.

**Request:**
```json
{
  "prompt": "Add a reranker service using BGE-Reranker-v2-Mini",
  "auto_apply": false
}
```

**Response:**
```json
{
  "success": true,
  "intent": "Add reranker service",
  "changes": [
    {
      "action": "add_service",
      "service_name": "reranker",
      "definition": { ... }
    }
  ],
  "diff": "# Architecture Changes\n+ Add service: reranker\n  Image: ghcr.io/huggingface/text-embeddings-inference:latest",
  "applied": false,
  "version_id": null
}
```

### GET /versions

Список всех версий архитектуры.

**Response:**
```json
{
  "versions": [
    {
      "id": "v-20260116-120000",
      "timestamp": "20260116-120000",
      "description": "Before: Add reranker",
      "created_at": "2026-01-16T12:00:00Z"
    }
  ]
}
```

### POST /rollback/{version_id}

Откатиться к конкретной версии.

**Response:**
```json
{
  "success": true,
  "version_id": "v-20260116-120000"
}
```

### GET /inspect

Инспектировать текущую архитектуру.

**Response:**
```json
{
  "services": [
    {
      "name": "ollama",
      "image": "ollama/ollama:latest",
      "ports": ["11434:11434"],
      "status": "defined"
    }
  ],
  "networks": ["ai-local-net"],
  "volumes": ["chroma-data", "ollama-data"]
}
```

## Использование

### Через API

```powershell
# Предложить изменение
curl -X POST http://localhost:8003/modify `
  -H "Content-Type: application/json" `
  -d '{"prompt": "Add Redis cache", "auto_apply": false}'

# Применить с подтверждением
curl -X POST http://localhost:8003/modify `
  -H "Content-Type: application/json" `
  -d '{"prompt": "Add Redis cache", "auto_apply": true}'

# Откатиться
curl -X POST http://localhost:8003/rollback/v-20260116-120000
```

### Через MCP (в Kiro)

```
@kiro используй arch_modify чтобы добавить reranker на основе BGE-Reranker-v2-Mini
```

## Поддерживаемые Интенты

### Add Service
- "Add a reranker service"
- "Create a cache proxy"
- "Deploy Qdrant vector database"

### Remove Service
- "Remove Redis"
- "Delete the cache service"
- "Stop MongoDB"

### Switch Component
- "Switch vector DB to Qdrant"
- "Use LanceDB instead of ChromaDB"
- "Replace Redis with Memcached"

### Scale Service
- "Scale RAG API to 3 replicas"
- "Increase Ollama to 2 instances"

## Безопасность

### Sandboxing
- Изменения ограничены workspace директорией
- Нет доступа к host системе вне `/workspace`
- Docker socket read-only

### Rollback Mechanism
- Автоматический snapshot перед каждым изменением
- Быстрый откат одной командой
- Сохранение всех предыдущих состояний

### Resource Limits
- CPU: 1 core
- Memory: 1GB
- Disk: ограничен workspace

## Auto-Apply Mode

По умолчанию **выключен** (требует подтверждения).

Включить через environment:
```yaml
environment:
  - AUTO_APPLY=true
```

Или через API:
```json
{
  "prompt": "Add Redis",
  "auto_apply": true
}
```

⚠️ **Внимание**: Auto-apply режим применяет изменения без подтверждения!

## Примеры Workflow

### 1. Добавить Reranker

```bash
# Шаг 1: Предложить изменение
curl -X POST http://localhost:8003/modify \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Add a reranker based on BGE-Reranker-v2-Mini"}'

# Шаг 2: Проверить diff
# (показывает что будет добавлено)

# Шаг 3: Применить
curl -X POST http://localhost:8003/modify \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Add a reranker based on BGE-Reranker-v2-Mini", "auto_apply": true}'

# Шаг 4: Перезапустить стек
docker compose up -d
```

### 2. Переключить Vector DB

```bash
# Переключиться с ChromaDB на Qdrant
curl -X POST http://localhost:8003/modify \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Switch vector DB to Qdrant in Docker", "auto_apply": true}'

# Перезапустить
docker compose down
docker compose up -d
```

### 3. Откатиться

```bash
# Список версий
curl http://localhost:8003/versions

# Откат
curl -X POST http://localhost:8003/rollback/v-20260116-120000

# Перезапустить
docker compose down
docker compose up -d
```

## Расширение

### Добавить новый компонент

Отредактируйте `arch_parser.py`:

```python
self.component_map = {
    "your-component": {
        "image": "your/image:latest",
        "port": 8080,
        "type": "custom"
    }
}
```

### Добавить новый интент

Добавьте pattern в `arch_parser.py`:

```python
self.patterns = {
    "your_intent": [
        r"your\s+regex\s+pattern"
    ]
}
```

## Ограничения

### Текущие
- Не поддерживает сложные зависимости между сервисами
- Не валидирует совместимость компонентов
- Не проверяет доступность ресурсов

### Будущие улучшения
- AI-powered intent parsing (через LLM)
- Автоматическая валидация изменений
- Предсказание влияния на производительность
- Интеграция с CI/CD

## Мониторинг

Логи доступны в:
```bash
docker logs ai-arch-engine
```

Метрики доступны на:
```
http://localhost:8003/metrics
```

## Troubleshooting

### Изменения не применяются

1. Проверьте права доступа к `docker-compose.yml`
2. Убедитесь что workspace path правильный
3. Проверьте логи: `docker logs ai-arch-engine`

### Откат не работает

1. Проверьте что версия существует: `curl http://localhost:8003/versions`
2. Убедитесь что `.arch-versions` директория доступна
3. Проверьте права доступа

### Intent не распознаётся

1. Проверьте поддерживаемые patterns в документации
2. Используйте более простую формулировку
3. Проверьте логи для confidence score

