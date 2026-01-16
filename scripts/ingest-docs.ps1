# Ingest Documents Script
# Ingests documents from a local path into the RAG system

param(
    [Parameter(Mandatory=$true)]
    [string]$Path,
    
    [switch]$Recursive = $true
)

$ErrorActionPreference = "Stop"

Write-Host "=== Document Ingestion ===" -ForegroundColor Cyan
Write-Host ""

# Validate path
if (-not (Test-Path $Path)) {
    Write-Host "Error: Path not found: $Path" -ForegroundColor Red
    exit 1
}

Write-Host "Ingesting from: $Path" -ForegroundColor Yellow
Write-Host "Recursive: $Recursive" -ForegroundColor Yellow
Write-Host ""

# Convert Windows path for API
$apiPath = $Path

# Call RAG API
$body = @{
    path = $apiPath
    recursive = $Recursive.IsPresent
} | ConvertTo-Json

try {
    Write-Host "Sending request to RAG API..." -ForegroundColor Gray
    
    $response = Invoke-RestMethod `
        -Uri "http://localhost:9001/ingest" `
        -Method Post `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 300
    
    Write-Host ""
    Write-Host "=== Ingestion Complete ===" -ForegroundColor Green
    Write-Host "Files processed: $($response.files_processed)" -ForegroundColor White
    Write-Host "Chunks created: $($response.chunks_created)" -ForegroundColor White
    
    if ($response.errors.Count -gt 0) {
        Write-Host ""
        Write-Host "Errors encountered:" -ForegroundColor Yellow
        foreach ($error in $response.errors) {
            Write-Host "  - $error" -ForegroundColor Red
        }
    }
    
} catch {
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
