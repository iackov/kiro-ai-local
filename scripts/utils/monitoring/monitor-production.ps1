# Production Monitoring Script
# Continuous monitoring of system health and performance

param(
    [int]$IntervalSeconds = 10,
    [int]$Duration = 60
)

$baseUrl = "http://localhost:9000"
$iterations = [math]::Floor($Duration / $IntervalSeconds)

Write-Host "=== PRODUCTION MONITORING ===" -ForegroundColor Cyan
Write-Host "Monitoring for $Duration seconds (checking every $IntervalSeconds seconds)" -ForegroundColor White
Write-Host ""

$healthHistory = @()

for ($i = 1; $i -le $iterations; $i++) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] Check $i/$iterations..." -NoNewline
    
    try {
        $metrics = Invoke-RestMethod -Uri "$baseUrl/api/production/metrics" -TimeoutSec 10
        
        $health = $metrics.health.score
        $status = $metrics.health.status
        $requests = $metrics.performance.total_requests
        $rate = $metrics.performance.request_rate_per_second
        $errors = $metrics.performance.error_count
        $autoActions = $metrics.autonomy.auto_actions_taken
        
        $healthHistory += $health
        
        # Color based on health
        $color = "Green"
        if ($health -lt 80) { $color = "Yellow" }
        if ($health -lt 50) { $color = "Red" }
        
        Write-Host " Health: $health/100" -ForegroundColor $color -NoNewline
        Write-Host " | Requests: $requests" -NoNewline
        Write-Host " | Rate: $rate/s" -NoNewline
        Write-Host " | Errors: $errors" -NoNewline
        Write-Host " | Auto-Actions: $autoActions" -ForegroundColor Cyan
        
        # Alert on issues
        if ($metrics.issues.Count -gt 0) {
            Write-Host "  [!] Issues detected:" -ForegroundColor Yellow
            foreach ($issue in $metrics.issues) {
                Write-Host "    - $($issue.service): $($issue.metric) = $($issue.value)" -ForegroundColor Yellow
            }
        }
        
        # Show auto-healing opportunities
        $opps = Invoke-RestMethod -Uri "$baseUrl/api/auto/opportunities" -TimeoutSec 5
        if ($opps.total -gt 0) {
            Write-Host "  [AUTO] $($opps.total) healing opportunities detected" -ForegroundColor Cyan
        }
        
    } catch {
        Write-Host " [ERROR] $($_.Exception.Message)" -ForegroundColor Red
        $healthHistory += 0
    }
    
    if ($i -lt $iterations) {
        Start-Sleep -Seconds $IntervalSeconds
    }
}

Write-Host ""
Write-Host "=== MONITORING SUMMARY ===" -ForegroundColor Cyan

if ($healthHistory.Count -gt 0) {
    $avgHealth = ($healthHistory | Measure-Object -Average).Average
    $minHealth = ($healthHistory | Measure-Object -Minimum).Minimum
    $maxHealth = ($healthHistory | Measure-Object -Maximum).Maximum
    
    Write-Host "Health Score:" -ForegroundColor White
    Write-Host "  Average: $([math]::Round($avgHealth, 1))/100" -ForegroundColor Green
    Write-Host "  Min: $minHealth/100" -ForegroundColor Yellow
    Write-Host "  Max: $maxHealth/100" -ForegroundColor Green
    
    # Stability check
    $healthVariance = 0
    if ($healthHistory.Count -gt 1) {
        $avg = ($healthHistory | Measure-Object -Average).Average
        $sumSquares = 0
        foreach ($h in $healthHistory) {
            $sumSquares += [math]::Pow($h - $avg, 2)
        }
        $healthVariance = [math]::Sqrt($sumSquares / $healthHistory.Count)
    }
    
    if ($healthVariance -lt 5) {
        Write-Host "  Stability: Excellent (variance: $([math]::Round($healthVariance, 1)))" -ForegroundColor Green
    } elseif ($healthVariance -lt 15) {
        Write-Host "  Stability: Good (variance: $([math]::Round($healthVariance, 1)))" -ForegroundColor Yellow
    } else {
        Write-Host "  Stability: Unstable (variance: $([math]::Round($healthVariance, 1)))" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Monitoring complete." -ForegroundColor Cyan
