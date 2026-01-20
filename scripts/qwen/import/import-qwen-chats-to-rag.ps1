# Import Qwen Chats to RAG
# Загружает все диалоги из Qwen в RAG систему

param(
    [switch]$RefreshCookies = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== Import Qwen Chats to RAG ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check cookies
Write-Host "[1/5] Checking Qwen cookies..." -ForegroundColor Yellow
$configPath = "C:\Users\Jack\source\kiro\qwen\src\mcp_server\qwen_config.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json
$cookie = $config.cookies.cookie_string

if ($cookie.Length -lt 100) {
    Write-Host "  ERROR: Cookie too short or missing" -ForegroundColor Red
    Write-Host "  Run: .\scripts\refresh-qwen-cookies.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "  OK Cookie loaded: $($cookie.Length) chars" -ForegroundColor Green
Write-Host ""

# Step 2: Get chats list from Qwen API
Write-Host "[2/5] Fetching chats from Qwen API..." -ForegroundColor Yellow

$headers = @{
    "Cookie" = $cookie
    "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    "Accept" = "application/json"
    "Origin" = "https://chat.qwen.ai"
    "Referer" = "https://chat.qwen.ai/"
}

try {
    $chatsResponse = Invoke-RestMethod -Uri "https://chat.qwen.ai/api/v2/chats/list" -Headers $headers -Method Get -TimeoutSec 30
    
    if (-not $chatsResponse.success) {
        Write-Host "  ERROR: $($chatsResponse.data.code) - $($chatsResponse.data.details)" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Cookies may be expired. To refresh:" -ForegroundColor Yellow
        Write-Host "  .\scripts\refresh-qwen-cookies.ps1" -ForegroundColor White
        exit 1
    }
    
    $chats = $chatsResponse.data
    Write-Host "  OK Found $($chats.Count) chats" -ForegroundColor Green
    
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Possible reasons:" -ForegroundColor Yellow
    Write-Host "  1. Cookies expired - run: .\scripts\refresh-qwen-cookies.ps1" -ForegroundColor White
    Write-Host "  2. Network issue - check internet connection" -ForegroundColor White
    Write-Host "  3. API changed - check Qwen API documentation" -ForegroundColor White
    exit 1
}

Write-Host ""

# Step 3: Fetch messages for each chat
Write-Host "[3/5] Fetching messages from chats..." -ForegroundColor Yellow

$allMessages = @()
$chatCount = 0

foreach ($chat in $chats) {
    $chatCount++
    Write-Host "  Processing chat $chatCount/$($chats.Count): $($chat.title)" -ForegroundColor Gray
    
    try {
        # Get messages for this chat
        $messagesUrl = "https://chat.qwen.ai/api/v2/chats/$($chat.id)/messages"
        $messagesResponse = Invoke-RestMethod -Uri $messagesUrl -Headers $headers -Method Get -TimeoutSec 30
        
        if ($messagesResponse.success) {
            $messages = $messagesResponse.data
            Write-Host "    Found $($messages.Count) messages" -ForegroundColor Green
            
            # Format chat for RAG
            $chatText = "# Chat: $($chat.title)`n"
            $chatText += "Date: $($chat.created_at)`n"
            $chatText += "Model: $($chat.model)`n`n"
            
            foreach ($msg in $messages) {
                $role = if ($msg.role -eq "user") { "User" } else { "Assistant" }
                $chatText += "## $role`n$($msg.content)`n`n"
            }
            
            $allMessages += @{
                chat_id = $chat.id
                title = $chat.title
                content = $chatText
                message_count = $messages.Count
            }
        }
        
    } catch {
        Write-Host "    WARNING: Failed to fetch messages: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "  OK Collected $($allMessages.Count) chats with messages" -ForegroundColor Green
Write-Host ""

# Step 4: Save to files
Write-Host "[4/5] Saving chats to files..." -ForegroundColor Yellow

$outputDir = "data/qwen-chats"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

$savedCount = 0
foreach ($chat in $allMessages) {
    $filename = "$outputDir/chat-$($chat.chat_id).md"
    $chat.content | Out-File -FilePath $filename -Encoding UTF8
    $savedCount++
}

Write-Host "  OK Saved $savedCount files to $outputDir" -ForegroundColor Green
Write-Host ""

# Step 5: Ingest to RAG
Write-Host "[5/5] Ingesting to RAG system..." -ForegroundColor Yellow

try {
    $body = @{
        path = "/data/qwen-chats"
        recursive = $true
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod `
        -Uri "http://localhost:9001/ingest" `
        -Method Post `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 300
    
    Write-Host "  OK Ingested!" -ForegroundColor Green
    Write-Host "    Files processed: $($response.files_processed)" -ForegroundColor White
    Write-Host "    Chunks created: $($response.chunks_created)" -ForegroundColor White
    
    if ($response.errors.Count -gt 0) {
        Write-Host "    Errors: $($response.errors.Count)" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Make sure RAG API is running: docker ps | findstr rag-api" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=== Import Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Chats imported: $($allMessages.Count)" -ForegroundColor White
Write-Host "  Files created: $savedCount" -ForegroundColor White
Write-Host "  Chunks in RAG: $($response.chunks_created)" -ForegroundColor White
Write-Host ""
Write-Host "Now you can search your Qwen chat history:" -ForegroundColor Yellow
Write-Host '  curl -X POST http://localhost:9001/query -H "Content-Type: application/json" -d ''{"query": "your question", "top_k": 5}''' -ForegroundColor White
Write-Host ""
