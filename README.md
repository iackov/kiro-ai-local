# AI Combiner Stack - Full Autonomy System

**Полностью автономная AI-система с 6 уровнями автономности**

Локальная AI-инфраструктура с RAG, Architecture Engine, Self-Monitoring, Adaptive Learning и Auto-Healing.

---

## 🎯 Что Это?

AI Combiner Stack - это самоуправляемая AI-система, которая:
- **Находит информацию** в 19,000+ документов (RAG)
- **Координирует сервисы** (Multi-Service Orchestration)
- **Модифицирует себя** безопасно (Architecture Engine)
- **Мониторит себя** и предлагает улучшения (Self-Monitoring)
- **Учится** на ваших предпочтениях (Adaptive Learning)
- **Восстанавливается** автоматически при сбоях (Auto-Healing)

**Статус:** ✅ Production Ready | Health: 100/100 | All 6 Levels Active

---

## 🚀 Быстрый Старт

```powershell
# 1. Запустить все сервисы
docker compose up -d

# 2. Проверить статус (включая все 6 уровней)
.\scripts\full-system-check.ps1

# 3. Открыть Web UI
start http://localhost:9000
```

**Результат:** Все 6 уровней автономности активны, система готова к работе.

---

## 📦 Сервисы

| Сервис | Порт | Статус | Описание |
|--------|------|--------|----------|
| **Web UI** | 9000 | ✅ | Веб-интерфейс (все 6 уровней) |
| **RAG API** | 9001 | ✅ | ChromaDB + семантический поиск |
| **MCP Gateway** | 9002 | ✅ | Интеграция с Kiro IDE |
| **Arch Engine** | 9004 | ✅ | Управление архитектурой |
| **Ollama** | 11434 | ✅ | LLM (qwen2.5-coder:7b) |
| **MongoDB** | 27017 | ✅ | База данных чатов |
| **Redis** | 6379 | ✅ | Кэширование |

**Метрики:** 19,103 документов | Health: 100/100 | Latency: ~700ms

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kiro IDE (MCP Client)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │ MCP Protocol
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Web UI (Port 9000)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Level 1: Basic RAG          │ Level 4: Self-Monitoring   │  │
│  │ Level 2: Multi-Service      │ Level 5: Adaptive Learning │  │
│  │ Level 3: Architecture Engine│ Level 6: Auto-Healing      │  │
│  └──────────────────────────────────────────────────────────┘  │
└───┬─────────────┬─────────────┬─────────────┬──────────────────┘
    │             │             │             │
    ▼             ▼             ▼             ▼
┌─────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐
│ RAG API │ │   MCP    │ │   Arch   │ │   Ollama    │
│  :9001  │ │ Gateway  │ │  Engine  │ │   :11434    │
│         │ │  :9002   │ │  :9004   │ │             │
└────┬────┘ └──────────┘ └────┬─────┘ └─────────────┘
     │                         │
     ▼                         ▼
┌──────────┐           ┌──────────────┐
│ ChromaDB │           │ docker-      │
│ 19K docs │           │ compose.yml  │
└──────────┘           └──────────────┘
```

---

## 🎓 6 Уровней Автономности

### Level 1: Basic RAG
Семантический поиск по документам
```powershell
$body = @{ query = "docker compose"; top_k = 3 }
Invoke-RestMethod -Uri "http://localhost:9000/api/rag/query" -Method Post -Body $body
```

### Level 2: Multi-Service Orchestration
Координация RAG + Architecture Engine
```powershell
$body = @{ query = "add redis service"; top_k = 3 }
Invoke-RestMethod -Uri "http://localhost:9000/api/combined/query" -Method Post -Body $body
```

### Level 3: Architecture Engine
Безопасная модификация docker-compose.yml
```powershell
$body = @{ prompt = "Add nginx with 512M memory"; auto_apply = $false }
$proposal = Invoke-RestMethod -Uri "http://localhost:9000/api/arch/propose" -Method Post -Body $body
```

### Level 4: Self-Monitoring
Анализ производительности и предложения
```powershell
$metrics = Invoke-RestMethod -Uri "http://localhost:9000/api/metrics/insights"
Write-Host "Health: $($metrics.health_score)/100"
```

### Level 5: Adaptive Learning
Обучение на предпочтениях пользователя
```powershell
$body = @{ suggestion_id = "add_redis"; action = "applied" }
Invoke-RestMethod -Uri "http://localhost:9000/api/learning/feedback" -Method Post -Body $body
```

### Level 6: Auto-Healing
Автоматическое восстановление при сбоях
```powershell
$opps = Invoke-RestMethod -Uri "http://localhost:9000/api/auto/opportunities"
# Система автоматически исправит проблемы
```

---

## 📚 Документация

### Основное
- **[CURRENT-STATUS.md](CURRENT-STATUS.md)** - Полный статус и возможности системы
- [QUICKSTART.md](QUICKSTART.md) - Подробное руководство по запуску
- [WEB-UI-GUIDE.md](docs/WEB-UI-GUIDE.md) - Руководство по Web UI
- [WEB-UI-QUICKSTART.md](docs/WEB-UI-QUICKSTART.md) - Быстрый старт Web UI

### Интеграции
- [IMPORT-QWEN-CHATS-INSTRUCTIONS.md](IMPORT-QWEN-CHATS-INSTRUCTIONS.md) - Импорт чатов Qwen
- [GET-FRESH-COOKIES.md](GET-FRESH-COOKIES.md) - Обновление cookies для Qwen API
- [HOW-TO-CHECK-QWEN-IN-KIRO.md](HOW-TO-CHECK-QWEN-IN-KIRO.md) - Проверка интеграции с Kiro

### Тестирование
```powershell
.\scripts\full-system-check.ps1      # Полная проверка (22 теста)
.\scripts\test-full-autonomy.ps1     # Тест всех 6 уровней
.\scripts\stress-test.ps1            # Нагрузочное тестирование
.\scripts\demo-autonomy.ps1          # Демонстрация возможностей
```

---

## 🔧 Управление

### Запуск/Остановка
```powershell
docker compose up -d              # Запустить все
docker compose down               # Остановить все
docker compose restart web-ui     # Перезапустить сервис
docker logs ai-web-ui --tail 50   # Посмотреть логи
```

### Обновление
```powershell
docker compose build web-ui       # Пересобрать после изменений
docker compose up -d web-ui       # Применить изменения
```

---

## 📊 Текущий Статус

```
✅ Full System Check: 22/22 passed (100%)
✅ Autonomy Levels: 6/6 active
✅ Stress Test: 20/20 requests successful
✅ Health Score: 100/100
✅ Documents: 19,103
✅ Uptime: Stable
```

**Система полностью готова к использованию.**

---

## 🎯 Что Дальше?

Возможные направления развития:
1. UI улучшения - графики метрик, визуализация архитектуры
2. Больше auto-actions - автоматическое масштабирование
3. Advanced learning - ML-модели для предсказания проблем
4. Multi-stack support - управление несколькими compose файлами
5. Cloud integration - деплой в облако одной командой

---

## 📞 Поддержка

- **Проверка здоровья:** `.\scripts\full-system-check.ps1`
- **Логи:** `docker logs <container-name>`
- **Документация:** См. [CURRENT-STATUS.md](CURRENT-STATUS.md)

---

**License:** MIT  
**Status:** ✅ Production Ready - Full Autonomy Achieved
