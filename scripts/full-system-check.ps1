# Full System Check
$ErrorActionPreference = "Continue"

Write-Host "=== AI COMBINER STACK - FULL SYSTEM CHECK ===" -ForegroundColor Cyan
Write-Host ""

$passed = 0
$failed = 0

# Docker Infrastructure
Write-Host "[1/6] Docker Infrastructure" -ForegroundColor Yellow
$containers = @("ai-ollama", "ai-rag-api", "ai-mcp-gateway", "ai-mongodb")
foreach ($c in $containers) {
    $status = docker ps --filter "name=$c" --format "{{.Status}}"
    if ($status -match "Up") {
        Write-Host "  OK $c" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "  FAIL $c" -ForegroundColor Red
        $failed++
    }
}

# Core Services
Write-Host "`n[2/6] Core Services" -ForegroundColor Yellow
try {
    $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    Write-Host "  OK Ollama (11434)" -ForegroundColor Green
    $passed++
} catch {
    Write-Host "  FAIL Ollama" -ForegroundColor Red
    $failed++
}

try {
    $null = Invoke-RestMethod -Uri "http://localhost:9001/health" -TimeoutSec 5
    Write-Host "  OK RAG API (9001)" -ForegroundColor Green
    $passed++
} catch {
    Write-Host "  FAIL RAG API" -ForegroundColor Red
    $failed++
}

try {
    $null = Invoke-RestMethod -Uri "http://localhost:9002/health" -TimeoutSec 5
    Write-Host "  OK MCP Gateway (9002)" -ForegroundColor Green
    $passed++
} catch {
    Write-Host "  FAIL MCP Gateway" -ForegroundColor Red
    $failed++
}

# RAG Functionality
Write-Host "`n[3/6] RAG Functionality" -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:9001/inspect" -TimeoutSec 5
    Write-Host "  OK Database ($($stats.total_documents) docs)" -ForegroundColor Green
    $passed++
} catch {
    Write-Host "  FAIL Database" -ForegroundColor Red
    $failed++
}

try {
    $body = '{"query": "test", "top_k": 1}'
    $null = Invoke-RestMethod -Uri "http://localhost:9001/query" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
    Write-Host "  OK Semantic search" -ForegroundColor Green
    $passed++
} catch {
    Write-Host "  FAIL Semantic search" -ForegroundColor Red
    $failed++
}

# Qwen MCP
Write-Host "`n[4/6] Qwen MCP" -ForegroundColor Yellow
$qwenPath = "C:\Users\Jack\source\kiro\qwen\src\mcp_server"
if ((Test-Path "$qwenPath\qwen_mcp_server.py") -and (Test-Path "$qwenPath\qwen_client.py")) {
    Write-Host "  OK Qwen files" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  FAIL Qwen files" -ForegroundColor Red
    $failed++
}

if (Test-Path "$qwenPath\qwen_config.json") {
    $config = Get-Content "$qwenPath\qwen_config.json" -Raw | ConvertFrom-Json
    if ($config.cookies.cookie_string.Length -gt 100) {
        Write-Host "  OK Qwen config (cookie: $($config.cookies.cookie_string.Length) chars)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "  FAIL Qwen config (no cookie)" -ForegroundColor Red
        $failed++
    }
}

$mcpPath = "$env:USERPROFILE\.kiro\settings\mcp.json"
if (Test-Path $mcpPath) {
    $mcpConfig = Get-Content $mcpPath -Raw | ConvertFrom-Json
    if ($mcpConfig.mcpServers.'qwen-chat') {
        Write-Host "  OK Kiro MCP config" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "  FAIL Kiro MCP config" -ForegroundColor Red
        $failed++
    }
}

# Data Persistence
Write-Host "`n[5/6] Data Persistence" -ForegroundColor Yellow
$result = docker exec ai-rag-api test -f /chroma/chroma/chroma.sqlite3 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK ChromaDB SQLite" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  FAIL ChromaDB SQLite" -ForegroundColor Red
    $failed++
}

$result = docker exec ai-mongodb mongosh --quiet --eval "db.version()" qwen_chats 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK MongoDB accessible" -ForegroundColor Green
    $passed++
} else {
    Write-Host "  FAIL MongoDB" -ForegroundColor Red
    $failed++
}

# Performance
Write-Host "`n[6/6] Performance" -ForegroundColor Yellow
try {
    $models = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    Write-Host "  OK Ollama models ($($models.models.Count) loaded)" -ForegroundColor Green
    $passed++
} catch {
    Write-Host "  FAIL Ollama models" -ForegroundColor Red
    $failed++
}

try {
    $start = Get-Date
    $body = '{"query": "test", "top_k": 1}'
    $null = Invoke-RestMethod -Uri "http://localhost:9001/query" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
    $duration = ((Get-Date) - $start).TotalMilliseconds
    Write-Host "  OK Query performance ($([math]::Round($duration, 0))ms)" -ForegroundColor Green
    $passed++
} catch {
    Write-Host "  FAIL Query performance" -ForegroundColor Red
    $failed++
}

# Summary
Write-Host ""
Write-Host "=== AUTONOMY LEVELS ===" -ForegroundColor Cyan
Write-Host ""

# Level 1: RAG
Write-Host "[Level 1] Basic RAG..." -NoNewline
try {
    $body = @{ query = "test"; top_k = 1 }
    $rag = Invoke-RestMethod -Uri "http://localhost:9000/api/rag/query" -Method Post -Body $body -TimeoutSec 10
    Write-Host " OK" -ForegroundColor Green
    $passed++
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $failed++
}

# Level 2: Multi-Service
Write-Host "[Level 2] Multi-Service..." -NoNewline
try {
    $body = @{ query = "test"; top_k = 1 }
    $combined = Invoke-RestMethod -Uri "http://localhost:9000/api/combined/query" -Method Post -Body $body -TimeoutSec 10
    Write-Host " OK ($($combined.services_used.Count) services)" -ForegroundColor Green
    $passed++
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $failed++
}

# Level 3: Architecture
Write-Host "[Level 3] Architecture..." -NoNewline
try {
    $body = @{ prompt = "test"; auto_apply = $false }
    $arch = Invoke-RestMethod -Uri "http://localhost:9000/api/arch/propose" -Method Post -Body $body -TimeoutSec 10
    Write-Host " OK" -ForegroundColor Green
    $passed++
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $failed++
}

# Level 4: Metrics
Write-Host "[Level 4] Metrics..." -NoNewline
try {
    $metrics = Invoke-RestMethod -Uri "http://localhost:9000/api/metrics/insights" -TimeoutSec 10
    Write-Host " OK (health: $($metrics.health_score))" -ForegroundColor Green
    $passed++
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $failed++
}

# Level 5: Learning
Write-Host "[Level 5] Learning..." -NoNewline
try {
    $learning = Invoke-RestMethod -Uri "http://localhost:9000/api/learning/insights" -TimeoutSec 10
    Write-Host " OK" -ForegroundColor Green
    $passed++
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $failed++
}

# Level 6: Auto-Healing
Write-Host "[Level 6] Auto-Healing..." -NoNewline
try {
    $opps = Invoke-RestMethod -Uri "http://localhost:9000/api/auto/opportunities" -TimeoutSec 10
    Write-Host " OK" -ForegroundColor Green
    $passed++
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $failed++
}

# Summary
Write-Host ""
Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
$total = $passed + $failed
$rate = [math]::Round(($passed / $total) * 100, 1)
Write-Host "Total: $total | Passed: $passed | Failed: $failed | Rate: $rate%" -ForegroundColor White
Write-Host ""

if ($failed -eq 0) {
    Write-Host "ALL SYSTEMS OPERATIONAL - FULL AUTONOMY ACHIEVED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Services:" -ForegroundColor Yellow
    Write-Host "  Web UI:      http://localhost:9000" -ForegroundColor White
    Write-Host "  RAG API:     http://localhost:9001/docs" -ForegroundColor White
    Write-Host "  MCP Gateway: http://localhost:9002/health" -ForegroundColor White
    Write-Host "  Arch Engine: http://localhost:9004/docs" -ForegroundColor White
    Write-Host "  Ollama:      http://localhost:11434" -ForegroundColor White
    Write-Host "  MongoDB:     mongodb://localhost:27017" -ForegroundColor White
    Write-Host ""
    Write-Host "Autonomy Levels: 6/6 Active" -ForegroundColor Green
    Write-Host "Kiro IDE: qwen-chat Connected" -ForegroundColor Green
    exit 0
} else {
    Write-Host "SOME TESTS FAILED" -ForegroundColor Red
    Write-Host "Check errors above" -ForegroundColor Yellow
    exit 1
}
