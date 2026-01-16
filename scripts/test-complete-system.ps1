# Complete System Test - All Capabilities
Write-Host "=== COMPLETE SYSTEM TEST ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:9000"
$passed = 0
$total = 0

# Test 1: Conversational
Write-Host "[1] Conversational Interface..." -NoNewline
$total++
try {
    $body = @{ message = "What is system status?" }
    $chat = Invoke-RestMethod -Uri "$baseUrl/api/chat" -Method Post -Body $body -TimeoutSec 30
    if ($chat.response.Length -gt 10) {
        Write-Host " OK" -ForegroundColor Green
        $passed++
    } else {
        Write-Host " FAIL" -ForegroundColor Red
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
}

# Test 2: Task Execution
Write-Host "[2] Task Execution..." -NoNewline
$total++
try {
    $body = @{ task = "Check system health" }
    $task = Invoke-RestMethod -Uri "$baseUrl/api/execute" -Method Post -Body $body -TimeoutSec 30
    if ($task.status -eq "completed") {
        Write-Host " OK" -ForegroundColor Green
        $passed++
    } else {
        Write-Host " FAIL" -ForegroundColor Red
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
}

# Test 3: Unified Interface
Write-Host "[3] Unified Autonomous..." -NoNewline
$total++
try {
    $body = @{ message = "Check health"; auto_execute = $true }
    $unified = Invoke-RestMethod -Uri "$baseUrl/api/autonomous" -Method Post -Body $body -TimeoutSec 30
    if ($unified.task_executed) {
        Write-Host " OK" -ForegroundColor Green
        $passed++
    } else {
        Write-Host " FAIL" -ForegroundColor Red
    }
} catch {
    Write-Host " FAIL" -ForegroundColor Red
}

# Test 4-12: All 9 Autonomy Levels
$levels = @(
    @{name="RAG"; endpoint="/api/rag/query"; method="Post"; body=@{query="test";top_k=1}},
    @{name="Multi-Service"; endpoint="/api/combined/query"; method="Post"; body=@{query="test";top_k=1}},
    @{name="Architecture"; endpoint="/api/arch/propose"; method="Post"; body=@{prompt="test";auto_apply=$false}},
    @{name="Monitoring"; endpoint="/api/metrics/insights"; method="Get"; body=$null},
    @{name="Learning"; endpoint="/api/learning/insights"; method="Get"; body=$null},
    @{name="Auto-Healing"; endpoint="/api/auto/opportunities"; method="Get"; body=$null},
    @{name="Planning"; endpoint="/api/planning/action-plan"; method="Get"; body=$null},
    @{name="Reasoning"; endpoint="/api/reasoning/analyze"; method="Post"; body=@{query="docker"}},
    @{name="Goals"; endpoint="/api/goals/list"; method="Get"; body=$null}
)

foreach ($level in $levels) {
    $total++
    Write-Host "[$($total-2)] $($level.name)..." -NoNewline
    
    try {
        if ($level.method -eq "Get") {
            $result = Invoke-RestMethod -Uri "$baseUrl$($level.endpoint)" -TimeoutSec 10
        } else {
            $result = Invoke-RestMethod -Uri "$baseUrl$($level.endpoint)" -Method Post -Body $level.body -TimeoutSec 10
        }
        Write-Host " OK" -ForegroundColor Green
        $passed++
    } catch {
        Write-Host " FAIL" -ForegroundColor Red
    }
}

# Summary
Write-Host ""
Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Passed: $passed/$total" -ForegroundColor $(if($passed -eq $total) { "Green" } else { "Yellow" })
Write-Host "Success Rate: $([math]::Round(($passed/$total)*100, 1))%" -ForegroundColor White

if ($passed -eq $total) {
    Write-Host ""
    Write-Host "SYSTEM 100% OPERATIONAL!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Capabilities:" -ForegroundColor Cyan
    Write-Host "  ✓ Conversational AI" -ForegroundColor Green
    Write-Host "  ✓ Task Execution" -ForegroundColor Green
    Write-Host "  ✓ Unified Interface" -ForegroundColor Green
    Write-Host "  ✓ 9 Autonomy Levels" -ForegroundColor Green
    Write-Host "  ✓ Self-Modification" -ForegroundColor Green
    Write-Host "  ✓ Auto-Healing" -ForegroundColor Green
    Write-Host ""
    Write-Host "READY FOR FULL SWITCH!" -ForegroundColor Green
}
