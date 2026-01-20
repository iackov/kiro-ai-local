# Refresh Qwen Cookies Script
# Обновляет куки для Qwen MCP сервера

param(
    [Parameter(Mandatory=$false)]
    [string]$CookieString
)

$ErrorActionPreference = "Stop"

$configPath = "C:\Users\Jack\source\kiro\qwen\src\mcp_server\qwen_config.json"

Write-Host "=== Обновление Qwen Cookies ===" -ForegroundColor Cyan
Write-Host ""

# Проверка существования конфига
if (-not (Test-Path $configPath)) {
    Write-Host "Ошибка: Конфиг не найден: $configPath" -ForegroundColor Red
    exit 1
}

# Если куки не переданы, запросить у пользователя
if (-not $CookieString) {
    Write-Host "Как получить новые куки:" -ForegroundColor Yellow
    Write-Host "1. Откройте https://chat.qwen.ai в браузере" -ForegroundColor White
    Write-Host "2. Войдите в аккаунт" -ForegroundColor White
    Write-Host "3. Откройте DevTools (F12) -> Network" -ForegroundColor White
    Write-Host "4. Отправьте любое сообщение в чат" -ForegroundColor White
    Write-Host "5. Найдите запрос к /api/v2/chat/completions" -ForegroundColor White
    Write-Host "6. Скопируйте значение заголовка Cookie" -ForegroundColor White
    Write-Host ""
    
    $CookieString = Read-Host "Вставьте новую cookie строку"
    
    if (-not $CookieString) {
        Write-Host "Отменено" -ForegroundColor Yellow
        exit 0
    }
}

# Загрузить текущий конфиг
$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Обновить cookie_string
$config.cookies.cookie_string = $CookieString

# Сохранить обратно
$config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8

Write-Host ""
Write-Host "✓ Куки успешно обновлены!" -ForegroundColor Green
Write-Host ""
Write-Host "Теперь перезапустите MCP сервер в Kiro:" -ForegroundColor Yellow
Write-Host "  1. Откройте панель MCP в Kiro" -ForegroundColor White
Write-Host "  2. Найдите 'qwen-chat' сервер" -ForegroundColor White
Write-Host "  3. Нажмите кнопку переподключения" -ForegroundColor White
Write-Host ""
Write-Host "Или перезапустите Kiro IDE" -ForegroundColor White
Write-Host ""

# Показать первые/последние символы для проверки
$preview = $CookieString.Substring(0, [Math]::Min(50, $CookieString.Length)) + "..."
Write-Host "Сохранено: $preview" -ForegroundColor Gray
