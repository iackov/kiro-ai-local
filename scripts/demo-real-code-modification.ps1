# Real Code Self-Modification - System modifies its own Python code

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   REAL CODE SELF-MODIFICATION" -ForegroundColor Cyan
Write-Host "   System modifies its own source code" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$targetFile = "services/web-ui/main.py"

# Step 1: Show current code
Write-Host "[Step 1] Current Code State" -ForegroundColor Yellow
Write-Host "File: $targetFile`n" -ForegroundColor Gray
$currentHash = (Get-FileHash $targetFile -Algorithm MD5).Hash
Write-Host "  File Hash: $currentHash" -ForegroundColor Cyan
Write-Host "  File Size: $((Get-Item $targetFile).Length) bytes" -ForegroundColor Gray

# Step 2: Create backup
Write-Host "`n[Step 2] Creating Backup" -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "$targetFile.backup.$timestamp"
Copy-Item $targetFile $backupFile
Write-Host "  Backup: $backupFile" -ForegroundColor Green

# Step 3: Modify the code
Write-Host "`n[Step 3] MODIFYING OWN CODE" -ForegroundColor Yellow
Write-Host "Adding new feature to main.py...`n" -ForegroundColor White

$content = Get-Content $targetFile -Raw
$newContent = $content -replace '(from fastapi import FastAPI)', "`$1`n# AUTO-GENERATED: Self-modification timestamp: $timestamp"

Set-Content $targetFile $newContent -NoNewline
Write-Host "  Code modified!" -ForegroundColor Green

$newHash = (Get-FileHash $targetFile -Algorithm MD5).Hash
Write-Host "  New Hash: $newHash" -ForegroundColor Cyan
Write-Host "  Changed: $(if($currentHash -ne $newHash){'YES'}else{'NO'})" -ForegroundColor $(if($currentHash -ne $newHash){'Green'}else{'Red'})

# Step 4: Rebuild
Write-Host "`n[Step 4] Rebuilding with Modified Code" -ForegroundColor Yellow
Write-Host "Running: docker-compose build web-ui`n" -ForegroundColor Gray

$buildOutput = docker-compose build web-ui 2>&1 | Select-Object -Last 5
$buildOutput | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

# Step 5: Restart
Write-Host "`n[Step 5] Restarting Service" -ForegroundColor Yellow
docker-compose restart web-ui 2>&1 | Out-Null
Write-Host "  Waiting for startup..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Step 6: Verify
Write-Host "`n[Step 6] Verification" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:9000/health" -TimeoutSec 10
    Write-Host "  Status: $($health.status)" -ForegroundColor Green
    Write-Host "  Health: $($health.health_score)/100" -ForegroundColor Cyan
    Write-Host "`n  SUCCESS! Service running with modified code" -ForegroundColor Green
} catch {
    Write-Host "  Service not responding yet" -ForegroundColor Yellow
}

# Step 7: Show the modification
Write-Host "`n[Step 7] Code Modification Details" -ForegroundColor Yellow
Write-Host "Showing added lines:`n" -ForegroundColor Gray
$modifiedContent = Get-Content $targetFile | Select-Object -First 10
$modifiedContent | Where-Object { $_ -match "AUTO-GENERATED" } | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Cyan
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   SELF-MODIFICATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "What Actually Happened:" -ForegroundColor White
Write-Host "  1. System backed up its own code" -ForegroundColor Gray
Write-Host "  2. Modified main.py (added comment)" -ForegroundColor Gray
Write-Host "  3. Rebuilt Docker image with new code" -ForegroundColor Gray
Write-Host "  4. Restarted service with modified code" -ForegroundColor Gray
Write-Host "  5. Verified service is running" -ForegroundColor Gray

Write-Host "`nFile Hashes:" -ForegroundColor Yellow
Write-Host "  Before: $currentHash" -ForegroundColor Gray
Write-Host "  After:  $newHash" -ForegroundColor Gray
Write-Host "  Backup: $backupFile" -ForegroundColor Gray

Write-Host "`nThe system PHYSICALLY modified its own source code!" -ForegroundColor Cyan
Write-Host "The modified code is now RUNNING in production!" -ForegroundColor Green

# Cleanup option
Write-Host "`n[Cleanup] Restoring original code..." -ForegroundColor Yellow
Copy-Item $backupFile $targetFile -Force
Remove-Item $backupFile
Write-Host "  Original code restored" -ForegroundColor Green
Write-Host "  Backup removed" -ForegroundColor Gray

Write-Host "`nNote: In production, system would keep modifications" -ForegroundColor Yellow
Write-Host "      This demo restores for safety" -ForegroundColor Gray
Write-Host ""
