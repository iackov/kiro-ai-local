# MongoDB Backup & Restore

## Обзор

MongoDB используется для хранения истории чатов Qwen. Регулярные бэкапы важны для сохранения данных.

## Автоматический Backup

### Через основной скрипт

```powershell
.\scripts\backup.ps1
```

Это создаст бэкап:
- ChromaDB данных
- Конфигурационных файлов
- Логов
- **MongoDB данных** (если MongoDB запущена)

### Только MongoDB

```powershell
.\scripts\backup-mongodb.ps1
```

## Ручной Backup

### Экспорт всей базы данных

```powershell
# Создать директорию для бэкапа
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupPath = "backups/mongodb-$timestamp"
New-Item -ItemType Directory -Path $backupPath -Force

# Экспорт через mongodump
docker exec ai-mongodb mongodump `
  --db qwen_chats `
  --out /tmp/backup

# Копировать из контейнера
docker cp ai-mongodb:/tmp/backup "$backupPath/"
```

### Экспорт конкретной коллекции

```powershell
# Экспорт только чатов
docker exec ai-mongodb mongoexport `
  --db qwen_chats `
  --collection chats `
  --out /tmp/chats.json

docker cp ai-mongodb:/tmp/chats.json "backups/chats-$timestamp.json"

# Экспорт только сообщений
docker exec ai-mongodb mongoexport `
  --db qwen_chats `
  --collection messages `
  --out /tmp/messages.json

docker cp ai-mongodb:/tmp/messages.json "backups/messages-$timestamp.json"
```

## Restore

### Полное восстановление

```powershell
# Остановить MongoDB
docker compose stop mongodb

# Восстановить из бэкапа
docker compose start mongodb

# Подождать запуска
Start-Sleep -Seconds 5

# Копировать бэкап в контейнер
docker cp "backups/mongodb-20260116-120000/backup" ai-mongodb:/tmp/

# Восстановить
docker exec ai-mongodb mongorestore `
  --db qwen_chats `
  /tmp/backup/qwen_chats
```

### Восстановление конкретной коллекции

```powershell
# Копировать JSON в контейнер
docker cp "backups/chats-20260116-120000.json" ai-mongodb:/tmp/chats.json

# Импортировать
docker exec ai-mongodb mongoimport `
  --db qwen_chats `
  --collection chats `
  --file /tmp/chats.json
```

### Через основной скрипт rollback

```powershell
.\scripts\rollback.ps1 -BackupPath "backups/20260116-120000"
```

Это восстановит:
- Конфигурации
- ChromaDB данные
- MongoDB данные (если есть в бэкапе)

## Автоматизация

### Scheduled Task (Windows)

Создать задачу для ежедневного бэкапа:

```powershell
# Создать скрипт задачи
$scriptPath = "$PWD\scripts\backup.ps1"
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
  -Argument "-File `"$scriptPath`""

$trigger = New-ScheduledTaskTrigger -Daily -At 3am

Register-ScheduledTask -TaskName "AI-Combiner-Backup" `
  -Action $action `
  -Trigger $trigger `
  -Description "Daily backup of AI Combiner stack"
```

### Через Docker (cron)

Добавить в `docker-compose.yml`:

```yaml
services:
  backup-scheduler:
    image: alpine:latest
    container_name: ai-backup-scheduler
    volumes:
      - mongo-data:/data/mongo:ro
      - ./backups:/backups
    command: sh -c "while true; do mongodump --host mongodb --db qwen_chats --out /backups/auto-$(date +%Y%m%d-%H%M%S); sleep 86400; done"
    depends_on:
      - mongodb
    restart: unless-stopped
```

## Проверка Backup

### Проверить размер

```powershell
# Размер MongoDB данных
docker exec ai-mongodb du -sh /data/db

# Размер бэкапа
Get-ChildItem -Recurse "backups/mongodb-20260116-120000" | 
  Measure-Object -Property Length -Sum | 
  Select-Object @{Name="Size(MB)";Expression={[math]::Round($_.Sum/1MB,2)}}
```

### Проверить содержимое

```powershell
# Список коллекций в бэкапе
docker exec ai-mongodb ls -la /tmp/backup/qwen_chats/

# Количество документов
docker exec ai-mongodb mongosh qwen_chats --quiet --eval "
  print('Chats: ' + db.chats.countDocuments());
  print('Messages: ' + db.messages.countDocuments());
"
```

## Retention Policy

### Рекомендуемая стратегия

- **Ежедневные**: Хранить 7 дней
- **Еженедельные**: Хранить 4 недели
- **Ежемесячные**: Хранить 12 месяцев

### Скрипт очистки старых бэкапов

```powershell
# Удалить бэкапы старше 7 дней
$retentionDays = 7
$cutoffDate = (Get-Date).AddDays(-$retentionDays)

Get-ChildItem "backups" -Directory | 
  Where-Object { $_.CreationTime -lt $cutoffDate } |
  Remove-Item -Recurse -Force

Write-Host "Cleaned up backups older than $retentionDays days"
```

## Миграция

### Экспорт для миграции на другой сервер

```powershell
# Полный экспорт с метаданными
docker exec ai-mongodb mongodump `
  --db qwen_chats `
  --archive=/tmp/qwen_chats.archive `
  --gzip

docker cp ai-mongodb:/tmp/qwen_chats.archive "qwen_chats_export.archive.gz"
```

### Импорт на новом сервере

```powershell
# Копировать архив в новый контейнер
docker cp "qwen_chats_export.archive.gz" ai-mongodb:/tmp/

# Импортировать
docker exec ai-mongodb mongorestore `
  --archive=/tmp/qwen_chats_export.archive.gz `
  --gzip
```

## Мониторинг

### Размер базы данных

```powershell
docker exec ai-mongodb mongosh qwen_chats --quiet --eval "
  db.stats().dataSize / 1024 / 1024
"
```

### Последний бэкап

```powershell
Get-ChildItem "backups" -Directory | 
  Sort-Object CreationTime -Descending | 
  Select-Object -First 1 Name, CreationTime
```

## Troubleshooting

### Бэкап не создаётся

1. Проверьте что MongoDB запущена:
   ```powershell
   docker ps | findstr mongodb
   ```

2. Проверьте права доступа к директории backups:
   ```powershell
   Test-Path "backups" -PathType Container
   ```

3. Проверьте место на диске:
   ```powershell
   Get-PSDrive C | Select-Object Used,Free
   ```

### Restore не работает

1. Убедитесь что MongoDB остановлена перед restore
2. Проверьте формат бэкапа (mongodump vs mongoexport)
3. Проверьте логи:
   ```powershell
   docker logs ai-mongodb
   ```

### Бэкап слишком большой

1. Очистите старые чаты:
   ```powershell
   docker exec ai-mongodb mongosh qwen_chats --eval "
     db.messages.deleteMany({
       timestamp: { $lt: new Date(Date.now() - 30*24*60*60*1000) }
     })
   "
   ```

2. Используйте сжатие:
   ```powershell
   docker exec ai-mongodb mongodump --gzip --db qwen_chats
   ```

## Безопасность

### Шифрование бэкапов

```powershell
# Создать зашифрованный бэкап
$password = Read-Host -AsSecureString "Enter backup password"
$backupFile = "backups/mongodb-encrypted-$(Get-Date -Format 'yyyyMMdd-HHmmss').zip"

# Создать бэкап
docker exec ai-mongodb mongodump --db qwen_chats --archive=/tmp/backup.archive

# Копировать и зашифровать
docker cp ai-mongodb:/tmp/backup.archive - | 
  7z a -si -p$password -mhe=on $backupFile
```

### Хранение в облаке

```powershell
# Загрузить в S3 (если настроен AWS CLI)
aws s3 cp "backups/mongodb-20260116-120000.archive.gz" `
  s3://your-bucket/ai-combiner-backups/

# Или в Azure Blob Storage
az storage blob upload `
  --account-name youraccount `
  --container-name backups `
  --file "backups/mongodb-20260116-120000.archive.gz"
```

