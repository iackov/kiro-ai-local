# Demonstration: Self-Healing with Auto-Rollback
# System modifies its own code, detects failure, and auto-recovers

Write-Host "=== SELF-HEALING AUTO-ROLLBACK DEMONSTRATION ===" -ForegroundColor Cyan
Write-Host "System will modify its own code, break, detect, and auto-recover" -ForegroundColor White
Write-Host ""

$baseUrl = "http://localhost:9000"

# Step 1: Current healthy state
Write-Host "[Step 1] Verify system is healthy" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/api/metrics/health" -TimeoutSec 10
    Write-Host "  Health Score: $($health.health_score)/100" -ForegroundColor Green
    Write-Host "  Status: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: System not responding" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Propose breaking change to web-ui memory
Write-Host "[Step 2] Propose BREAKING change: Reduce web-ui memory to 32M" -ForegroundColor Yellow
Write-Host "  (This will cause OOM and crash)" -ForegroundColor Red

$body = @{
    prompt = "Change web-ui memory limit to 32M"
    auto_apply = $false
}

$proposal = Invoke-RestMethod -Uri "$baseUrl/api/arch/propose" -Method Post -Body $body -TimeoutSec 30

Write-Host "  Change ID: $($proposal.change_id)" -ForegroundColor Cyan
Write-Host "  Safe: $($proposal.safe)" -ForegroundColor $(if($proposal.safe) { "Yellow" } else { "Red" })

Write-Host ""
Write-Host "Press Enter to apply BREAKING change..." -ForegroundColor Yellow
Read-Host

# Step 3: Apply breaking change
Write-Host "[Step 3] Applying breaking change" -ForegroundColor Yellow

$applyBody = @{
    change_id = $proposal.change_id
    confirm = $true
}

$result = Invoke-RestMethod -Uri "$baseUrl/api/arch/apply" -Method Post -Body $applyBody -TimeoutSec 30

Write-Host "  Applied: $($result.status)" -ForegroundColor Yellow
Write-Host "  Rollback ID: $($result.rollback_id)" -ForegroundColor Cyan
$rollbackId = $result.rollback_id

Write-Host ""

# Step 4: Restart web-ui with broken config
Write-Host "[Step 4] Restarting web-ui with broken config..." -ForegroundColor Yellow
docker compose up -d web-ui 2>&1 | Out-Null
Write-Host "  Waiting for startup..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Step 5: Detect failure
Write-Host ""
Write-Host "[Step 5] Detecting failure..." -ForegroundColor Yellow

$attempts = 0
$maxAttempts = 3
$failed = $false

while ($attempts -lt $maxAttempts) {
    $attempts++
    Write-Host "  Attempt $attempts/$maxAttempts..." -NoNewline
    
    try {
        $health = Invoke-RestMethod -Uri "$baseUrl/api/metrics/health" -TimeoutSec 5
        Write-Host " OK" -ForegroundColor Green
        break
    } catch {
        Write-Host " FAILED" -ForegroundColor Red
        $failed = $true
        Start-Sleep -Seconds 2
    }
}

if ($failed) {
    Write-Host ""
    Write-Host "  CRITICAL: Web-UI is DOWN!" -ForegroundColor Red
    Write-Host "  Checking container status..." -ForegroundColor Yellow
    
    $containerStatus = docker ps -a --filter "name=ai-web-ui" --format "{{.Status}}"
    Write-Host "  Container: $containerStatus" -ForegroundColor Red
    
    # Check logs for OOM
    Write-Host ""
    Write-Host "  Checking logs for errors..." -ForegroundColor Yellow
    $logs = docker logs ai-web-ui --tail 20 2>&1
    if ($logs -match "killed|OOM|memory|error") {
        Write-Host "  ERROR DETECTED: Memory/OOM issue" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "[Step 6] AUTO-ROLLBACK INITIATED" -ForegroundColor Cyan
    Write-Host "  System detected critical failure" -ForegroundColor Yellow
    Write-Host "  Initiating automatic rollback..." -ForegroundColor Yellow
    
    # Rollback via arch-engine directly
    Write-Host ""
    Write-Host "  Rolling back to: $rollbackId" -ForegroundColor Cyan
    
    $rollbackBody = @{
        rollback_id = $rollbackId
    }
    
    try {
        # Call arch-engine directly since web-ui is down
        $rollbackResult = Invoke-RestMethod -Uri "http://localhost:9004/arch/rollback" -Method Post -Body ($rollbackBody | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 30
        
        Write-Host "  Rollback: $($rollbackResult.status)" -ForegroundColor Green
        Write-Host "  Restored from: $($rollbackResult.restored_from)" -ForegroundColor White
    } catch {
        Write-Host "  Rollback via API failed, using backup directly..." -ForegroundColor Yellow
        
        # Direct file restore
        $backupFile = "docker-compose.yml.backup.$($rollbackId.Replace('_', ''))"
        if (Test-Path $backupFile) {
            Copy-Item $backupFile docker-compose.yml -Force
            Write-Host "  Restored from backup file" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "[Step 7] Restarting with restored config..." -ForegroundColor Yellow
    docker compose up -d web-ui 2>&1 | Out-Null
    Write-Host "  Waiting for recovery..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    # Verify recovery
    Write-Host ""
    Write-Host "[Step 8] Verifying recovery..." -ForegroundColor Yellow
    
    $recovered = $false
    for ($i = 1; $i -le 3; $i++) {
        Write-Host "  Attempt $i/3..." -NoNewline
        try {
            $health = Invoke-RestMethod -Uri "$baseUrl/api/metrics/health" -TimeoutSec 10
            Write-Host " OK" -ForegroundColor Green
            Write-Host "  Health Score: $($health.health_score)/100" -ForegroundColor Green
            $recovered = $true
            break
        } catch {
            Write-Host " Waiting..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
        }
    }
    
    Write-Host ""
    if ($recovered) {
        Write-Host "=== SELF-HEALING SUCCESSFUL ===" -ForegroundColor Green
        Write-Host ""
        Write-Host "Summary:" -ForegroundColor White
        Write-Host "  1. System applied breaking change (32M memory)" -ForegroundColor Cyan
        Write-Host "  2. Web-UI crashed (OOM)" -ForegroundColor Cyan
        Write-Host "  3. System detected failure" -ForegroundColor Cyan
        Write-Host "  4. Automatic rollback initiated" -ForegroundColor Cyan
        Write-Host "  5. Configuration restored" -ForegroundColor Cyan
        Write-Host "  6. Service recovered" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "THE SYSTEM HEALED ITSELF!" -ForegroundColor Green
    } else {
        Write-Host "=== RECOVERY FAILED ===" -ForegroundColor Red
        Write-Host "Manual intervention required" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "  System survived the change (unexpected)" -ForegroundColor Yellow
    Write-Host "  Rolling back anyway for demo..." -ForegroundColor Gray
    
    $rollbackBody = @{
        rollback_id = $rollbackId
    }
    
    Invoke-RestMethod -Uri "$baseUrl/api/arch/rollback" -Method Post -Body $rollbackBody -TimeoutSec 30 | Out-Null
    Write-Host "  Rolled back" -ForegroundColor Green
}

Write-Host ""
Write-Host "Demonstration complete." -ForegroundColor Cyan
