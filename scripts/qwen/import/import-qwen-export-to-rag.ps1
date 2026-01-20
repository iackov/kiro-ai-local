# Import Qwen Export to RAG
# Конвертирует экспорт чатов Qwen в markdown и загружает в RAG

param(
    [Parameter(Mandatory=$true)]
    [string]$ExportFile,
    
    [int]$MaxChats = 0  # 0 = all chats
)

$ErrorActionPreference = "Stop"

Write-Host "=== Import Qwen Export to RAG ===" -ForegroundColor Cyan
Write-Host ""

# Check file
if (-not (Test-Path $ExportFile)) {
    Write-Host "ERROR: File not found: $ExportFile" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item $ExportFile).Length / 1MB
Write-Host "File: $ExportFile" -ForegroundColor White
Write-Host "Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor White
Write-Host ""

# Parse JSON
Write-Host "[1/3] Parsing export file..." -ForegroundColor Yellow
try {
    $export = Get-Content $ExportFile -Raw -Encoding UTF8 | ConvertFrom-Json
    Write-Host "  OK Parsed successfully" -ForegroundColor Green
    
    $totalChats = $export.Count
    Write-Host "  Total chats: $totalChats" -ForegroundColor White
    
    if ($MaxChats -gt 0 -and $MaxChats -lt $totalChats) {
        Write-Host "  Will process: $MaxChats (limited)" -ForegroundColor Yellow
        $chatsToProcess = $export | Select-Object -First $MaxChats
    } else {
        $chatsToProcess = $export
    }
    
} catch {
    Write-Host "  ERROR: Failed to parse JSON: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Convert to Markdown
Write-Host "[2/3] Converting to Markdown..." -ForegroundColor Yellow

$outputDir = "data/qwen-export"
if (Test-Path $outputDir) {
    Remove-Item -Recurse -Force $outputDir
}
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

$fileCount = 0
$totalMessages = 0

foreach ($chat in $chatsToProcess) {
    $chatId = $chat.id
    $title = $chat.title -replace '[\\/:*?"<>|]', '_'  # Safe filename
    
    if (-not $chat.messages -or $chat.messages.Count -eq 0) {
        continue
    }
    
    # Create markdown
    $markdown = "# $($chat.title)`n`n"
    $markdown += "**Chat ID**: $chatId`n"
    $markdown += "**Created**: $($chat.created_at)`n"
    $markdown += "**Updated**: $($chat.updated_at)`n"
    $markdown += "**Messages**: $($chat.messages.Count)`n"
    $markdown += "`n---`n`n"
    
    foreach ($msg in $chat.messages) {
        $role = if ($msg.role -eq "user") { "👤 User" } else { "🤖 Assistant" }
        $markdown += "## $role`n`n"
        $markdown += "$($msg.content)`n`n"
        $markdown += "---`n`n"
        $totalMessages++
    }
    
    $filename = "$outputDir/chat-$fileCount-$title.md"
    $markdown | Out-File -FilePath $filename -Encoding UTF8
    $fileCount++
    
    if ($fileCount % 10 -eq 0) {
        Write-Host "  Processed $fileCount chats..." -ForegroundColor Gray
    }
}

Write-Host "  OK Created $fileCount markdown files" -ForegroundColor Green
Write-Host "  Total messages: $totalMessages" -ForegroundColor White
Write-Host ""

# Ingest to RAG
Write-Host "[3/3] Ingesting to RAG..." -ForegroundColor Yellow

try {
    $body = @{
        path = "/data/qwen-export"
        recursive = $true
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod `
        -Uri "http://localhost:9001/ingest" `
        -Method Post `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 600
    
    Write-Host "  OK Ingested!" -ForegroundColor Green
    Write-Host "    Files processed: $($response.files_processed)" -ForegroundColor White
    Write-Host "    Chunks created: $($response.chunks_created)" -ForegroundColor White
    
    if ($response.errors.Count -gt 0) {
        Write-Host "    Errors: $($response.errors.Count)" -ForegroundColor Yellow
        $response.errors | Select-Object -First 3 | ForEach-Object {
            Write-Host "      - $_" -ForegroundColor Red
        }
    }
    
} catch {
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Import Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Chats imported: $fileCount" -ForegroundColor White
Write-Host "  Messages: $totalMessages" -ForegroundColor White
Write-Host "  Chunks in RAG: $($response.chunks_created)" -ForegroundColor White
Write-Host ""
Write-Host "Now you can search your Qwen history!" -ForegroundColor Yellow
Write-Host ""
