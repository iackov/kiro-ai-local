# Discover Qwen API endpoints
# Пробуем найти endpoint для получения списка чатов

$ErrorActionPreference = "Continue"

Write-Host "=== Discovering Qwen API Endpoints ===" -ForegroundColor Cyan
Write-Host ""

# Читаем куки из конфига
$configPath = "C:\Users\Jack\source\kiro\qwen\src\mcp_server\qwen_config.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json
$cookie = $config.cookies.cookie_string

Write-Host "Cookie loaded: $($cookie.Length) chars" -ForegroundColor Green
Write-Host ""

# Базовый URL
$baseUrl = "https://chat.qwen.ai"

# Заголовки (как в qwen_client.py, но без Connection)
$headers = @{
    "Cookie" = $cookie
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    "Accept" = "text/event-stream, application/json, text/plain, */*"
    "Accept-Language" = "ru-RU,ru;q=0.9,en;q=0.8"
    "Cache-Control" = "no-cache"
    "Origin" = "https://chat.qwen.ai"
    "Referer" = "https://chat.qwen.ai/"
}

# Пробуем разные endpoints для получения списка чатов
$endpoints = @(
    "/api/v2/chats",
    "/api/v2/chats/list",
    "/api/v2/user/chats",
    "/api/chats",
    "/api/conversations",
    "/api/v2/conversations",
    "/api/v2/history",
    "/api/history"
)

Write-Host "Testing endpoints..." -ForegroundColor Yellow
Write-Host ""

foreach ($endpoint in $endpoints) {
    $url = "$baseUrl$endpoint"
    Write-Host "Testing: $endpoint" -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get -TimeoutSec 10
        Write-Host "  SUCCESS! Found endpoint: $endpoint" -ForegroundColor Green
        Write-Host "  Response:" -ForegroundColor White
        $response | ConvertTo-Json -Depth 3 | Write-Host
        Write-Host ""
        break
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode) {
            Write-Host "  $statusCode - $($_.Exception.Message)" -ForegroundColor Red
        } else {
            Write-Host "  Failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=== Alternative: Check browser DevTools ===" -ForegroundColor Yellow
Write-Host ""
Write-Host "To find the correct endpoint:" -ForegroundColor White
Write-Host "1. Open https://chat.qwen.ai in browser" -ForegroundColor Gray
Write-Host "2. Open DevTools (F12) -> Network tab" -ForegroundColor Gray
Write-Host "3. Refresh the page or navigate to chat history" -ForegroundColor Gray
Write-Host "4. Look for API calls that return chat list" -ForegroundColor Gray
Write-Host "5. Copy the endpoint URL" -ForegroundColor Gray
Write-Host ""
