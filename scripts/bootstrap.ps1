# AI Combiner Stack - Bootstrap Script
# Initializes the entire stack from scratch

param(
    [switch]$SkipPull = $false,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== AI Combiner Stack Bootstrap ===" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "[1/7] Checking prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "  ✓ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Docker is running
try {
    docker ps | Out-Null
    Write-Host "  ✓ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Docker daemon not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Create .env if it doesn't exist
Write-Host "[2/7] Setting up environment..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  ✓ Created .env file (please edit with your settings)" -ForegroundColor Green
} else {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green
}

# Create data directories
Write-Host "[3/7] Creating data directories..." -ForegroundColor Yellow
$directories = @("data/uploads", "logs")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created $dir" -ForegroundColor Green
    }
}

# Pull Docker images
if (-not $SkipPull) {
    Write-Host "[4/7] Pulling Docker images (this may take a while)..." -ForegroundColor Yellow
    docker compose pull
    Write-Host "  ✓ Images pulled" -ForegroundColor Green
} else {
    Write-Host "[4/7] Skipping image pull" -ForegroundColor Yellow
}

# Build custom services
Write-Host "[5/7] Building custom services..." -ForegroundColor Yellow
docker compose build
Write-Host "  ✓ Services built" -ForegroundColor Green

# Start services
Write-Host "[6/7] Starting services..." -ForegroundColor Yellow
docker compose up -d
Write-Host "  ✓ Services started" -ForegroundColor Green

# Wait for services to be ready
Write-Host "[7/7] Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Pull Ollama models
Write-Host "Pulling Ollama models..." -ForegroundColor Yellow
Write-Host "  - llama2:7b (this will take several minutes)..." -ForegroundColor Gray
docker exec ai-ollama ollama pull llama2:7b

Write-Host "  - nomic-embed-text (embedding model)..." -ForegroundColor Gray
docker exec ai-ollama ollama pull nomic-embed-text

Write-Host "  ✓ Models pulled" -ForegroundColor Green

# Health check
Write-Host ""
Write-Host "Running health check..." -ForegroundColor Yellow
& "$PSScriptRoot\health-check.ps1"

Write-Host ""
Write-Host "=== Bootstrap Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Services are running at:" -ForegroundColor Cyan
Write-Host "  - RAG API:     http://localhost:8001/docs" -ForegroundColor White
Write-Host "  - ChromaDB:    http://localhost:8000" -ForegroundColor White
Write-Host "  - Ollama:      http://localhost:11434" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Configure MCP in Kiro (see README.md)" -ForegroundColor White
Write-Host "  2. Ingest documents: .\scripts\ingest-docs.ps1 -Path C:\your\docs" -ForegroundColor White
Write-Host "  3. Test queries: .\scripts\test-query.ps1" -ForegroundColor White
Write-Host ""
