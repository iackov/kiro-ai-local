# Stress Test - Load testing all autonomy levels
Write-Host "=== STRESS TEST - FULL AUTONOMY STACK ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:9000"
$iterations = 20
$results = @()

Write-Host "[Phase 1] Load Testing - $iterations iterations" -ForegroundColor Yellow
Write-Host ""

for ($i = 1; $i -le $iterations; $i++) {
    Write-Host "Iteration $i/$iterations..." -NoNewline
    
    $start = Get-Date
    
    try {
        # RAG query
        $body1 = @{ query = "docker service $i"; top_k = 3 }
        $rag = Invoke-RestMethod -Uri "$baseUrl/api/rag/query" -Method Post -Body $body1 -TimeoutSec 30
        
        # Combined query
        $body2 = @{ query = "add redis cache"; top_k = 2 }
        $combined = Invoke-RestMethod -Uri "$baseUrl/api/combined/query" -Method Post -Body $body2 -TimeoutSec 30
        
        # Metrics check
        $metrics = Invoke-RestMethod -Uri "$baseUrl/api/metrics/insights" -TimeoutSec 30
        
        $elapsed = ((Get-Date) - $start).TotalMilliseconds
        $results += [PSCustomObject]@{ iteration = $i; success = $true; latency = $elapsed }
        
        Write-Host " OK ($([math]::Round($elapsed, 0))ms)" -ForegroundColor Green
    }
    catch {
        $elapsed = ((Get-Date) - $start).TotalMilliseconds
        $results += [PSCustomObject]@{ iteration = $i; success = $false; latency = $elapsed; error = $_.Exception.Message }
        Write-Host " FAIL" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 100
}

Write-Host ""
Write-Host "[Phase 2] Analyzing Results..." -ForegroundColor Yellow

$successful = ($results | Where-Object { $_.success -eq $true }).Count
$failed = ($results | Where-Object { $_.success -eq $false }).Count
$avgLatency = ($results | Where-Object { $_.success -eq $true } | Measure-Object -Property latency -Average).Average
$maxLatency = ($results | Where-Object { $_.success -eq $true } | Measure-Object -Property latency -Maximum).Maximum
$minLatency = ($results | Where-Object { $_.success -eq $true } | Measure-Object -Property latency -Minimum).Minimum

Write-Host ""
Write-Host "=== RESULTS ===" -ForegroundColor Cyan
Write-Host "Total Requests: $iterations" -ForegroundColor White
Write-Host "Successful: $successful" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor $(if($failed -eq 0) { "Green" } else { "Red" })
Write-Host "Success Rate: $([math]::Round(($successful/$iterations)*100, 1))%" -ForegroundColor $(if($successful -eq $iterations) { "Green" } else { "Yellow" })
Write-Host ""
Write-Host "Latency Stats:" -ForegroundColor White
Write-Host "  Average: $([math]::Round($avgLatency, 0))ms" -ForegroundColor Cyan
Write-Host "  Min: $([math]::Round($minLatency, 0))ms" -ForegroundColor Green
Write-Host "  Max: $([math]::Round($maxLatency, 0))ms" -ForegroundColor Yellow

Write-Host ""
Write-Host "[Phase 3] Checking Auto-Healing..." -ForegroundColor Yellow
$opps = Invoke-RestMethod -Uri "$baseUrl/api/auto/opportunities" -TimeoutSec 30
Write-Host "Auto-healing opportunities: $($opps.total)" -ForegroundColor Cyan
Write-Host "Auto-actions taken: $($opps.auto_actions_taken)" -ForegroundColor Cyan

Write-Host ""
Write-Host "[Phase 4] Final Health Check..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "$baseUrl/api/metrics/health" -TimeoutSec 30
Write-Host "Health Score: $($health.health_score)/100" -ForegroundColor $(if($health.health_score -gt 80) { "Green" } elseif($health.health_score -gt 50) { "Yellow" } else { "Red" })
Write-Host "Status: $($health.status)" -ForegroundColor $(if($health.status -eq "healthy") { "Green" } else { "Yellow" })

Write-Host ""
if ($successful -eq $iterations -and $health.health_score -gt 80) {
    Write-Host "STRESS TEST PASSED - System is stable under load!" -ForegroundColor Green
} else {
    Write-Host "STRESS TEST COMPLETED - Some issues detected" -ForegroundColor Yellow
}
