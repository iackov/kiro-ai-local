# Test All 9 Autonomy Levels
Write-Host "=== TESTING 9 AUTONOMY LEVELS ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:9000"
$results = @()

# Level 1: Basic RAG
Write-Host "[Level 1] Basic RAG..." -NoNewline
try {
    $body = @{ query = "docker"; top_k = 2 }
    $resp = Invoke-RestMethod -Uri "$baseUrl/api/rag/query" -Method Post -Body $body -TimeoutSec 10
    Write-Host " OK" -ForegroundColor Green
    $results += "Level 1: OK"
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $results += "Level 1: FAIL"
}

# Level 2: Multi-Service
Write-Host "[Level 2] Multi-Service..." -NoNewline
try {
    $body = @{ query = "add service"; top_k = 2 }
    $resp = Invoke-RestMethod -Uri "$baseUrl/api/combined/query" -Method Post -Body $body -TimeoutSec 10
    Write-Host " OK ($($resp.services_used.Count) services)" -ForegroundColor Green
    $results += "Level 2: OK"
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $results += "Level 2: FAIL"
}

# Level 3: Architecture Engine
Write-Host "[Level 3] Architecture..." -NoNewline
try {
    $body = @{ prompt = "test"; auto_apply = $false }
    $resp = Invoke-RestMethod -Uri "$baseUrl/api/arch/propose" -Method Post -Body $body -TimeoutSec 10
    Write-Host " OK" -ForegroundColor Green
    $results += "Level 3: OK"
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $results += "Level 3: FAIL"
}

# Level 4: Self-Monitoring
Write-Host "[Level 4] Self-Monitoring..." -NoNewline
try {
    $resp = Invoke-RestMethod -Uri "$baseUrl/api/metrics/insights" -TimeoutSec 10
    Write-Host " OK (health: $($resp.health_score))" -ForegroundColor Green
    $results += "Level 4: OK"
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $results += "Level 4: FAIL"
}

# Level 5: Adaptive Learning
Write-Host "[Level 5] Adaptive Learning..." -NoNewline
try {
    $resp = Invoke-RestMethod -Uri "$baseUrl/api/learning/insights" -TimeoutSec 10
    Write-Host " OK" -ForegroundColor Green
    $results += "Level 5: OK"
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $results += "Level 5: FAIL"
}

# Level 6: Auto-Healing
Write-Host "[Level 6] Auto-Healing..." -NoNewline
try {
    $resp = Invoke-RestMethod -Uri "$baseUrl/api/auto/opportunities" -TimeoutSec 10
    Write-Host " OK" -ForegroundColor Green
    $results += "Level 6: OK"
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $results += "Level 6: FAIL"
}

# Level 7: Proactive Planning
Write-Host "[Level 7] Proactive Planning..." -NoNewline
try {
    $resp = Invoke-RestMethod -Uri "$baseUrl/api/planning/action-plan" -TimeoutSec 10
    Write-Host " OK" -ForegroundColor Green
    $results += "Level 7: OK"
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $results += "Level 7: FAIL"
}

# Level 8: Knowledge Graph Reasoning
Write-Host "[Level 8] Reasoning..." -NoNewline
try {
    $body = @{ query = "docker service memory" }
    $resp = Invoke-RestMethod -Uri "$baseUrl/api/reasoning/analyze" -Method Post -Body $body -TimeoutSec 10
    Write-Host " OK ($($resp.reasoning.concepts.Count) concepts)" -ForegroundColor Green
    $results += "Level 8: OK"
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $results += "Level 8: FAIL"
}

# Level 9: Goal-Oriented Behavior
Write-Host "[Level 9] Goal-Oriented..." -NoNewline
try {
    $resp = Invoke-RestMethod -Uri "$baseUrl/api/goals/list" -TimeoutSec 10
    Write-Host " OK ($($resp.total) goals)" -ForegroundColor Green
    $results += "Level 9: OK"
} catch {
    Write-Host " FAIL" -ForegroundColor Red
    $results += "Level 9: FAIL"
}

# Summary
Write-Host ""
Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
$passed = ($results | Where-Object { $_ -like "*OK*" }).Count
$total = $results.Count
Write-Host "Passed: $passed/$total levels" -ForegroundColor $(if($passed -eq $total) { "Green" } else { "Yellow" })

if ($passed -eq $total) {
    Write-Host ""
    Write-Host "ALL 9 AUTONOMY LEVELS OPERATIONAL!" -ForegroundColor Green
    Write-Host ""
    Write-Host "System Capabilities:" -ForegroundColor Cyan
    Write-Host "  [1] Basic RAG - Knowledge retrieval" -ForegroundColor White
    Write-Host "  [2] Multi-Service - Orchestration" -ForegroundColor White
    Write-Host "  [3] Architecture - Self-modification" -ForegroundColor White
    Write-Host "  [4] Self-Monitoring - Performance analysis" -ForegroundColor White
    Write-Host "  [5] Adaptive Learning - User preferences" -ForegroundColor White
    Write-Host "  [6] Auto-Healing - Self-repair" -ForegroundColor White
    Write-Host "  [7] Proactive Planning - Future prediction" -ForegroundColor White
    Write-Host "  [8] Reasoning - Concept understanding" -ForegroundColor White
    Write-Host "  [9] Goal-Oriented - Autonomous goal achievement" -ForegroundColor White
}
