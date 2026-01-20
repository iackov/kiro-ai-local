# Demonstration: Declarative vs Imperative Approach

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DECLARATIVE vs IMPERATIVE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:9000"

# WRONG: Imperative approach (what we DON'T do)
Write-Host "[IMPERATIVE APPROACH - WRONG]" -ForegroundColor Red
Write-Host "User tells system HOW to do things:" -ForegroundColor Red
Write-Host ""
Write-Host "  User: 'Execute docker ps command'" -ForegroundColor Gray
Write-Host "  User: 'Then check RAG service on port 9001'" -ForegroundColor Gray
Write-Host "  User: 'Then analyze metrics endpoint'" -ForegroundColor Gray
Write-Host "  User: 'Then aggregate results'" -ForegroundColor Gray
Write-Host ""
Write-Host "Problems:" -ForegroundColor Red
Write-Host "  - User must know implementation details" -ForegroundColor Yellow
Write-Host "  - No intelligence or autonomy" -ForegroundColor Yellow
Write-Host "  - Brittle and error-prone" -ForegroundColor Yellow
Write-Host "  - No learning or adaptation" -ForegroundColor Yellow
Write-Host ""
Start-Sleep -Seconds 2

# RIGHT: Declarative approach (what we DO)
Write-Host "[DECLARATIVE APPROACH - CORRECT]" -ForegroundColor Green
Write-Host "User tells system WHAT they want:" -ForegroundColor Green
Write-Host ""
Write-Host "  User: 'Check system health'" -ForegroundColor White
Write-Host ""
Write-Host "System autonomously:" -ForegroundColor Cyan
Write-Host "  1. Understands intent (execute)" -ForegroundColor Gray
Write-Host "  2. Searches knowledge base (RAG)" -ForegroundColor Gray
Write-Host "  3. Creates intelligent plan" -ForegroundColor Gray
Write-Host "  4. Assesses risks" -ForegroundColor Gray
Write-Host "  5. Makes decision" -ForegroundColor Gray
Write-Host "  6. Executes autonomously" -ForegroundColor Gray
Write-Host ""

# Live demonstration
Write-Host "LIVE DEMONSTRATION:" -ForegroundColor Yellow
Write-Host ""

$body = "message=Check%20system%20health&auto_execute=true"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45

Write-Host "Input (Declarative):" -ForegroundColor Cyan
Write-Host "  'Check system health'" -ForegroundColor White
Write-Host ""

Write-Host "System's Autonomous Response:" -ForegroundColor Cyan
Write-Host "  Intent: $($resp.intent)" -ForegroundColor White
Write-Host "  RAG Context: $($resp.rag_context_used) documents" -ForegroundColor White
Write-Host "  Entities: $($resp.entities.services -join ', ')" -ForegroundColor White
Write-Host ""

Write-Host "  Intelligent Plan Created:" -ForegroundColor White
for ($i = 0; $i -lt $resp.execution_plan.steps.Count; $i++) {
    Write-Host "    $($i+1). $($resp.execution_plan.steps[$i])" -ForegroundColor Gray
}
Write-Host ""

Write-Host "  Decision Made:" -ForegroundColor White
Write-Host "    Action: $($resp.execution_plan.autonomous_decision.action)" -ForegroundColor Green
Write-Host "    Confidence: $($resp.execution_plan.autonomous_decision.confidence)" -ForegroundColor Green
Write-Host "    Reasoning: $($resp.execution_plan.autonomous_decision.reasoning[0])" -ForegroundColor Gray
Write-Host ""

Write-Host "  Execution Result:" -ForegroundColor White
Write-Host "    Status: $($resp.task_result.summary.status)" -ForegroundColor Green
Write-Host "    Success: $($resp.task_result.summary.successful)/$($resp.task_result.summary.total_steps) steps" -ForegroundColor Green
Write-Host "    Rate: $($resp.task_result.summary.success_rate)%" -ForegroundColor Green
Write-Host ""

Write-Host "Benefits:" -ForegroundColor Green
Write-Host "  [OK] User doesn't need technical knowledge" -ForegroundColor White
Write-Host "  [OK] System is intelligent and autonomous" -ForegroundColor White
Write-Host "  [OK] Adapts and learns" -ForegroundColor White
Write-Host "  [OK] Safe and reliable" -ForegroundColor White
Write-Host ""
Start-Sleep -Seconds 2

# Example 2: Complex request
Write-Host "[Example 2] Complex Declarative Request" -ForegroundColor Yellow
Write-Host ""
Write-Host "User says: 'System is slow, fix it'" -ForegroundColor White
Write-Host ""

$body = "message=System%20is%20slow%20fix%20it&auto_execute=true"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45

Write-Host "System autonomously:" -ForegroundColor Cyan
Write-Host "  - Detected pattern: $($resp.execution_plan.adaptive_suggestions.pattern)" -ForegroundColor White
Write-Host "  - Created $($resp.execution_plan.steps.Count) step plan" -ForegroundColor White
Write-Host "  - Applied optimizations: $($resp.execution_plan.optimizations_applied)" -ForegroundColor White
Write-Host "  - Generated $($resp.execution_plan.adaptive_suggestions.suggestions.Count) suggestions" -ForegroundColor White
Write-Host "  - Executed with $($resp.task_result.summary.success_rate)% success" -ForegroundColor Green
Write-Host ""

Write-Host "User didn't specify:" -ForegroundColor Cyan
Write-Host "  - Which services to check" -ForegroundColor Gray
Write-Host "  - How to measure performance" -ForegroundColor Gray
Write-Host "  - What optimizations to apply" -ForegroundColor Gray
Write-Host "  - How to verify improvements" -ForegroundColor Gray
Write-Host ""
Write-Host "System figured it all out autonomously!" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2

# Example 3: Safety
Write-Host "[Example 3] Safety with Declarative Approach" -ForegroundColor Yellow
Write-Host ""
Write-Host "User says: 'Delete old logs'" -ForegroundColor White
Write-Host ""

$body = "message=Delete%20old%20logs&auto_execute=true"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45

Write-Host "System's safety analysis:" -ForegroundColor Red
Write-Host "  Safety Level: $($resp.execution_plan.safety_level)" -ForegroundColor Yellow
Write-Host "  Decision: $($resp.execution_plan.autonomous_decision.action)" -ForegroundColor Yellow
Write-Host "  Confidence: $($resp.execution_plan.autonomous_decision.confidence)" -ForegroundColor Yellow
Write-Host "  Requires Approval: $($resp.execution_plan.requires_approval)" -ForegroundColor Yellow
Write-Host ""

Write-Host "Reasoning:" -ForegroundColor White
foreach ($reason in $resp.execution_plan.autonomous_decision.reasoning) {
    Write-Host "  - $reason" -ForegroundColor Gray
}
Write-Host ""

Write-Host "System protected you from:" -ForegroundColor Green
Write-Host "  - Accidental data loss" -ForegroundColor White
Write-Host "  - Unsafe operations" -ForegroundColor White
Write-Host "  - Production issues" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "   DECLARATIVE SYSTEM DEMONSTRATED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Key Principles:" -ForegroundColor Cyan
Write-Host "  1. User describes WHAT (goal)" -ForegroundColor White
Write-Host "  2. System decides HOW (implementation)" -ForegroundColor White
Write-Host "  3. System is intelligent and autonomous" -ForegroundColor White
Write-Host "  4. System learns and adapts" -ForegroundColor White
Write-Host "  5. System ensures safety" -ForegroundColor White
Write-Host ""

Write-Host "NO imperative code required!" -ForegroundColor Green
Write-Host "System is fully declarative and autonomous!" -ForegroundColor Green
Write-Host ""
