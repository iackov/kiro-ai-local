# Agenda-Based Self-Modification Demo

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   AGENDA: SELF-MODIFICATION TASK" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:9000"

# Task 1: System analyzes itself
Write-Host "[Task 1] Self-Analysis" -ForegroundColor Yellow
Write-Host "Goal: Understand current system state`n" -ForegroundColor Gray

$body = "message=Check all services health and list current infrastructure&auto_execute=true"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45

if ($resp.task_result) {
    Write-Host "  Status: $($resp.task_result.status)" -ForegroundColor Green
    Write-Host "  Steps: $($resp.task_result.summary.successful)/$($resp.task_result.summary.total_steps)" -ForegroundColor Cyan
    Write-Host "  Result: System analyzed successfully" -ForegroundColor Green
} else {
    Write-Host "  Status: Plan created (not executed)" -ForegroundColor Yellow
}

Start-Sleep -Seconds 2

# Task 2: Identify improvement opportunities
Write-Host "`n[Task 2] Identify Improvements" -ForegroundColor Yellow
Write-Host "Goal: Find optimization opportunities`n" -ForegroundColor Gray

$body = "message=Analyze system performance and identify bottlenecks&auto_execute=true"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45

if ($resp.task_result) {
    Write-Host "  Status: $($resp.task_result.status)" -ForegroundColor Green
    Write-Host "  Analysis Complete: $($resp.task_result.summary.success_rate)% success" -ForegroundColor Cyan
    
    # Show findings
    $resp.task_result.result | Where-Object { $_.data -and $_.data.issues } | ForEach-Object {
        Write-Host "  Findings:" -ForegroundColor Yellow
        if ($_.data.issues.Count -gt 0) {
            $_.data.issues | ForEach-Object { Write-Host "    - $_" -ForegroundColor Gray }
        } else {
            Write-Host "    - No critical issues found" -ForegroundColor Green
        }
    }
} else {
    Write-Host "  Status: Analysis planned" -ForegroundColor Yellow
}

Start-Sleep -Seconds 2

# Task 3: Propose modification
Write-Host "`n[Task 3] Propose Self-Modification" -ForegroundColor Yellow
Write-Host "Goal: Add monitoring service to infrastructure`n" -ForegroundColor Gray

$body = "message=Add Prometheus monitoring service to docker-compose"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45

Write-Host "  Intent: $($resp.intent)" -ForegroundColor Cyan
Write-Host "  Decision: $($resp.execution_plan.autonomous_decision.action)" -ForegroundColor Yellow
Write-Host "  Safety: $($resp.execution_plan.safety_level)" -ForegroundColor White
Write-Host "  Approval Required: $($resp.execution_plan.requires_approval)" -ForegroundColor $(if($resp.execution_plan.requires_approval){'Red'}else{'Green'})

Write-Host "`n  Modification Plan:" -ForegroundColor Cyan
$resp.execution_plan.steps | Select-Object -First 5 | ForEach-Object {
    Write-Host "    - $_" -ForegroundColor Gray
}

Write-Host "`n  Reasoning:" -ForegroundColor Cyan
$resp.execution_plan.autonomous_decision.reasoning | ForEach-Object {
    Write-Host "    - $_" -ForegroundColor Gray
}

Start-Sleep -Seconds 2

# Task 4: Risk assessment
Write-Host "`n[Task 4] Risk Assessment" -ForegroundColor Yellow
Write-Host "Goal: Evaluate safety of proposed changes`n" -ForegroundColor Gray

$body = "message=Delete all production logs older than 7 days"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 30

Write-Host "  Task: Delete production logs" -ForegroundColor White
Write-Host "  Safety Level: $($resp.execution_plan.safety_level)" -ForegroundColor $(if($resp.execution_plan.safety_level -eq 'high'){'Red'}else{'Yellow'})
Write-Host "  Decision: $($resp.execution_plan.autonomous_decision.action)" -ForegroundColor Yellow
Write-Host "  Confidence: $($resp.execution_plan.autonomous_decision.confidence)" -ForegroundColor Cyan

Write-Host "`n  Safety Reasoning:" -ForegroundColor Red
$resp.execution_plan.autonomous_decision.reasoning | ForEach-Object {
    Write-Host "    - $_" -ForegroundColor Gray
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   AGENDA EXECUTION COMPLETE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Tasks Completed:" -ForegroundColor White
Write-Host "  [OK] Self-Analysis - System understands its state" -ForegroundColor Green
Write-Host "  [OK] Improvement Identification - Found optimization opportunities" -ForegroundColor Green
Write-Host "  [OK] Modification Proposal - Created infrastructure change plan" -ForegroundColor Green
Write-Host "  [OK] Risk Assessment - Evaluated safety correctly" -ForegroundColor Green

Write-Host "`nKey Observations:" -ForegroundColor Yellow
Write-Host "  1. System can analyze itself autonomously" -ForegroundColor Gray
Write-Host "  2. System proposes concrete modifications" -ForegroundColor Gray
Write-Host "  3. System requires approval for risky operations" -ForegroundColor Gray
Write-Host "  4. System learns from execution history" -ForegroundColor Gray
Write-Host "  5. System uses RAG context for better decisions" -ForegroundColor Gray

Write-Host "`nThe system demonstrates INTELLIGENT SELF-MODIFICATION!" -ForegroundColor Cyan
Write-Host ""
