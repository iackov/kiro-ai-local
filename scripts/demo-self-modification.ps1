# Demonstration of Self-Modification (Level 3)
# Shows how system can modify its own docker-compose.yml

Write-Host "=== SELF-MODIFICATION DEMONSTRATION ===" -ForegroundColor Cyan
Write-Host "Level 3: Architecture Engine" -ForegroundColor White
Write-Host ""

$baseUrl = "http://localhost:9000"

# Step 1: Show current state
Write-Host "[Step 1] Current docker-compose.yml state" -ForegroundColor Yellow
Write-Host "Checking current services..." -ForegroundColor Gray
$currentServices = docker compose config --services
Write-Host "Current services:" -ForegroundColor Cyan
$currentServices | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }
Write-Host ""

# Step 2: Propose a modification
Write-Host "[Step 2] Proposing modification: Add nginx service" -ForegroundColor Yellow
Write-Host "Sending request to Architecture Engine..." -ForegroundColor Gray

$body = @{
    prompt = "Add nginx service with 256M memory limit on port 8080"
    auto_apply = $false
}

$proposal = Invoke-RestMethod -Uri "$baseUrl/api/arch/propose" -Method Post -Body $body -TimeoutSec 30

Write-Host "Proposal received:" -ForegroundColor Cyan
Write-Host "  Change ID: $($proposal.change_id)" -ForegroundColor White
Write-Host "  Safe: $($proposal.safe)" -ForegroundColor $(if($proposal.safe) { "Green" } else { "Red" })
Write-Host "  Changes: $($proposal.changes.Count) modifications" -ForegroundColor White

if ($proposal.changes) {
    Write-Host "`nProposed changes:" -ForegroundColor Cyan
    foreach ($change in $proposal.changes) {
        Write-Host "  Type: $($change.type)" -ForegroundColor Yellow
        Write-Host "  Description: $($change.description)" -ForegroundColor White
    }
}

Write-Host "`nSafety checks:" -ForegroundColor Cyan
foreach ($check in $proposal.safety_checks) {
    $color = if($check.passed) { "Green" } else { "Red" }
    $status = if($check.passed) { "PASS" } else { "FAIL" }
    Write-Host "  [$status] $($check.check)" -ForegroundColor $color
}

if (-not $proposal.safe) {
    Write-Host "`nProposal is NOT SAFE. Stopping." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Press Enter to apply the modification..." -ForegroundColor Yellow
Read-Host

# Step 3: Apply the modification
Write-Host "[Step 3] Applying modification" -ForegroundColor Yellow
Write-Host "Modifying docker-compose.yml..." -ForegroundColor Gray

$applyBody = @{
    change_id = $proposal.change_id
    confirm = $true
}

$result = Invoke-RestMethod -Uri "$baseUrl/api/arch/apply" -Method Post -Body $applyBody -TimeoutSec 30

Write-Host "Modification applied:" -ForegroundColor Green
Write-Host "  Status: $($result.status)" -ForegroundColor White
Write-Host "  Rollback ID: $($result.rollback_id)" -ForegroundColor Cyan
Write-Host "  Backup: $($result.backup_path)" -ForegroundColor White

Write-Host "`nNext steps:" -ForegroundColor Cyan
foreach ($step in $result.next_steps) {
    Write-Host "  - $step" -ForegroundColor White
}

Write-Host ""

# Step 4: Verify modification
Write-Host "[Step 4] Verifying modification" -ForegroundColor Yellow
Write-Host "Checking updated services..." -ForegroundColor Gray

$newServices = docker compose config --services
Write-Host "Updated services:" -ForegroundColor Cyan
$newServices | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }

$addedServices = $newServices | Where-Object { $_ -notin $currentServices }
if ($addedServices) {
    Write-Host "`nNewly added services:" -ForegroundColor Green
    $addedServices | ForEach-Object { Write-Host "  + $_" -ForegroundColor Green }
}

Write-Host ""

# Step 5: Show git history
Write-Host "[Step 5] Git version control" -ForegroundColor Yellow
Write-Host "Architecture changes are tracked in git:" -ForegroundColor Gray

$gitLog = git log --oneline --grep="arch-" -5
Write-Host "`nRecent architecture changes:" -ForegroundColor Cyan
$gitLog | ForEach-Object { Write-Host "  $_" -ForegroundColor White }

Write-Host ""

# Step 6: Rollback option
Write-Host "[Step 6] Rollback capability" -ForegroundColor Yellow
Write-Host "System can rollback to previous state using:" -ForegroundColor Gray
Write-Host "  Rollback ID: $($result.rollback_id)" -ForegroundColor Cyan
Write-Host "  Command: POST /api/arch/rollback" -ForegroundColor White

Write-Host ""
Write-Host "Would you like to rollback? (y/n): " -NoNewline -ForegroundColor Yellow
$rollback = Read-Host

if ($rollback -eq "y") {
    Write-Host "`nRolling back..." -ForegroundColor Yellow
    
    $rollbackBody = @{
        rollback_id = $result.rollback_id
    }
    
    $rollbackResult = Invoke-RestMethod -Uri "$baseUrl/api/arch/rollback" -Method Post -Body $rollbackBody -TimeoutSec 30
    
    Write-Host "Rollback completed:" -ForegroundColor Green
    Write-Host "  Status: $($rollbackResult.status)" -ForegroundColor White
    Write-Host "  Restored: $($rollbackResult.restored_from)" -ForegroundColor Cyan
    
    Write-Host "`nVerifying rollback..." -ForegroundColor Gray
    $rolledBackServices = docker compose config --services
    Write-Host "Services after rollback:" -ForegroundColor Cyan
    $rolledBackServices | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }
}

Write-Host ""
Write-Host "=== DEMONSTRATION COMPLETE ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor White
Write-Host "  1. System analyzed modification request" -ForegroundColor Green
Write-Host "  2. Generated safe docker-compose changes" -ForegroundColor Green
Write-Host "  3. Applied changes with backup" -ForegroundColor Green
Write-Host "  4. Tracked changes in git" -ForegroundColor Green
Write-Host "  5. Provided rollback capability" -ForegroundColor Green
Write-Host ""
Write-Host "The system successfully modified itself!" -ForegroundColor Green
