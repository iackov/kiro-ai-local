# Refresh Qwen Authentication
# Updates Qwen API credentials in the environment

param(
    [Parameter(Mandatory=$false)]
    [string]$ApiKey,
    
    [Parameter(Mandatory=$false)]
    [string]$Cookie
)

$ErrorActionPreference = "Stop"

Write-Host "=== Qwen Authentication Refresh ===" -ForegroundColor Cyan
Write-Host ""

# Load current .env
$envPath = ".env"
if (-not (Test-Path $envPath)) {
    Write-Host "Error: .env file not found" -ForegroundColor Red
    exit 1
}

$envContent = Get-Content $envPath

# Prompt for credentials if not provided
if (-not $ApiKey) {
    $ApiKey = Read-Host "Enter Qwen API Key (or press Enter to skip)"
}

if (-not $Cookie) {
    $Cookie = Read-Host "Enter Qwen Cookie (or press Enter to skip)"
}

# Update .env file
$updated = $false

if ($ApiKey) {
    $envContent = $envContent -replace "QWEN_API_KEY=.*", "QWEN_API_KEY=$ApiKey"
    Write-Host "✓ Updated API Key" -ForegroundColor Green
    $updated = $true
}

if ($Cookie) {
    $envContent = $envContent -replace "QWEN_COOKIE=.*", "QWEN_COOKIE=$Cookie"
    Write-Host "✓ Updated Cookie" -ForegroundColor Green
    $updated = $true
}

if ($updated) {
    $envContent | Set-Content $envPath
    Write-Host ""
    Write-Host "Credentials updated in .env" -ForegroundColor Green
    Write-Host ""
    Write-Host "Restart services to apply changes:" -ForegroundColor Yellow
    Write-Host "  docker compose restart" -ForegroundColor White
} else {
    Write-Host "No credentials provided, nothing updated" -ForegroundColor Yellow
}
