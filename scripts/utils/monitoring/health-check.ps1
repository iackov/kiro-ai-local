# Health Check Script
# Verifies all services are running correctly

$ErrorActionPreference = "Continue"

Write-Host "=== Health Check ===" -ForegroundColor Cyan
Write-Host ""

$allHealthy = $true

# Check Docker containers
Write-Host "Docker Containers:" -ForegroundColor Yellow
$containers = @("ai-ollama", "ai-chromadb", "ai-rag-api", "ai-mcp-gateway", "ai-mongodb")

foreach ($container in $containers) {
    $status = docker ps --filter "name=$container" --format "{{.Status}}"
    if ($status -match "Up") {
        Write-Host "  ✓ $container : Running" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $container : Not running" -ForegroundColor Red
        $allHealthy = $false
    }
}

Write-Host ""

# Check service endpoints
Write-Host "Service Endpoints:" -ForegroundColor Yellow

# RAG API
try {
    $response = Invoke-RestMethod -Uri "http://localhost:9001/health" -TimeoutSec 5
    if ($response.status -eq "healthy" -or $response.status -eq "degraded") {
        Write-Host "  ✓ RAG API (9001) : $($response.status)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ RAG API (9001) : $($response.status)" -ForegroundColor Yellow
        $allHealthy = $false
    }
} catch {
    Write-Host "  ✗ RAG API (9001) : Unreachable" -ForegroundColor Red
    $allHealthy = $false
}

# Ollama
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    $modelCount = $response.models.Count
    Write-Host "  ✓ Ollama (11434) : Healthy ($modelCount models)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Ollama (11434) : Unreachable" -ForegroundColor Red
    $allHealthy = $false
}

Write-Host ""

# Database stats
Write-Host "Database Stats:" -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:9001/inspect" -TimeoutSec 5
    Write-Host "  Documents indexed: $($stats.total_documents)" -ForegroundColor White
    Write-Host "  Collection: $($stats.collection_name)" -ForegroundColor White
} catch {
    Write-Host "  Unable to retrieve stats" -ForegroundColor Red
}

Write-Host ""

if ($allHealthy) {
    Write-Host "=== All Systems Operational ===" -ForegroundColor Green
    exit 0
} else {
    Write-Host "=== Some Services Are Down ===" -ForegroundColor Red
    Write-Host "Run 'docker compose logs' to see details" -ForegroundColor Yellow
    exit 1
}
