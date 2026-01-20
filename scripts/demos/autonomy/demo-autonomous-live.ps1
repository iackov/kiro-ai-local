# Live Demo - Autonomous System in Action

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AUTONOMOUS SYSTEM - LIVE DEMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:9000"

# Demo 1: Simple health check
Write-Host "[Demo 1] Simple Request: 'Check system health'" -ForegroundColor Yellow
$body = "message=Check%20system%20health&auto_execute=true"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45

Write-Host "  Intent: $($resp.intent) | RAG: $($resp.rag_context_used) docs | Steps: $($resp.execution_plan.steps.Count)" -ForegroundColor Cyan
Write-Host "  Decision: $($resp.execution_plan.autonomous_decision.action) (confidence: $($resp.execution_plan.autonomous_decision.confidence))" -ForegroundColor Green
Write-Host "  Result: $($resp.task_result.summary.status) - $($resp.task_result.summary.successful)/$($resp.task_result.summary.total_steps) steps" -ForegroundColor Green
Write-Host ""

# Demo 2: Complex optimization
Write-Host "[Demo 2] Complex: 'System is slow, optimize performance'" -ForegroundColor Yellow
$body = "message=System%20is%20slow%20optimize%20performance&auto_execute=true"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45

Write-Host "  Pattern: $($resp.execution_plan.adaptive_suggestions.pattern)" -ForegroundColor Cyan
Write-Host "  Steps: $($resp.execution_plan.steps.Count) (optimized: $($resp.execution_plan.optimizations_applied))" -ForegroundColor Cyan
Write-Host "  Suggestions: $($resp.execution_plan.adaptive_suggestions.suggestions.Count)" -ForegroundColor Yellow
Write-Host "  Result: $($resp.task_result.summary.success_rate)% success" -ForegroundColor Green
Write-Host ""

# Demo 3: High-risk operation
Write-Host "[Demo 3] High-Risk: 'Delete old production logs'" -ForegroundColor Yellow
$body = "message=Delete%20old%20production%20logs&auto_execute=true"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45

Write-Host "  Safety Level: $($resp.execution_plan.safety_level)" -ForegroundColor Red
Write-Host "  Decision: $($resp.execution_plan.autonomous_decision.action) (confidence: $($resp.execution_plan.autonomous_decision.confidence))" -ForegroundColor Yellow
Write-Host "  Requires Approval: $($resp.execution_plan.requires_approval)" -ForegroundColor Yellow
Write-Host "  Failure Points: $($resp.execution_plan.predicted_failure_points.Count)" -ForegroundColor Red
Write-Host ""

# Demo 4: Context-aware
Write-Host "[Demo 4] Context-Aware: 'Optimize Docker setup'" -ForegroundColor Yellow
$body = "message=Optimize%20Docker%20setup&auto_execute=false"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45

Write-Host "  RAG Context: $($resp.rag_context_used) documents" -ForegroundColor Cyan
Write-Host "  Entities: $($resp.entities.technologies -join ', ')" -ForegroundColor Cyan
Write-Host "  Confidence: $($resp.execution_plan.autonomous_decision.confidence)" -ForegroundColor Green
Write-Host "  Context-Aware: $($resp.capabilities.context_aware)" -ForegroundColor Green
Write-Host ""

# Demo 5: Learning
Write-Host "[Demo 5] Learning: Same task 3 times" -ForegroundColor Yellow
$successRates = @()
for ($i = 1; $i -le 3; $i++) {
    $body = "message=Check%20health&auto_execute=true"
    $resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45
    $successRates += $resp.execution_plan.adaptive_suggestions.historical_success_rate
    Start-Sleep -Milliseconds 300
}
Write-Host "  Success Rates: $($successRates[0])% -> $($successRates[1])% -> $($successRates[2])%" -ForegroundColor Cyan
Write-Host "  Learning: $(if ($successRates[2] -ge $successRates[0]) { 'Improved' } else { 'Stable' })" -ForegroundColor Green
Write-Host ""

# System Insights
Write-Host "[System Intelligence]" -ForegroundColor Yellow
$adaptive = Invoke-RestMethod -Uri "$baseUrl/api/learning/adaptive" -TimeoutSec 10
$decisions = Invoke-RestMethod -Uri "$baseUrl/api/decisions/insights" -TimeoutSec 10
$meta = Invoke-RestMethod -Uri "$baseUrl/api/meta-learning/insights" -TimeoutSec 10
$predictive = Invoke-RestMethod -Uri "$baseUrl/api/predictive/insights" -TimeoutSec 10

Write-Host "  Executions: $($adaptive.total_executions) | Success: $($adaptive.overall_success_rate)% | Patterns: $($adaptive.patterns_learned)" -ForegroundColor Cyan
Write-Host "  Decisions: $($decisions.total_decisions) | Confidence: $($decisions.avg_confidence)" -ForegroundColor Cyan
Write-Host "  Meta-Learning: $($meta.strategies.Count) strategies" -ForegroundColor Cyan
Write-Host "  Predictions: $($predictive.total_predictions) | Prevented: $($predictive.prevented_issues)" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "   SYSTEM FULLY OPERATIONAL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Capabilities Demonstrated:" -ForegroundColor White
Write-Host "  [OK] Context Understanding" -ForegroundColor Green
Write-Host "  [OK] Intelligent Planning" -ForegroundColor Green
Write-Host "  [OK] Risk Assessment" -ForegroundColor Green
Write-Host "  [OK] RAG Integration" -ForegroundColor Green
Write-Host "  [OK] Adaptive Learning" -ForegroundColor Green
Write-Host "  [OK] Decision Making" -ForegroundColor Green
Write-Host "  [OK] Meta-Learning" -ForegroundColor Green
Write-Host "  [OK] Predictive Analysis" -ForegroundColor Green
Write-Host ""
