# MongoDB Backup Script
# Creates a backup of MongoDB data

param(
    [string]$BackupDir = "backups"
)

$ErrorActionPreference = "Stop"

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupPath = "$BackupDir/mongodb-$timestamp"

Write-Host "=== MongoDB Backup ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backup location: $backupPath" -ForegroundColor Yellow
Write-Host ""

# Check MongoDB is running
Write-Host "[1/3] Checking MongoDB status..." -ForegroundColor Yellow
$mongoStatus = docker ps --filter "name=ai-mongodb" --format "{{.Status}}"
if (-not ($mongoStatus -match "Up")) {
    Write-Host "  ✗ MongoDB is not running" -ForegroundColor Red
    Write-Host "  Start it with: docker compose up -d mongodb" -ForegroundColor Yellow
    exit 1
}
Write-Host "  ✓ MongoDB is running" -ForegroundColor Green

# Create backup directory
New-Item -ItemType Directory -Path $backupPath -Force | Out-Null

# Backup MongoDB data
Write-Host "[2/3] Creating MongoDB dump..." -ForegroundColor Yellow
docker exec ai-mongodb mongodump `
    --db qwen_chats `
    --out /tmp/backup `
    --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ MongoDB dump failed" -ForegroundColor Red
    exit 1
}

# Copy from container
docker cp ai-mongodb:/tmp/backup "$backupPath/"
Write-Host "  ✓ MongoDB data backed up" -ForegroundColor Green

# Create manifest
Write-Host "[3/3] Creating manifest..." -ForegroundColor Yellow
$manifest = @{
    timestamp = $timestamp
    type = "mongodb"
    database = "qwen_chats"
    created_at = (Get-Date).ToString("o")
} | ConvertTo-Json

$manifest | Set-Content "$backupPath/manifest.json"
Write-Host "  ✓ Manifest created" -ForegroundColor Green

# Get stats
$stats = docker exec ai-mongodb mongosh qwen_chats --quiet --eval "
    JSON.stringify({
        chats: db.chats.countDocuments(),
        messages: db.messages.countDocuments()
    })
" | ConvertFrom-Json

Write-Host ""
Write-Host "=== Backup Complete ===" -ForegroundColor Green
Write-Host "Location: $backupPath" -ForegroundColor White
Write-Host "Chats: $($stats.chats)" -ForegroundColor White
Write-Host "Messages: $($stats.messages)" -ForegroundColor White
Write-Host ""

# Cleanup temp files in container
docker exec ai-mongodb rm -rf /tmp/backup

