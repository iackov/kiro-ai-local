# Full Autonomy Test - All 6 Levels
# Tests complete autonomous operation chain

Write-Host "=== FULL AUTONOMY TEST - 6 LEVELS ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:9000"
$results = @()

# Level 1: Basic RAG Query
Write-Host "[Level 1] Testing Basic RAG..." -ForegroundColor Yellow
try {
    $body = @{ query = "docker compose"; top_k = 3 }
    $response = Invoke-RestMethod -Uri "$baseUrl/api/rag/query" -Method Post -Body $body -TimeoutSec 30
    $results += @{ level = 1; status = "OK"; latency = $response.latency_ms }
    Write-Host "  [OK] RAG working ($([math]::Round($response.latency_ms, 0))ms)" -ForegroundColor Green
} catch {
    $results += @{ level = 1; status = "FAIL"; error = $_.Exception.Message }
    Write-Host "  [FAIL] Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Level 2: Multi-Service Orchestration
Write-Host "[Level 2] Testing Multi-Service..." -ForegroundColor Yellow
try {
    $body = @{ query = "how to add redis service"; top_k = 3 }
    $response = Invoke-RestMethod -Uri "$baseUrl/api/combined/query" -Method Post -Body $body -TimeoutSec 30
    $results += @{ level = 2; status = "OK"; services = $response.services_used.Count }
    Write-Host "  [OK] Combined query ($($response.services_used.Count) services)" -ForegroundColor Green
} catch {
    $results += @{ level = 2; status = "FAIL"; error = $_.Exception.Message }
    Write-Host "  [FAIL] Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Level 3: Architecture Engine
Write-Host "[Level 3] Testing Architecture Engine..." -ForegroundColor Yellow
try {
    $body = @{ prompt = "Add test service with 512M memory"; auto_apply = $false }
    $response = Invoke-RestMethod -Uri "$baseUrl/api/arch/propose" -Method Post -Body $body -TimeoutSec 30
    $results += @{ level = 3; status = "OK"; safe = $response.safe }
    Write-Host "  [OK] Architecture proposal (safe: $($response.safe))" -ForegroundColor Green
} catch {
    $results += @{ level = 3; status = "FAIL"; error = $_.Exception.Message }
    Write-Host "  [FAIL] Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Level 4: Metrics & Insights
Write-Host "[Level 4] Testing Metrics..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/metrics/insights" -TimeoutSec 30
    $results += @{ level = 4; status = "OK"; insights = $response.insights.Count }
    Write-Host "  [OK] Metrics insights ($($response.insights.Count) insights)" -ForegroundColor Green
} catch {
    $results += @{ level = 4; status = "FAIL"; error = $_.Exception.Message }
    Write-Host "  [FAIL] Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Level 5: Adaptive Learning
Write-Host "[Level 5] Testing Adaptive Learning..." -ForegroundColor Yellow
try {
    # Record preference
    $body = @{ suggestion_id = "test_suggestion"; action = "applied" }
    Invoke-RestMethod -Uri "$baseUrl/api/learning/feedback" -Method Post -Body $body -TimeoutSec 30 | Out-Null
    
    # Get insights
    $response = Invoke-RestMethod -Uri "$baseUrl/api/learning/insights" -TimeoutSec 30
    $results += @{ level = 5; status = "OK"; preferences = $response.user_preferences.applied_suggestions.Count }
    Write-Host "  [OK] Learning active ($($response.user_preferences.applied_suggestions.Count) preferences)" -ForegroundColor Green
} catch {
    $results += @{ level = 5; status = "FAIL"; error = $_.Exception.Message }
    Write-Host "  [FAIL] Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Level 6: Auto-Healing
Write-Host "[Level 6] Testing Auto-Healing..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/auto/opportunities" -TimeoutSec 30
    $results += @{ level = 6; status = "OK"; opportunities = $response.total; actions = $response.auto_actions_taken }
    Write-Host "  [OK] Auto-healing ready ($($response.auto_actions_taken) actions taken)" -ForegroundColor Green
} catch {
    $results += @{ level = 6; status = "FAIL"; error = $_.Exception.Message }
    Write-Host "  [FAIL] Failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
$passed = ($results | Where-Object { $_.status -eq "OK" }).Count
$total = $results.Count
Write-Host "Passed: $passed/$total levels" -ForegroundColor $(if($passed -eq $total) { "Green" } else { "Yellow" })

if ($passed -eq $total) {
    Write-Host ""
    Write-Host "🎉 FULL AUTONOMY ACHIEVED! All 6 levels operational!" -ForegroundColor Green
}
