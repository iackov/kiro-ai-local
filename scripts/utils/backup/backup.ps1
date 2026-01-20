# Backup Script
# Creates a backup of vector database and configurations

param(
    [string]$BackupDir = "backups"
)

$ErrorActionPreference = "Stop"

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupPath = "$BackupDir/$timestamp"

Write-Host "=== Creating Backup ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backup location: $backupPath" -ForegroundColor Yellow
Write-Host ""

# Create backup directory
New-Item -ItemType Directory -Path $backupPath -Force | Out-Null

# Backup configurations
Write-Host "[1/3] Backing up configurations..." -ForegroundColor Yellow
Copy-Item ".env" "$backupPath/.env" -ErrorAction SilentlyContinue
Copy-Item "docker-compose.yml" "$backupPath/docker-compose.yml"
Write-Host "  ✓ Configurations backed up" -ForegroundColor Green

# Backup ChromaDB data
Write-Host "[2/4] Backing up ChromaDB data..." -ForegroundColor Yellow
docker run --rm `
    -v ai-combiner_chroma-data:/data `
    -v "${PWD}/${backupPath}:/backup" `
    alpine tar czf /backup/chroma-data.tar.gz -C /data .
Write-Host "  ✓ ChromaDB data backed up" -ForegroundColor Green

# Backup MongoDB data
Write-Host "[3/4] Backing up MongoDB data..." -ForegroundColor Yellow
$mongoStatus = docker ps --filter "name=ai-mongodb" --format "{{.Status}}"
if ($mongoStatus -match "Up") {
    docker exec ai-mongodb mongodump `
        --db qwen_chats `
        --out /tmp/backup `
        --quiet 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        docker cp ai-mongodb:/tmp/backup "$backupPath/mongodb"
        docker exec ai-mongodb rm -rf /tmp/backup
        Write-Host "  ✓ MongoDB data backed up" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ MongoDB backup skipped (dump failed)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ MongoDB backup skipped (not running)" -ForegroundColor Yellow
}

# Backup logs
Write-Host "[4/4] Backing up logs..." -ForegroundColor Yellow
if (Test-Path "logs") {
    Copy-Item -Recurse "logs" "$backupPath/logs"
    Write-Host "  ✓ Logs backed up" -ForegroundColor Green
}

# Create manifest
$manifest = @{
    timestamp = $timestamp
    version = "1.0.0"
    components = @("chroma-data", "mongodb", "configurations", "logs")
} | ConvertTo-Json

$manifest | Set-Content "$backupPath/manifest.json"

Write-Host ""
Write-Host "=== Backup Complete ===" -ForegroundColor Green
Write-Host "Location: $backupPath" -ForegroundColor White
Write-Host ""
