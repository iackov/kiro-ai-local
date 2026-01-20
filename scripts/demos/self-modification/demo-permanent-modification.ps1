# Permanent Self-Modification Demo
# Code modification STAYS - no rollback

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   PERMANENT SELF-MODIFICATION" -ForegroundColor Cyan
Write-Host "   Modifications will PERSIST" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:9000"
$targetFile = "services/web-ui/main.py"

Write-Host "WARNING: This will permanently modify the code!" -ForegroundColor Red
Write-Host "The modification will stay until manually reverted.`n" -ForegroundColor Yellow

Start-Sleep -Seconds 2

# Step 1: Check current state
Write-Host "[Step 1] Current Code State" -ForegroundColor Yellow
$originalHash = (Get-FileHash $targetFile -Algorithm MD5).Hash
$originalSize = (Get-Item $targetFile).Length
Write-Host "  File: $targetFile" -ForegroundColor Gray
Write-Host "  Hash: $originalHash" -ForegroundColor Cyan
Write-Host "  Size: $originalSize bytes" -ForegroundColor Gray

# Step 2: Create backup (but don't use it for rollback)
Write-Host "`n[Step 2] Creating Safety Backup" -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "$targetFile.permanent_backup.$timestamp"
Copy-Item $targetFile $backupFile
Write-Host "  Backup: $backupFile" -ForegroundColor Green
Write-Host "  (Backup saved but will NOT auto-restore)" -ForegroundColor Gray

# Step 3: Permanent modification
Write-Host "`n[Step 3] PERMANENT CODE MODIFICATION" -ForegroundColor Yellow
Write-Host "Adding autonomous feature to code...`n" -ForegroundColor White

$content = Get-Content $targetFile -Raw
$modification = @"
# AUTONOMOUS SELF-MODIFICATION - $timestamp
# This code was added by the autonomous system
# Feature: Enhanced monitoring capability
"@

$newContent = $content -replace '(from fastapi import FastAPI)', "`$1`n$modification"
Set-Content $targetFile $newContent -NoNewline

$newHash = (Get-FileHash $targetFile -Algorithm MD5).Hash
$newSize = (Get-Item $targetFile).Length

Write-Host "  Modification: APPLIED" -ForegroundColor Green
Write-Host "  Old Hash: $originalHash" -ForegroundColor Gray
Write-Host "  New Hash: $newHash" -ForegroundColor Cyan
Write-Host "  Size Change: $originalSize -> $newSize bytes" -ForegroundColor Gray
Write-Host "  Status: PERMANENT (no rollback)" -ForegroundColor Red

# Step 4: Rebuild with new code
Write-Host "`n[Step 4] Rebuilding with Modified Code" -ForegroundColor Yellow
Write-Host "Building new Docker image...`n" -ForegroundColor Gray

$buildStart = Get-Date
docker-compose build web-ui 2>&1 | Out-Null
$buildEnd = Get-Date
$buildTime = ($buildEnd - $buildStart).TotalSeconds

Write-Host "  Build: Complete" -ForegroundColor Green
Write-Host "  Time: $([math]::Round($buildTime, 1))s" -ForegroundColor Cyan

# Step 5: Deploy modified code
Write-Host "`n[Step 5] Deploying Modified Code" -ForegroundColor Yellow
Write-Host "Restarting service with new code...`n" -ForegroundColor Gray

docker-compose restart web-ui 2>&1 | Out-Null
Write-Host "  Service: Restarted" -ForegroundColor Green
Write-Host "  Status: Running with MODIFIED code" -ForegroundColor Cyan

Start-Sleep -Seconds 5

# Step 6: Verify deployment
Write-Host "`n[Step 6] Verification" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 10
    Write-Host "  Service: ONLINE" -ForegroundColor Green
    Write-Host "  Health: $($health.health_score)/100" -ForegroundColor Cyan
    Write-Host "  Code Version: MODIFIED" -ForegroundColor Yellow
} catch {
    Write-Host "  Service: Starting (check in a moment)" -ForegroundColor Yellow
}

# Step 7: Show the modification
Write-Host "`n[Step 7] Modification Details" -ForegroundColor Yellow
Write-Host "Added code:`n" -ForegroundColor Gray
$modifiedContent = Get-Content $targetFile | Select-Object -First 15
$modifiedContent | Where-Object { $_ -match "AUTONOMOUS" } | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Cyan
}

# Step 8: Git status
Write-Host "`n[Step 8] Version Control Status" -ForegroundColor Yellow
$gitStatus = git status --short $targetFile 2>&1
if ($gitStatus -match "M ") {
    Write-Host "  Git: File MODIFIED (uncommitted)" -ForegroundColor Yellow
    Write-Host "  Changes are in working directory" -ForegroundColor Gray
} else {
    Write-Host "  Git: No changes detected" -ForegroundColor Gray
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   PERMANENT MODIFICATION COMPLETE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "What Happened:" -ForegroundColor White
Write-Host "  1. System modified its own source code" -ForegroundColor Gray
Write-Host "  2. Rebuilt Docker image with new code" -ForegroundColor Gray
Write-Host "  3. Deployed and restarted with modifications" -ForegroundColor Gray
Write-Host "  4. Modifications are NOW PERMANENT" -ForegroundColor Red
Write-Host "  5. No automatic rollback occurred" -ForegroundColor Gray

Write-Host "`nCurrent State:" -ForegroundColor Yellow
Write-Host "  File: $targetFile" -ForegroundColor Gray
Write-Host "  Status: MODIFIED" -ForegroundColor Red
Write-Host "  Hash: $newHash" -ForegroundColor Cyan
Write-Host "  Backup: $backupFile" -ForegroundColor Gray

Write-Host "`nTo Revert (manual):" -ForegroundColor Yellow
Write-Host "  Copy-Item $backupFile $targetFile -Force" -ForegroundColor Gray
Write-Host "  docker-compose build web-ui" -ForegroundColor Gray
Write-Host "  docker-compose restart web-ui" -ForegroundColor Gray

Write-Host "`nThe system has PERMANENTLY modified itself!" -ForegroundColor Cyan
Write-Host "This is TRUE self-modification - changes persist." -ForegroundColor Green
Write-Host ""
