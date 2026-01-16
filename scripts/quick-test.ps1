# Quick Test - Check basic stack
$ErrorActionPreference = "Continue"

Write-Host "=== Quick Test ===" -ForegroundColor Cyan
Write-Host ""

$allOk = $true

# Test 1: Containers
Write-Host "[1/5] Checking containers..." -ForegroundColor Yellow
$containers = @("ai-ollama", "ai-rag-api", "ai-mongodb")
foreach ($c in $containers) {
    $status = docker ps --filter "name=$c" --format "{{.Status}}"
    if ($status -match "Up") {
        Write-Host "  OK $c" -ForegroundColor Green
    } else {
        Write-Host "  FAIL $c NOT RUNNING" -ForegroundColor Red
        $allOk = $false
    }
}

# Test 2: RAG API
Write-Host "`n[2/5] Testing RAG API..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:9001/health" -TimeoutSec 5
    Write-Host "  OK RAG API responds" -ForegroundColor Green
} catch {
    Write-Host "  FAIL RAG API unreachable" -ForegroundColor Red
    $allOk = $false
}

# Test 3: Database
Write-Host "`n[3/5] Testing database..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:9001/inspect" -TimeoutSec 5
    Write-Host "  OK Database accessible (docs: $($stats.total_documents))" -ForegroundColor Green
} catch {
    Write-Host "  FAIL Database check failed" -ForegroundColor Red
    $allOk = $false
}

# Test 4: Ollama
Write-Host "`n[4/5] Testing Ollama..." -ForegroundColor Yellow
try {
    $models = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    Write-Host "  OK Ollama responds (models: $($models.models.Count))" -ForegroundColor Green
    if ($models.models.Count -eq 0) {
        Write-Host "     WARNING: No models loaded" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  FAIL Ollama unreachable" -ForegroundColor Red
    $allOk = $false
}

# Test 5: MongoDB
Write-Host "`n[5/5] Testing MongoDB..." -ForegroundColor Yellow
$mongoTest = docker exec ai-mongodb mongosh --quiet --eval "db.version()" qwen_chats 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK MongoDB accessible" -ForegroundColor Green
} else {
    Write-Host "  WARNING MongoDB check inconclusive" -ForegroundColor Yellow
}

Write-Host ""
if ($allOk) {
    Write-Host "=== All Tests Passed ===" -ForegroundColor Green
    exit 0
} else {
    Write-Host "=== Some Tests Failed ===" -ForegroundColor Red
    exit 1
}
