# Import Qwen Export to RAG in batches
param(
    [Parameter(Mandatory=$true)]
    [string]$ExportFile,
    [int]$BatchSize = 50
)

$ErrorActionPreference = "Stop"

Write-Host "=== Import Qwen Export to RAG (Batched) ===" -ForegroundColor Cyan
Write-Host ""

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
$export = Get-Content $ExportFile -Raw -Encoding UTF8 | ConvertFrom-Json
$chats = $export.data
$totalChats = $chats.Count
Write-Host "  Total chats: $totalChats" -ForegroundColor White

$batches = [math]::Ceiling($totalChats / $BatchSize)
Write-Host "  Will process in $batches batches" -ForegroundColor White
Write-Host ""

$totalProcessed = 0
$totalMessages = 0
$totalChunks = 0

for ($batch = 0; $batch -lt $batches; $batch++) {
    $start = $batch * $BatchSize
    $end = [math]::Min($start + $BatchSize - 1, $totalChats - 1)
    $batchChats = $chats[$start..$end]
    
    Write-Host "[Batch $($batch + 1)/$batches] Processing chats $($start + 1)-$($end + 1)..." -ForegroundColor Yellow
    
    $batchDir = "data/qwen-batch-$batch"
    if (Test-Path $batchDir) {
        Remove-Item -Recurse -Force $batchDir
    }
    New-Item -ItemType Directory -Path $batchDir -Force | Out-Null
    
    $batchFiles = 0
    $batchMessages = 0
    
    foreach ($chat in $batchChats) {
        # Get messages from history object
        $messages = @()
        if ($chat.chat.history.messages) {
            $chat.chat.history.messages.PSObject.Properties | ForEach-Object {
                $messages += $_.Value
            }
        }
        
        if ($messages.Count -eq 0) {
            continue
        }
        
        $title = $chat.title -replace '[\\/:*?"<>|]', '_'
        
        # Create markdown
        $markdown = "# $($chat.title)`n`n"
        $markdown += "**Chat ID**: $($chat.id)`n"
        $markdown += "**Created**: $($chat.created_at)`n"
        $markdown += "**Type**: $($chat.chat_type)`n"
        $markdown += "**Tags**: $($chat.meta.tags)`n"
        $markdown += "`n---`n`n"
        
        foreach ($msg in $messages) {
            if (-not $msg.content) { continue }
            
            $role = if ($msg.role -eq "user") { "👤 User" } else { "🤖 Assistant" }
            $markdown += "## $role`n`n"
            $markdown += "$($msg.content)`n`n"
            $markdown += "---`n`n"
            $batchMessages++
        }
        
        $filename = "$batchDir/chat-$batchFiles-$title.md"
        $markdown | Out-File -FilePath $filename -Encoding UTF8
        $batchFiles++
    }
    
    Write-Host "  Created $batchFiles files with $batchMessages messages" -ForegroundColor Gray
    
    if ($batchFiles -eq 0) {
        Write-Host "  Skipping empty batch" -ForegroundColor Yellow
        Remove-Item -Recurse -Force $batchDir
        continue
    }
    
    # Ingest to RAG
    try {
        $body = @{
            path = "/data/qwen-batch-$batch"
            recursive = $true
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod `
            -Uri "http://localhost:9001/ingest" `
            -Method Post `
            -Body $body `
            -ContentType "application/json" `
            -TimeoutSec 600
        
        Write-Host "  OK Ingested: $($response.files_processed) files, $($response.chunks_created) chunks" -ForegroundColor Green
        
        $totalProcessed += $batchFiles
        $totalMessages += $batchMessages
        $totalChunks += $response.chunks_created
        
    } catch {
        Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Remove-Item -Recurse -Force $batchDir
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "=== Import Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Chats processed: $totalProcessed" -ForegroundColor White
Write-Host "  Messages: $totalMessages" -ForegroundColor White
Write-Host "  Chunks in RAG: $totalChunks" -ForegroundColor White
Write-Host ""

$stats = Invoke-RestMethod -Uri "http://localhost:9001/inspect"
Write-Host "Total documents in RAG: $($stats.total_documents)" -ForegroundColor Yellow
Write-Host ""
