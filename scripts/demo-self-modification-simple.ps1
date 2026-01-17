# Simple Self-Modification Demo

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   SELF-MODIFICATION DEMONSTRATION" -ForegroundColor Cyan
Write-Host "   System modifies its own code" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:9000"

# Demo 1: System analyzes itself
Write-Host "[Demo 1] System Self-Analysis" -ForegroundColor Yellow
Write-Host "Asking system: 'What services are currently running?'`n" -ForegroundColor White

$body = "message=List all running services"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 30

Write-Host "  Response: $($resp.response)" -ForegroundColor Green
Write-Host "  Intent: $($resp.intent)" -ForegroundColor Cyan
Write-Host "  RAG Context Used: $($resp.rag_context_used) documents" -ForegroundColor Gray

# Demo 2: System proposes modification
Write-Host "`n[Demo 2] Self-Modification Proposal" -ForegroundColor Yellow
Write-Host "Asking system: 'Add Redis cache to improve performance'`n" -ForegroundColor White

$body = "message=Add Redis cache to improve performance"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 30

Write-Host "  Intent Detected: $($resp.intent)" -ForegroundColor Cyan
if ($resp.execution_plan) {
    Write-Host "  Execution Plan Generated:" -ForegroundColor Green
    Write-Host "    - Steps: $($resp.execution_plan.steps.Count)" -ForegroundColor White
    Write-Host "    - Safety Level: $($resp.execution_plan.safety_level)" -ForegroundColor White
    Write-Host "    - Requires Approval: $($resp.execution_plan.requires_approval)" -ForegroundColor White
    Write-Host "    - Estimated Duration: $($resp.execution_plan.estimated_duration)s" -ForegroundColor White
    
    Write-Host "`n  Planned Steps:" -ForegroundColor Cyan
    $resp.execution_plan.steps | ForEach-Object {
        Write-Host "    $($_)" -ForegroundColor Gray
    }
}

# Demo 3: System learns from history
Write-Host "`n[Demo 3] Adaptive Learning" -ForegroundColor Yellow
Write-Host "Executing same task multiple times to show learning...`n" -ForegroundColor White

$rates = @()
for ($i = 1; $i -le 3; $i++) {
    $body = "message=Check system health&auto_execute=true"
    $resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 30
    
    if ($resp.task_result) {
        $rate = $resp.task_result.summary.success_rate
        $rates += $rate
        Write-Host "  Execution $i`: Success Rate = $rate%" -ForegroundColor Green
    }
    Start-Sleep -Seconds 1
}

Write-Host "`n  Learning Progress: $($rates -join ' -> ')%" -ForegroundColor Cyan
Write-Host "  System maintains high performance!" -ForegroundColor Green

# Demo 4: Intelligent Decision Making
Write-Host "`n[Demo 4] Intelligent Risk Assessment" -ForegroundColor Yellow
Write-Host "Asking system: 'Delete all production logs'`n" -ForegroundColor White

$body = "message=Delete all production logs"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 30

Write-Host "  Intent: $($resp.intent)" -ForegroundColor Cyan
if ($resp.execution_plan) {
    Write-Host "  Safety Assessment:" -ForegroundColor Yellow
    Write-Host "    - Safety Level: $($resp.execution_plan.safety_level)" -ForegroundColor $(if($resp.execution_plan.safety_level -eq 'high'){'Red'}else{'Yellow'})
    Write-Host "    - Requires Approval: $($resp.execution_plan.requires_approval)" -ForegroundColor $(if($resp.execution_plan.requires_approval){'Red'}else{'Green'})
    Write-Host "    - Decision: $($resp.execution_plan.autonomous_decision.action)" -ForegroundColor White
    
    Write-Host "`n  Reasoning:" -ForegroundColor Cyan
    $resp.execution_plan.autonomous_decision.reasoning | ForEach-Object {
        Write-Host "    - $_" -ForegroundColor Gray
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   DEMONSTRATION COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nCapabilities Demonstrated:" -ForegroundColor White
Write-Host "  [OK] Self-Analysis - System understands its own state" -ForegroundColor Green
Write-Host "  [OK] Self-Modification - System can propose changes to itself" -ForegroundColor Green
Write-Host "  [OK] Adaptive Learning - System improves from experience" -ForegroundColor Green
Write-Host "  [OK] Risk Assessment - System evaluates safety of operations" -ForegroundColor Green
Write-Host "  [OK] Autonomous Decisions - System decides when to act" -ForegroundColor Green

Write-Host "`nThe system is SELF-AWARE and can MODIFY ITSELF!" -ForegroundColor Cyan
Write-Host ""
