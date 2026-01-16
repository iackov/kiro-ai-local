# Важные пути в системе

## Конфигурация Qwen MCP

**Основной конфиг** (куки, MongoDB, модели):
```
C:\Users\Jack\source\kiro\qwen\src\mcp_server\qwen_config.json
```

**Python скрипт MCP сервера**:
```
C:\Users\Jack\source\kiro\qwen\src\mcp_server\qwen_mcp_server.py
```

**Клиент Qwen API**:
```
C:\Users\Jack\source\kiro\qwen\src\mcp_server\qwen_client.py
```

## Конфигурация Kiro

**MCP серверы** (глобальная конфигурация):
```
C:\Users\Jack\.kiro\settings\mcp.json
```

**MCP серверы** (workspace конфигурация):
```
.kiro\settings\mcp.json
```

## AI Combiner Stack (текущий проект)

**Docker Compose**:
```
C:\Users\Jack\source\kiro-ai-local\docker-compose.yml
```

**Environment переменные**:
```
C:\Users\Jack\source\kiro-ai-local\.env
```

**Скрипты**:
```
C:\Users\Jack\source\kiro-ai-local\scripts\
```

## Быстрые команды

### Открыть конфиг Qwen
```powershell
.\scripts\edit-qwen-config.ps1
```
или
```powershell
notepad "C:\Users\Jack\source\kiro\qwen\src\mcp_server\qwen_config.json"
```

### Открыть MCP конфиг Kiro
```powershell
notepad "$env:USERPROFILE\.kiro\settings\mcp.json"
```

### Обновить куки Qwen
```powershell
.\scripts\refresh-qwen-cookies.ps1
```

### Настроить MongoDB для Qwen
```powershell
.\scripts\setup-qwen-mongo.ps1
```

## Структура qwen_config.json

```json
{
  "cookies": {
    "cookie_string": "ЗДЕСЬ_ВАШИ_КУКИ"
  },
  "headers": { ... },
  "api_endpoints": {
    "base_url": "https://chat.qwen.ai",
    ...
  },
  "models": {
    "default": "qwen3-coder-plus",
    ...
  },
  "mongo": {
    "uri": "mongodb://localhost:27017",
    "database": "qwen_chats",
    ...
  }
}
```

## Что обновлять

### Протухли куки
Обновите `cookies.cookie_string` в `qwen_config.json`

### Изменить модель по умолчанию
Обновите `models.default` в `qwen_config.json`

### Подключить MongoDB
Обновите `mongo.uri` в `qwen_config.json` или запустите:
```powershell
.\scripts\setup-qwen-mongo.ps1
```

### Добавить/удалить MCP сервер
Редактируйте `~/.kiro/settings/mcp.json`
