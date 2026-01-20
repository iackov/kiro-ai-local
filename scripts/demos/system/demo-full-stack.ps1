# AI Combiner Stack - Full Demo
# Demonstrates: RAG search + Qwen chat + MCP integration

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AI COMBINER STACK - FULL DEMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check all services
Write-Host "[Step 1] Checking Services..." -ForegroundColor Yellow
Write-Host ""

$services = @(
    @{ name = "RAG API"; url = "http://localhost:9001/inspect" },
    @{ name = "Ollama"; url = "http://localhost:11434/api/tags" },
    @{ name = "Qwen Chat"; url = "http://localhost:3000" }
)

foreach ($svc in $services) {
    try {
        $null = Invoke-RestMethod -Uri $svc.url -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  OK $($svc.name)" -ForegroundColor Green
    } catch {
        Write-Host "  X  $($svc.name) - NOT RUNNING" -ForegroundColor Red
    }
}
Write-Host ""

# Step 2: RAG Database Stats
Write-Host "[Step 2] RAG Database Status" -ForegroundColor Yellow
$stats = Invoke-RestMethod -Uri "http://localhost:9001/inspect"
Write-Host "  Documents: $($stats.total_documents)" -ForegroundColor White
Write-Host "  Collection: $($stats.collection_name)" -ForegroundColor White
Write-Host ""

# Step 3: Search Qwen History
Write-Host "[Step 3] Searching Qwen History in RAG..." -ForegroundColor Yellow
$searchQuery = "Python Flask web server"
Write-Host "  Query: '$searchQuery'" -ForegroundColor White

$body = @{
    query = $searchQuery
    top_k = 2
} | ConvertTo-Json

$ragResults = Invoke-RestMethod `
    -Uri "http://localhost:9001/query" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"

Write-Host "  Found: $($ragResults.total_results) results" -ForegroundColor Green
Write-Host "  Time: $([math]::Round($ragResults.processing_time_ms, 2))ms" -ForegroundColor Gray
Write-Host ""

if ($ragResults.total_results -gt 0) {
    Write-Host "  Top Result:" -ForegroundColor Cyan
    $topDoc = $ragResults.documents[0]
    $preview = $topDoc.content.Substring(0, [Math]::Min(300, $topDoc.content.Length))
    Write-Host "    $preview..." -ForegroundColor Gray
    Write-Host ""
}

# Step 4: Combine with Qwen
Write-Host "[Step 4] Combining RAG Context with Qwen..." -ForegroundColor Yellow
Write-Host ""

# Build context from RAG results
$context = "Context from your previous conversations:`n`n"
foreach ($doc in $ragResults.documents) {
    $snippet = $doc.content.Substring(0, [Math]::Min(200, $doc.content.Length))
    $context += "- $snippet...`n`n"
}

# Create prompt with context
$prompt = "$context`n`nBased on the above context, create a simple Flask hello world example."

Write-Host "  Sending to Qwen with RAG context..." -ForegroundColor White
Write-Host "  (This would normally go through MCP)" -ForegroundColor Gray
Write-Host ""

# Step 5: Show MCP Integration
Write-Host "[Step 5] MCP Integration Available" -ForegroundColor Yellow
Write-Host ""
Write-Host "  In Kiro IDE, you can use:" -ForegroundColor White
Write-Host "    - qwen_chat: Send messages to Qwen" -ForegroundColor Gray
Write-Host "    - rag_query: Search your Qwen history" -ForegroundColor Gray
Write-Host ""
Write-Host "  Example workflow:" -ForegroundColor Cyan
Write-Host "    1. Search history: rag_query('Python Flask')" -ForegroundColor White
Write-Host "    2. Get context from results" -ForegroundColor White
Write-Host "    3. Ask Qwen: qwen_chat('Improve this Flask code')" -ForegroundColor White
Write-Host "    4. Qwen responds with context-aware answer" -ForegroundColor White
Write-Host ""

# Step 6: Architecture Summary
Write-Host "[Step 6] Stack Architecture" -ForegroundColor Yellow
Write-Host ""
Write-Host "  [Kiro IDE] <--MCP--> [Qwen MCP Server]" -ForegroundColor Cyan
Write-Host "       |                      |" -ForegroundColor Gray
Write-Host "       |                      v" -ForegroundColor Gray
Write-Host "       |              [Qwen Chat :3000]" -ForegroundColor Cyan
Write-Host "       |" -ForegroundColor Gray
Write-Host "       +-----------> [RAG API :9001]" -ForegroundColor Cyan
Write-Host "                            |" -ForegroundColor Gray
Write-Host "                            v" -ForegroundColor Gray
Write-Host "                     [ChromaDB + Ollama]" -ForegroundColor Cyan
Write-Host ""

# Step 7: Usage Examples
Write-Host "[Step 7] Real Usage Examples" -ForegroundColor Yellow
Write-Host ""
Write-Host "  A) Search your Qwen history:" -ForegroundColor Cyan
Write-Host "     curl -X POST http://localhost:9001/query \" -ForegroundColor White
Write-Host "       -H 'Content-Type: application/json' \" -ForegroundColor White
Write-Host "       -d '{\"query\": \"Docker setup\", \"top_k\": 5}'" -ForegroundColor White
Write-Host ""
Write-Host "  B) In Kiro IDE (via MCP):" -ForegroundColor Cyan
Write-Host "     @kiro search my Qwen history for Docker examples" -ForegroundColor White
Write-Host ""
Write-Host "  C) Combine RAG + Qwen:" -ForegroundColor Cyan
Write-Host "     @kiro use rag_query to find my Python notes," -ForegroundColor White
Write-Host "           then ask Qwen to improve the code" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "   DEMO COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your AI Combiner Stack is ready!" -ForegroundColor Cyan
Write-Host "  - $($stats.total_documents) documents searchable" -ForegroundColor White
Write-Host "  - RAG + Qwen + MCP integrated" -ForegroundColor White
Write-Host "  - Full context-aware AI system" -ForegroundColor White
Write-Host ""
