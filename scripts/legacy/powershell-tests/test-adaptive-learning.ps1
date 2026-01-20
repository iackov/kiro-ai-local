# Test Adaptive Learning System
Write-Host "=== Testing Adaptive Learning System ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Generate baseline data
Write-Host "[Step 1] Generating baseline queries..." -ForegroundColor Yellow
for($i=1; $i -le 30; $i++) {
    $queries = @("Docker optimization", "Redis setup", "Docker compose", "Redis cache", "Docker networking")
    $q = $queries[$i % $queries.Count]
    $body = @{ query = $q; top_k = 3 }
    Invoke-RestMethod -Uri "http://localhost:9000/api/rag/query" -Method Post -Body $body -TimeoutSec 30 | Out-Null
    Write-Host "." -NoNewline
}
Write-Host " Done!" -ForegroundColor Green

# Step 2: Check initial suggestions
Write-Host "`n[Step 2] Checking initial suggestions..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
$analysis1 = Invoke-RestMethod -Uri "http://localhost:9000/api/metrics/analysis"
Write-Host "Suggestions: $($analysis1.suggestions.Count)" -ForegroundColor Cyan
Write-Host "Learning applied: $($analysis1.learning_applied)" -ForegroundColor Cyan

if($analysis1.suggestions.Count -gt 0) {
    Write-Host "`nInitial suggestions:" -ForegroundColor Yellow
    $analysis1.suggestions | ForEach-Object {
        Write-Host "  [$($_.priority)] $($_.issue)" -ForegroundColor White
    }
}

# Step 3: Apply a suggestion
Write-Host "`n[Step 3] Applying Redis suggestion..." -ForegroundColor Yellow
$body = @{ suggestion_action = "Add Redis cache service" }
try {
    $result = Invoke-RestMethod -Uri "http://localhost:9000/api/auto/apply-suggestion" -Method Post -Body $body -TimeoutSec 30
    Write-Host "Status: $($result.status)" -ForegroundColor Green
} catch {
    Write-Host "Note: Redis might already exist" -ForegroundColor Yellow
}

# Step 4: Dismiss a suggestion
Write-Host "`n[Step 4] Dismissing Grafana suggestion..." -ForegroundColor Yellow
$body2 = @{ suggestion_action = "Add Grafana monitoring" }
$result2 = Invoke-RestMethod -Uri "http://localhost:9000/api/auto/dismiss-suggestion" -Method Post -Body $body2
Write-Host "Status: $($result2.status)" -ForegroundColor Green

# Step 5: Check learning
Write-Host "`n[Step 5] Checking learning data..." -ForegroundColor Yellow
$learning = Invoke-RestMethod -Uri "http://localhost:9000/api/learning/insights"
Write-Host "Total suggestions: $($learning.total_suggestions)" -ForegroundColor Cyan
Write-Host "Applied: $($learning.applied_count)" -ForegroundColor Green
Write-Host "Dismissed: $($learning.dismissed_count)" -ForegroundColor Red
Write-Host "Acceptance rate: $([math]::Round($learning.acceptance_rate * 100, 1))%" -ForegroundColor Cyan

if($learning.insights.Count -gt 0) {
    Write-Host "`nLearning insights:" -ForegroundColor Yellow
    $learning.insights | ForEach-Object {
        Write-Host "  🧠 $_" -ForegroundColor White
    }
}

# Step 6: Generate more queries to trigger adapted suggestions
Write-Host "`n[Step 6] Generating more queries..." -ForegroundColor Yellow
for($i=1; $i -le 20; $i++) {
    $queries = @("Redis performance", "Redis cluster", "Redis backup")
    $q = $queries[$i % $queries.Count]
    $body = @{ query = $q; top_k = 3 }
    Invoke-RestMethod -Uri "http://localhost:9000/api/rag/query" -Method Post -Body $body -TimeoutSec 30 | Out-Null
    Write-Host "." -NoNewline
}
Write-Host " Done!" -ForegroundColor Green

# Step 7: Check adapted suggestions
Write-Host "`n[Step 7] Checking adapted suggestions..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
$analysis2 = Invoke-RestMethod -Uri "http://localhost:9000/api/metrics/analysis"
Write-Host "Suggestions: $($analysis2.suggestions.Count)" -ForegroundColor Cyan
Write-Host "Learning applied: $($analysis2.learning_applied)" -ForegroundColor Cyan

if($analysis2.suggestions.Count -gt 0) {
    Write-Host "`nAdapted suggestions:" -ForegroundColor Yellow
    $analysis2.suggestions | ForEach-Object {
        $badge = if($_.learning_adjusted) { "[🧠 Adapted]" } else { "" }
        Write-Host "  [$($_.priority)] $($_.issue) $badge" -ForegroundColor White
    }
}

# Step 8: Compare before/after
Write-Host "`n[Step 8] Adaptation Analysis:" -ForegroundColor Yellow
Write-Host "Before learning:" -ForegroundColor White
Write-Host "  - Suggestions: $($analysis1.suggestions.Count)" -ForegroundColor Gray
Write-Host "  - Learning applied: $($analysis1.learning_applied)" -ForegroundColor Gray

Write-Host "After learning:" -ForegroundColor White
Write-Host "  - Suggestions: $($analysis2.suggestions.Count)" -ForegroundColor Gray
Write-Host "  - Learning applied: $($analysis2.learning_applied)" -ForegroundColor Gray

if($analysis2.learning_applied) {
    Write-Host "`n✅ System is adapting based on user preferences!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  No adaptation detected yet (need more data)" -ForegroundColor Yellow
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
