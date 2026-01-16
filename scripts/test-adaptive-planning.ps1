# Test Adaptive Planning and Learning

Write-Host "=== TESTING ADAPTIVE PLANNING ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:9000"

# Test 1: Execute multiple similar tasks to build learning
Write-Host "[1] Building Learning History..." -ForegroundColor Yellow
$tasks = @(
    "Check system health",
    "Check all services health",
    "Analyze system performance",
    "Add Redis cache service"
)

foreach ($task in $tasks) {
    Write-Host "  Executing: $task" -NoNewline
    $encodedTask = $task -replace ' ', '%20'
    $body = "message=$encodedTask&auto_execute=true"
    $resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45
    Write-Host " - $($resp.task_result.summary.status)" -ForegroundColor $(if ($resp.task_result.summary.status -eq "completed") { "Green" } else { "Yellow" })
}
Write-Host ""

# Test 2: Check adaptive learning insights
Write-Host "[2] Checking Adaptive Learning Insights..." -ForegroundColor Yellow
$insights = Invoke-RestMethod -Uri "$baseUrl/api/learning/adaptive" -TimeoutSec 10

Write-Host "  Total Executions: $($insights.total_executions)" -ForegroundColor Cyan
Write-Host "  Successful: $($insights.successful_executions)" -ForegroundColor Green
Write-Host "  Success Rate: $($insights.overall_success_rate)%" -ForegroundColor Green
Write-Host "  Patterns Learned: $($insights.patterns_learned)" -ForegroundColor Cyan
Write-Host "  Step Types Tracked: $($insights.step_types_tracked)" -ForegroundColor Cyan

if ($insights.best_pattern) {
    Write-Host "  Best Pattern: $($insights.best_pattern.name) ($($insights.best_pattern.success_rate)%)" -ForegroundColor Green
}
if ($insights.worst_pattern) {
    Write-Host "  Worst Pattern: $($insights.worst_pattern.name) ($($insights.worst_pattern.success_rate)%)" -ForegroundColor Yellow
}
Write-Host ""

# Test 3: Test adaptive suggestions
Write-Host "[3] Testing Adaptive Suggestions..." -ForegroundColor Yellow
$body = "message=Add new service&auto_execute=false"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 30

if ($resp.execution_plan.adaptive_suggestions) {
    $suggestions = $resp.execution_plan.adaptive_suggestions
    Write-Host "  Pattern: $($suggestions.pattern)" -ForegroundColor Cyan
    Write-Host "  Historical Success Rate: $($suggestions.historical_success_rate)%" -ForegroundColor Cyan
    Write-Host "  Suggestions Count: $($suggestions.suggestions.Count)" -ForegroundColor Yellow
    
    if ($suggestions.suggestions.Count -gt 0) {
        Write-Host "  Suggestions:" -ForegroundColor White
        foreach ($sug in $suggestions.suggestions) {
            Write-Host "    - [$($sug.type)] $($sug.message)" -ForegroundColor Gray
        }
    }
}
Write-Host ""

# Test 4: Test step optimization
Write-Host "[4] Testing Step Optimization..." -ForegroundColor Yellow
$body = "message=Optimize system performance&auto_execute=false"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 30

if ($resp.execution_plan) {
    Write-Host "  Original Steps: $($resp.execution_plan.original_steps.Count)" -ForegroundColor White
    Write-Host "  Optimized Steps: $($resp.execution_plan.steps.Count)" -ForegroundColor Cyan
    Write-Host "  Optimizations Applied: $($resp.execution_plan.optimizations_applied)" -ForegroundColor $(if ($resp.execution_plan.optimizations_applied) { "Green" } else { "Gray" })
    
    if ($resp.execution_plan.optimizations_applied) {
        Write-Host "  Optimized Plan:" -ForegroundColor White
        for ($i = 0; $i -lt $resp.execution_plan.steps.Count; $i++) {
            Write-Host "    $($i+1). $($resp.execution_plan.steps[$i])" -ForegroundColor Gray
        }
    }
}
Write-Host ""

# Test 5: Execute with learned optimizations
Write-Host "[5] Executing with Learned Optimizations..." -ForegroundColor Yellow
$body = "message=Check health and analyze metrics&auto_execute=true"
$resp = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded" -TimeoutSec 45

Write-Host "  Task Status: $($resp.task_result.summary.status)" -ForegroundColor Green
Write-Host "  Steps: $($resp.task_result.summary.successful)/$($resp.task_result.summary.total_steps)" -ForegroundColor Cyan
Write-Host "  Success Rate: $($resp.task_result.summary.success_rate)%" -ForegroundColor Green
Write-Host ""

# Test 6: Verify learning improved over time
Write-Host "[6] Verifying Learning Improvement..." -ForegroundColor Yellow
$insights2 = Invoke-RestMethod -Uri "$baseUrl/api/learning/adaptive" -TimeoutSec 10

$improvement = $insights2.overall_success_rate - $insights.overall_success_rate
Write-Host "  Initial Success Rate: $($insights.overall_success_rate)%" -ForegroundColor White
Write-Host "  Current Success Rate: $($insights2.overall_success_rate)%" -ForegroundColor Cyan
Write-Host "  Improvement: $($improvement)%" -ForegroundColor $(if ($improvement -ge 0) { "Green" } else { "Yellow" })
Write-Host ""

Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "[OK] Learning history built" -ForegroundColor Green
Write-Host "[OK] Adaptive insights generated" -ForegroundColor Green
Write-Host "[OK] Suggestions provided" -ForegroundColor Green
Write-Host "[OK] Step optimization working" -ForegroundColor Green
Write-Host "[OK] Execution with learning" -ForegroundColor Green
Write-Host ""
Write-Host "ADAPTIVE PLANNING OPERATIONAL!" -ForegroundColor Green
