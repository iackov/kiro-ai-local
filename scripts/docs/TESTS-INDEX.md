# 📋 Индекс Тестов

## ✅ Актуальные Тесты (Структурированные)

Все актуальные тесты перемещены в `scripts/tests/`:

### 📁 Unit Tests (`scripts/tests/unit/`)
- `test-tree-of-thought.py` - Tree-of-Thought Engine
- `test-self-modification.py` - Self-Modification Engine  
- `test-autonomous-optimizer.py` - Autonomous Optimizer
- `test-proactive-engine.py` - Proactive Engine
- `test-knowledge-store.py` - Knowledge Store

### 📁 Integration Tests (`scripts/tests/integration/`)
- `test-execution.py` - Автономное выполнение задач
- `test-improvements.py` - Model Router и кэширование
- `test-full-system.py` - Комплексный тест всей системы

### 📁 Verification Tests (`scripts/tests/verification/`)
- `verify-readme-claims.py` - Проверка всех 25 возможностей из README

### 🚀 Запуск
```bash
# Все тесты
python scripts/tests/run-all.py

# Только юнит-тесты
python scripts/tests/run-all.py --unit

# Только интеграционные
python scripts/tests/run-all.py --integration

# Только проверка возможностей
python scripts/tests/run-all.py --verification
```

## 📦 Устаревшие Тесты (Корень scripts/)

Эти файлы остаются для обратной совместимости, но рекомендуется использовать структурированные версии:

### Python Тесты
- `test-tree-of-thought.py` → `tests/unit/test-tree-of-thought.py`
- `test-self-modification.py` → `tests/unit/test-self-modification.py`
- `test-autonomous-optimizer.py` → `tests/unit/test-autonomous-optimizer.py`
- `test-proactive-engine.py` → `tests/unit/test-proactive-engine.py`
- `test-knowledge-store.py` → `tests/unit/test-knowledge-store.py`
- `test-execution.py` → `tests/integration/test-execution.py`
- `test-improvements.py` → `tests/integration/test-improvements.py`
- `test-full-system.py` → `tests/integration/test-full-system.py`
- `test-web-behavior.py` - Эмуляция веб-интерфейса (специфичный)
- `verify-readme-claims.py` → `tests/verification/verify-readme-claims.py`

### PowerShell Тесты (Демо-скрипты)
Эти скрипты используются для демонстрации возможностей:

#### Автономность
- `test-9-levels.ps1` - Тест 9 уровней автономности
- `test-final-autonomous.ps1` - Финальный тест автономности
- `test-full-autonomy.ps1` - Полная автономность
- `test-intelligence.ps1` - Тест интеллекта системы

#### Компоненты
- `test-adaptive-learning.ps1` - Адаптивное обучение
- `test-adaptive-planning.ps1` - Адаптивное планирование
- `test-arch-engine.ps1` - Architecture Engine
- `test-code-generation.ps1` - Генерация кода
- `test-decision-engine.ps1` - Decision Engine
- `test-improved-core.ps1` - Улучшенное ядро
- `test-loop-prevention.ps1` - Предотвращение циклов
- `test-predictive.ps1` - Предсказательные возможности
- `test-self-improvement.ps1` - Самоулучшение

#### Система
- `test-complete-system.ps1` - Полная система
- `test-new-model.ps1` - Новая модель
- `test-query.ps1` - Запросы
- `test-real-execution.ps1` - Реальное выполнение

#### Qwen Integration
- `test-qwen-api-direct.py` - Прямой доступ к Qwen API
- `test-qwen-history-search.ps1` - Поиск в истории Qwen
- `test-qwen-mcp.ps1` - Qwen через MCP
- `test-qwen-via-mcp.ps1` - Qwen через MCP (альтернатива)

## 🗑️ Можно Удалить

Следующие файлы дублируют функциональность и могут быть удалены после миграции:

```bash
# Python тесты (дублируются в tests/)
scripts/test-tree-of-thought.py
scripts/test-self-modification.py
scripts/test-autonomous-optimizer.py
scripts/test-proactive-engine.py
scripts/test-knowledge-store.py
scripts/test-execution.py
scripts/test-improvements.py
scripts/test-full-system.py
scripts/verify-readme-claims.py
```

## 📝 Рекомендации

1. **Используйте структурированные тесты** из `scripts/tests/`
2. **PowerShell тесты** оставьте для демонстраций
3. **Специфичные тесты** (test-web-behavior.py, test-qwen-*.py) оставьте в корне
4. **Удалите дубликаты** после проверки работоспособности

## 🔄 Миграция

Если вы используете старые тесты в CI/CD или скриптах:

```bash
# Старый способ
python scripts/test-tree-of-thought.py

# Новый способ
python scripts/tests/unit/test-tree-of-thought.py

# Или через раннер
python scripts/tests/run-all.py --unit
```
