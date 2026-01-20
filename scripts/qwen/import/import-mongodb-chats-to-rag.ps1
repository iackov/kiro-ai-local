# Import Qwen chats from MongoDB to RAG
# Экспортирует чаты из MongoDB и загружает в RAG систему

$ErrorActionPreference = "Stop"

Write-Host "=== Import MongoDB Chats to RAG ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check MongoDB
Write-Host "[1/4] Checking MongoDB..." -ForegroundColor Yellow
$chatsCount = docker exec ai-mongodb mongosh --quiet --eval "db.chats.countDocuments()" qwen_chats 2>$null
$messagesCount = docker exec ai-mongodb mongosh --quiet --eval "db.messages.countDocuments()" qwen_chats 2>$null

Write-Host "  Chats: $chatsCount" -ForegroundColor White
Write-Host "  Messages: $messagesCount" -ForegroundColor White

if ($chatsCount -eq 0) {
    Write-Host "  No chats found in MongoDB" -ForegroundColor Yellow
    Write-Host "  Use Qwen via MCP first to create chat history" -ForegroundColor Gray
    exit 0
}
Write-Host ""

# Step 2: Export from MongoDB
Write-Host "[2/4] Exporting from MongoDB..." -ForegroundColor Yellow

# Export chats
docker exec ai-mongodb mongoexport --db qwen_chats --collection chats --out /tmp/chats.json --quiet
docker cp ai-mongodb:/tmp/chats.json data/chats.json

# Export messages  
docker exec ai-mongodb mongoexport --db qwen_chats --collection messages --out /tmp/messages.json --quiet
docker cp ai-mongodb:/tmp/messages.json data/messages.json

Write-Host "  OK Exported to data/" -ForegroundColor Green
Write-Host ""

# Step 3: Convert to Markdown
Write-Host "[3/4] Converting to Markdown..." -ForegroundColor Yellow

$chats = Get-Content data/chats.json | ForEach-Object { $_ | ConvertFrom-Json }
$messages = Get-Content data/messages.json | ForEach-Object { $_ | ConvertFrom-Json }

$outputDir = "data/qwen-chats"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

$fileCount = 0
foreach ($chat in $chats) {
    $chatId = $chat.id
    $chatMessages = $messages | Where-Object { $_.chat_id -eq $chatId }
    
    if ($chatMessages.Count -eq 0) { continue }
    
    # Create markdown
    $markdown = "# Chat: $($chat.title)`n"
    $markdown += "Created: $($chat.created_at)`n"
    $markdown += "Model: $($chat.model)`n"
    $markdown += "`n---`n`n"
    
    foreach ($msg in $chatMessages | Sort-Object timestamp) {
        $role = if ($msg.role -eq "user") { "User" } else { "Assistant" }
        $markdown += "## $role`n"
        $markdown += "$($msg.content)`n`n"
    }
    
    $filename = "$outputDir/chat-$chatId.md"
    $markdown | Out-File -FilePath $filename -Encoding UTF8
    $fileCount++
}

Write-Host "  OK Created $fileCount markdown files" -ForegroundColor Green
Write-Host ""

# Step 4: Ingest to RAG
Write-Host "[4/4] Ingesting to RAG..." -ForegroundColor Yellow

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
        -TimeoutSec 60
    
    Write-Host "  OK Ingested!" -ForegroundColor Green
    Write-Host "    Files: $($response.files_processed)" -ForegroundColor White
    Write-Host "    Chunks: $($response.chunks_created)" -ForegroundColor White
    
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Cleanup
Remove-Item data/chats.json -ErrorAction SilentlyContinue
Remove-Item data/messages.json -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== Import Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Your Qwen chat history is now in RAG!" -ForegroundColor Cyan
Write-Host "Try searching: curl -X POST http://localhost:9001/query -d '{\"query\":\"your question\"}'" -ForegroundColor Gray
Write-Host ""
