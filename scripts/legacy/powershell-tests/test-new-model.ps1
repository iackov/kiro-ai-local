# Test New Model in AI Combiner Stack
# Supports: Ollama models, HuggingFace models via Ollama

param(
    [Parameter(Mandatory=$true)]
    [string]$ModelName,
    
    [string]$TestPrompt = "Explain what you are and your capabilities in 2 sentences."
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== Testing Model: $ModelName ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if model exists
Write-Host "[1] Checking if model is available..." -ForegroundColor Yellow
$models = ollama list | Out-String
if ($models -match $ModelName) {
    Write-Host "  OK Model found locally" -ForegroundColor Green
} else {
    Write-Host "  Model not found locally, attempting to pull..." -ForegroundColor Yellow
    Write-Host "  This may take several minutes..." -ForegroundColor Gray
    Write-Host ""
    
    try {
        ollama pull $ModelName
        Write-Host "  OK Model pulled successfully" -ForegroundColor Green
    } catch {
        Write-Host "  ERROR: Could not pull model" -ForegroundColor Red
        Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Step 2: Test basic inference
Write-Host "[2] Testing inference..." -ForegroundColor Yellow
Write-Host "  Prompt: $TestPrompt" -ForegroundColor White
Write-Host ""

$startTime = Get-Date

try {
    $response = ollama run $ModelName $TestPrompt --verbose 2>&1
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    
    Write-Host "  Response:" -ForegroundColor Cyan
    Write-Host "  $response" -ForegroundColor White
    Write-Host ""
    Write-Host "  Time: $([math]::Round($duration, 2))s" -ForegroundColor Gray
    
} catch {
    Write-Host "  ERROR: Inference failed" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Test with RAG context
Write-Host "[3] Testing with RAG context..." -ForegroundColor Yellow

# Get some context from RAG
$ragQuery = '{"query": "Python programming", "top_k": 1}'
$ragResult = Invoke-RestMethod `
    -Uri "http://localhost:9001/query" `
    -Method Post `
    -Body $ragQuery `
    -ContentType "application/json"

if ($ragResult.total_results -gt 0) {
    $context = $ragResult.documents[0].content.Substring(0, [Math]::Min(200, $ragResult.documents[0].content.Length))
    $contextPrompt = "Context: $context`n`nBased on this context, suggest an improvement."
    
    Write-Host "  Using RAG context..." -ForegroundColor White
    $response2 = ollama run $ModelName $contextPrompt 2>&1 | Select-Object -First 5
    Write-Host "  Response: $response2" -ForegroundColor Gray
}
Write-Host ""

# Step 4: Performance check
Write-Host "[4] Model Info:" -ForegroundColor Yellow
ollama show $ModelName 2>&1 | Select-Object -First 15
Write-Host ""

Write-Host "=== Test Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Model $ModelName is ready for AI Combiner Stack!" -ForegroundColor Cyan
Write-Host ""
