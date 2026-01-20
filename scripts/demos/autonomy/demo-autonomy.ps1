# Full Autonomy Demo - Showcase all 6 levels
Write-Host "=== FULL AUTONOMY DEMONSTRATION ===" -ForegroundColor Cyan
Write-Host "Demonstrating all 6 autonomy levels in action" -ForegroundColor White
Write-Host ""

$baseUrl = "http://localhost:9000"

# Level 1: Basic RAG
Write-Host "[Level 1] Basic RAG Query" -ForegroundColor Yellow
Write-Host "Query: 'How to configure docker compose?'" -ForegroundColor Gray
$body = @{ query = "How to configure docker compose?"; top_k = 3 }
$rag = Invoke-RestMethod -Uri "$baseUrl/api/rag/query" -Method Post -Body $body -TimeoutSec 30
Write-Host "  Found $($rag.documents.Count) documents in $([math]::Round($rag.latency_ms, 0))ms" -ForegroundColor Green
Write-Host ""

# Level 2: Multi-Service Orchestration
Write-Host "[Level 2] Multi-Service Orchestration" -ForegroundColor Yellow
Write-Host "Query: 'How to add Redis service?'" -ForegroundColor Gray
$body = @{ query = "How to add Redis service?"; top_k = 3 }
$combined = Invoke-RestMethod -Uri "$baseUrl/api/combined/query" -Method Post -Body $body -TimeoutSec 30
Write-Host "  Services used: $($combined.services_used -join ', ')" -ForegroundColor Green
Write-Host "  Total latency: $([math]::Round($combined.latency_ms, 0))ms" -ForegroundColor Green
Write-Host ""

# Level 3: Architecture Engine
Write-Host "[Level 3] Architecture Engine" -ForegroundColor Yellow
Write-Host "Proposing: 'Add nginx service with 256M memory'" -ForegroundColor Gray
$body = @{ prompt = "Add nginx service with 256M memory"; auto_apply = $false }
$arch = Invoke-RestMethod -Uri "$baseUrl/api/arch/propose" -Method Post -Body $body -TimeoutSec 30
Write-Host "  Safe: $($arch.safe)" -ForegroundColor $(if($arch.safe) { "Green" } else { "Red" })
Write-Host "  Changes: $($arch.changes.Count) modifications" -ForegroundColor Green
Write-Host "  Change ID: $($arch.change_id)" -ForegroundColor Cyan
Write-Host ""

# Level 4: Metrics & Insights
Write-Host "[Level 4] Metrics & Performance Analysis" -ForegroundColor Yellow
$metrics = Invoke-RestMethod -Uri "$baseUrl/api/metrics/insights" -TimeoutSec 30
Write-Host "  Health Score: $($metrics.health_score)/100" -ForegroundColor Green
Write-Host "  Insights: $($metrics.insights.Count)" -ForegroundColor Cyan
foreach ($insight in $metrics.insights) {
    Write-Host "    - $insight" -ForegroundColor White
}
Write-Host "  Suggestions: $($metrics.suggestions.Count)" -ForegroundColor Cyan
foreach ($suggestion in $metrics.suggestions | Select-Object -First 2) {
    Write-Host "    [$($suggestion.priority)] $($suggestion.suggestion)" -ForegroundColor White
}
Write-Host ""

# Level 5: Adaptive Learning
Write-Host "[Level 5] Adaptive Learning" -ForegroundColor Yellow
Write-Host "Recording user preference..." -ForegroundColor Gray
$body = @{ suggestion_id = "add_redis_cache"; action = "applied" }
Invoke-RestMethod -Uri "$baseUrl/api/learning/feedback" -Method Post -Body $body -TimeoutSec 30 | Out-Null

$learning = Invoke-RestMethod -Uri "$baseUrl/api/learning/insights" -TimeoutSec 30
Write-Host "  Total suggestions: $($learning.total_suggestions)" -ForegroundColor Green
Write-Host "  Acceptance rate: $([math]::Round($learning.acceptance_rate * 100, 1))%" -ForegroundColor Green
if ($learning.insights.Count -gt 0) {
    Write-Host "  Learning insights:" -ForegroundColor Cyan
    foreach ($insight in $learning.insights) {
        Write-Host "    - $insight" -ForegroundColor White
    }
}
Write-Host ""

# Level 6: Auto-Healing
Write-Host "[Level 6] Auto-Healing Detection" -ForegroundColor Yellow
Write-Host "Simulating errors..." -ForegroundColor Gray
for ($i = 1; $i -le 12; $i++) {
    try {
        $body = @{ query = "invalid query $i"; top_k = 999 }
        Invoke-RestMethod -Uri "$baseUrl/api/rag/query" -Method Post -Body $body -TimeoutSec 5 | Out-Null
    } catch {
        # Expected to fail
    }
}

Start-Sleep -Seconds 1
$opps = Invoke-RestMethod -Uri "$baseUrl/api/auto/opportunities" -TimeoutSec 30
Write-Host "  Auto-healing opportunities detected: $($opps.total)" -ForegroundColor $(if($opps.total -gt 0) { "Yellow" } else { "Green" })

if ($opps.total -gt 0) {
    Write-Host "  Opportunities:" -ForegroundColor Cyan
    foreach ($opp in $opps.opportunities) {
        Write-Host "    [$($opp.confidence)] $($opp.service): $($opp.issue)" -ForegroundColor White
        Write-Host "      Action: $($opp.action)" -ForegroundColor Cyan
    }
    
    Write-Host ""
    Write-Host "  Executing auto-healing..." -ForegroundColor Yellow
    $firstOpp = $opps.opportunities[0]
    $body = @{ action_type = "restart_service"; service = $firstOpp.service }
    $result = Invoke-RestMethod -Uri "$baseUrl/api/auto/execute" -Method Post -Body $body -TimeoutSec 30
    Write-Host "  Status: $($result.status)" -ForegroundColor Green
    Write-Host "  Message: $($result.message)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== DEMONSTRATION COMPLETE ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "All 6 autonomy levels demonstrated:" -ForegroundColor White
Write-Host "  [1] Basic RAG - Knowledge retrieval" -ForegroundColor Green
Write-Host "  [2] Multi-Service - Orchestration" -ForegroundColor Green
Write-Host "  [3] Architecture - Self-modification" -ForegroundColor Green
Write-Host "  [4] Metrics - Self-monitoring" -ForegroundColor Green
Write-Host "  [5] Learning - Adaptation" -ForegroundColor Green
Write-Host "  [6] Auto-Healing - Self-repair" -ForegroundColor Green
Write-Host ""
Write-Host "FULL AUTONOMY ACHIEVED!" -ForegroundColor Green
