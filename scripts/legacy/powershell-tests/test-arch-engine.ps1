# Test Architecture Engine
param(
    [string]$Prompt = "Add Redis cache service"
)

Write-Host "=== Testing Architecture Engine ===" -ForegroundColor Cyan
Write-Host ""

# Check if arch-engine is running
Write-Host "[1] Checking Arch Engine status..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:9004/health" -Method Get
    Write-Host "  OK Arch Engine is running" -ForegroundColor Green
} catch {
    Write-Host "  X  Arch Engine not running" -ForegroundColor Red
    Write-Host "  Run: docker compose up -d arch-engine" -ForegroundColor Yellow
    exit 1
}

# Test propose endpoint
Write-Host ""
Write-Host "[2] Proposing architecture change..." -ForegroundColor Yellow
Write-Host "  Prompt: $Prompt" -ForegroundColor Gray

$body = @{
    prompt = $Prompt
    auto_apply = $false
} | ConvertTo-Json

try {
    $proposal = Invoke-RestMethod -Uri "http://localhost:9004/arch/propose" `
        -Method Post `
        -Body $body `
        -ContentType "application/json"
    
    Write-Host "  OK Proposal generated" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Change ID: $($proposal.change_id)" -ForegroundColor Cyan
    Write-Host "  Intent: $($proposal.intent.action) $($proposal.intent.type)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Diff:" -ForegroundColor Yellow
    Write-Host $proposal.diff -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Preview:" -ForegroundColor Yellow
    Write-Host $proposal.preview -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Safety Checks:" -ForegroundColor Yellow
    foreach ($check in $proposal.safety_checks) {
        $status = if ($check.passed) { "[OK]" } else { "[FAIL]" }
        $color = if ($check.passed) { "Green" } else { "Red" }
        Write-Host "    $status $($check.name): $($check.message)" -ForegroundColor $color
    }
    
    # Ask for confirmation
    Write-Host ""
    $confirm = Read-Host "Apply this change? (y/n)"
    
    if ($confirm -eq "y") {
        Write-Host ""
        Write-Host "[3] Applying architecture change..." -ForegroundColor Yellow
        
        $applyBody = @{
            change_id = $proposal.change_id
            confirm = $true
        } | ConvertTo-Json
        
        $result = Invoke-RestMethod -Uri "http://localhost:9004/arch/apply" `
            -Method Post `
            -Body $applyBody `
            -ContentType "application/json"
        
        Write-Host "  OK Change applied!" -ForegroundColor Green
        Write-Host "  Rollback ID: $($result.rollback_id)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  Next steps:" -ForegroundColor Yellow
        foreach ($step in $result.next_steps) {
            Write-Host "    - $step" -ForegroundColor Gray
        }
    } else {
        Write-Host "  Change cancelled" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "  X  Failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.Exception.Response.Content -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "[4] Architecture history..." -ForegroundColor Yellow
try {
    $history = Invoke-RestMethod -Uri "http://localhost:9004/arch/history" -Method Get
    Write-Host "  Total changes: $($history.total)" -ForegroundColor Cyan
    
    if ($history.total -gt 0) {
        Write-Host ""
        Write-Host "  Recent changes:" -ForegroundColor Yellow
        foreach ($change in $history.changes | Select-Object -First 5) {
            Write-Host "    [$($change.sha)] $($change.message)" -ForegroundColor Gray
            Write-Host "      $($change.timestamp)" -ForegroundColor DarkGray
        }
    }
} catch {
    Write-Host "  X  Could not fetch history" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
