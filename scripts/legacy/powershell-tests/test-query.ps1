# Test Query Script
# Tests the RAG system with a sample query

param(
    [Parameter(Mandatory=$false)]
    [string]$Query = "What is the architecture of this system?",
    
    [int]$TopK = 5
)

$ErrorActionPreference = "Stop"

Write-Host "=== RAG Query Test ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Query: $Query" -ForegroundColor Yellow
Write-Host ""

$body = @{
    query = $Query
    top_k = $TopK
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod `
        -Uri "http://localhost:9001/query" `
        -Method Post `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 30
    
    Write-Host "Results: $($response.total_results)" -ForegroundColor Green
    Write-Host "Processing time: $([math]::Round($response.processing_time_ms, 2))ms" -ForegroundColor Gray
    Write-Host ""
    
    foreach ($doc in $response.documents) {
        Write-Host "---" -ForegroundColor Gray
        Write-Host "Score: $([math]::Round($doc.score, 4))" -ForegroundColor Cyan
        Write-Host "Source: $($doc.metadata.source)" -ForegroundColor Gray
        Write-Host ""
        Write-Host $doc.content.Substring(0, [Math]::Min(200, $doc.content.Length)) -ForegroundColor White
        if ($doc.content.Length -gt 200) {
            Write-Host "..." -ForegroundColor Gray
        }
        Write-Host ""
    }
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
