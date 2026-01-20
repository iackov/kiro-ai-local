# Rollback Script
# Restores from a previous backup

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupPath
)

$ErrorActionPreference = "Stop"

Write-Host "=== Rollback ===" -ForegroundColor Cyan
Write-Host ""

# Validate backup
if (-not (Test-Path $BackupPath)) {
    Write-Host "Error: Backup not found: $BackupPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "$BackupPath/manifest.json")) {
    Write-Host "Error: Invalid backup (missing manifest)" -ForegroundColor Red
    exit 1
}

$manifest = Get-Content "$BackupPath/manifest.json" | ConvertFrom-Json
Write-Host "Backup timestamp: $($manifest.timestamp)" -ForegroundColor Yellow
Write-Host ""

# Confirm
$confirm = Read-Host "This will stop services and restore data. Continue? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Rollback cancelled" -ForegroundColor Yellow
    exit 0
}

# Stop services
Write-Host "[1/4] Stopping services..." -ForegroundColor Yellow
docker compose down
Write-Host "  ✓ Services stopped" -ForegroundColor Green

# Restore configurations
Write-Host "[2/4] Restoring configurations..." -ForegroundColor Yellow
if (Test-Path "$BackupPath/.env") {
    Copy-Item "$BackupPath/.env" ".env" -Force
}
Write-Host "  ✓ Configurations restored" -ForegroundColor Green

# Restore ChromaDB data
Write-Host "[3/4] Restoring ChromaDB data..." -ForegroundColor Yellow
docker volume rm ai-combiner_chroma-data -f
docker volume create ai-combiner_chroma-data
docker run --rm `
    -v ai-combiner_chroma-data:/data `
    -v "${PWD}/${BackupPath}:/backup" `
    alpine tar xzf /backup/chroma-data.tar.gz -C /data
Write-Host "  ✓ ChromaDB data restored" -ForegroundColor Green

# Restart services
Write-Host "[4/4] Restarting services..." -ForegroundColor Yellow
docker compose up -d
Write-Host "  ✓ Services restarted" -ForegroundColor Green

Write-Host ""
Write-Host "=== Rollback Complete ===" -ForegroundColor Green
Write-Host ""
