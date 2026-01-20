# Test Qwen History Search in RAG
$ErrorActionPreference = "Stop"

Write-Host "=== Testing Qwen History Search ===" -ForegroundColor Cyan
Write-Host ""

# Check RAG status
Write-Host "[1] RAG Database Status" -ForegroundColor Yellow
$stats = Invoke-RestMethod -Uri "http://localhost:9001/inspect" -TimeoutSec 10
Write-Host "  Total documents: $($stats.total_documents)" -ForegroundColor Green
Write-Host ""

# Test 1: Python
Write-Host "[2] Search: Python" -ForegroundColor Yellow
$body1 = '{"query": "Python programming", "top_k": 3}'
$result1 = Invoke-RestMethod -Uri "http://localhost:9001/query" -Method Post -Body $body1 -ContentType "application/json"
Write-Host "  Found: $($result1.total_results) results" -ForegroundColor Green
if ($result1.total_results -gt 0) {
    $preview = $result1.documents[0].content.Substring(0, [Math]::Min(100, $result1.documents[0].content.Length))
    Write-Host "  $preview..." -ForegroundColor Gray
}
Write-Host ""

# Test 2: Docker
Write-Host "[3] Search: Docker" -ForegroundColor Yellow
$body2 = '{"query": "Docker containers", "top_k": 3}'
$result2 = Invoke-RestMethod -Uri "http://localhost:9001/query" -Method Post -Body $body2 -ContentType "application/json"
Write-Host "  Found: $($result2.total_results) results" -ForegroundColor Green
Write-Host ""

# Test 3: AI
Write-Host "[4] Search: AI" -ForegroundColor Yellow
$body3 = '{"query": "artificial intelligence neural networks", "top_k": 3}'
$result3 = Invoke-RestMethod -Uri "http://localhost:9001/query" -Method Post -Body $body3 -ContentType "application/json"
Write-Host "  Found: $($result3.total_results) results" -ForegroundColor Green
Write-Host ""

Write-Host "=== Tests Complete ===" -ForegroundColor Green
Write-Host "Your Qwen history is searchable with $($stats.total_documents) documents!" -ForegroundColor Cyan
Write-Host ""
