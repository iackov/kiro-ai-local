# Setup Qwen MongoDB Connection
# Updates Qwen config to use local MongoDB

$ErrorActionPreference = "Stop"

$configPath = "C:\Users\Jack\source\kiro\qwen\src\mcp_server\qwen_config.json"

Write-Host "=== Qwen + MongoDB Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check config exists
if (-not (Test-Path $configPath)) {
    Write-Host "Error: Qwen config not found: $configPath" -ForegroundColor Red
    exit 1
}

# Check MongoDB is running
Write-Host "Checking MongoDB..." -ForegroundColor Yellow
try {
    $mongoTest = docker ps --filter "name=ai-mongodb" --format "{{.Status}}"
    if ($mongoTest -match "Up") {
        Write-Host "  OK MongoDB is running" -ForegroundColor Green
    } else {
        Write-Host "  ERROR MongoDB is not running" -ForegroundColor Red
        Write-Host "  Run: docker compose up -d mongodb" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "  ERROR checking MongoDB" -ForegroundColor Red
    exit 1
}

# Load current config
$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Update MongoDB settings
$config.mongo.uri = "mongodb://localhost:27017"
$config.mongo.database = "qwen_chats"
$config.mongo.collections = @{
    chats = "chats"
    messages = "messages"
}

# Save back
$config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8

Write-Host ""
Write-Host "OK Configuration updated!" -ForegroundColor Green
Write-Host ""
Write-Host "MongoDB settings:" -ForegroundColor Yellow
Write-Host "  URI: mongodb://localhost:27017" -ForegroundColor White
Write-Host "  Database: qwen_chats" -ForegroundColor White
Write-Host "  Collections: chats, messages" -ForegroundColor White
Write-Host ""
Write-Host "Qwen chat history will now be saved to MongoDB" -ForegroundColor Green
Write-Host ""
Write-Host "Restart MCP server in Kiro to apply changes" -ForegroundColor Yellow
Write-Host ""

# Check MongoDB connection
Write-Host "Checking MongoDB connection..." -ForegroundColor Yellow
try {
    docker exec ai-mongodb mongosh --quiet --eval "db.version()" qwen_chats | Out-Null
    Write-Host "  OK Connection successful" -ForegroundColor Green
} catch {
    Write-Host "  WARNING Could not verify connection (normal if mongosh not installed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
