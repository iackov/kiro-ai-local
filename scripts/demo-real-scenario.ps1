# Real Scenario: Search history + Ask Qwen with context

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== REAL SCENARIO DEMO ===" -ForegroundColor Cyan
Write-Host "Task: Find Docker info from history, then ask Qwen to create docker-compose" -ForegroundColor White
Write-Host ""

# Scenario 1: Search history
Write-Host "[1] Searching Qwen history for Docker knowledge..." -ForegroundColor Yellow
$body = '{"query": "Docker containers setup configuration", "top_k": 3}'
$results = Invoke-RestMethod `
    -Uri "http://localhost:9001/query" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"

Write-Host "  Found: $($results.total_results) relevant conversations" -ForegroundColor Green
Write-Host ""

if ($results.total_results -gt 0) {
    Write-Host "  Context from your history:" -ForegroundColor Cyan
    for ($i = 0; $i -lt [Math]::Min(2, $results.documents.Count); $i++) {
        $doc = $results.documents[$i]
        $preview = $doc.content.Substring(0, [Math]::Min(150, $doc.content.Length))
        Write-Host "    [$($i+1)] $preview..." -ForegroundColor Gray
    }
}
Write-Host ""

# Scenario 2: Test another search
Write-Host "[2] Searching for Python examples..." -ForegroundColor Yellow
$body2 = '{"query": "Python web server Flask FastAPI", "top_k": 2}'
$results2 = Invoke-RestMethod `
    -Uri "http://localhost:9001/query" `
    -Method Post `
    -Body $body2 `
    -ContentType "application/json"

Write-Host "  Found: $($results2.total_results) Python examples" -ForegroundColor Green
Write-Host ""

# Scenario 3: Show how it works in Kiro
Write-Host "[3] How this works in Kiro IDE:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Step 1: You ask Kiro" -ForegroundColor Cyan
Write-Host "    'Find my Docker notes and create a docker-compose for Python app'" -ForegroundColor White
Write-Host ""
Write-Host "  Step 2: Kiro uses MCP to:" -ForegroundColor Cyan
Write-Host "    a) Call rag_query('Docker Python')" -ForegroundColor White
Write-Host "    b) Get relevant context from your 19103 documents" -ForegroundColor White
Write-Host "    c) Call qwen_chat() with context + your question" -ForegroundColor White
Write-Host ""
Write-Host "  Step 3: Qwen responds with:" -ForegroundColor Cyan
Write-Host "    - Context-aware answer based on YOUR previous conversations" -ForegroundColor White
Write-Host "    - Personalized to your coding style and preferences" -ForegroundColor White
Write-Host "    - Complete docker-compose.yml example" -ForegroundColor White
Write-Host ""

# Show the power
Write-Host "[4] The Power of AI Combiner:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  WITHOUT RAG:" -ForegroundColor Red
Write-Host "    Qwen: 'Here is a generic docker-compose example...'" -ForegroundColor Gray
Write-Host ""
Write-Host "  WITH RAG:" -ForegroundColor Green
Write-Host "    Qwen: 'Based on your previous Docker setup where you used" -ForegroundColor Gray
Write-Host "           port 5000 and preferred alpine images, here is" -ForegroundColor Gray
Write-Host "           a docker-compose that matches your style...'" -ForegroundColor Gray
Write-Host ""

Write-Host "=== SCENARIO COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "Your AI now has MEMORY of all $($results.total_results + $results2.total_results)+ conversations!" -ForegroundColor Cyan
Write-Host ""
