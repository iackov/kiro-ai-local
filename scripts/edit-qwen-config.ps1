# Quick Edit Qwen Config
# Открывает qwen_config.json в редакторе

$configPath = "C:\Users\Jack\source\kiro\qwen\src\mcp_server\qwen_config.json"

Write-Host "Открытие конфига Qwen..." -ForegroundColor Cyan
Write-Host "Путь: $configPath" -ForegroundColor Yellow
Write-Host ""

if (Test-Path $configPath) {
    # Открыть в дефолтном редакторе
    Start-Process $configPath
    
    Write-Host "Что нужно обновить:" -ForegroundColor Yellow
    Write-Host "  1. cookies.cookie_string - новые куки из браузера" -ForegroundColor White
    Write-Host "  2. mongo.uri - если MongoDB на другом хосте" -ForegroundColor White
    Write-Host ""
    Write-Host "После изменений перезапустите MCP в Kiro" -ForegroundColor Green
} else {
    Write-Host "Ошибка: Файл не найден!" -ForegroundColor Red
    Write-Host "Путь: $configPath" -ForegroundColor Gray
}
