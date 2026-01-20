# Real Self-Modification Demo - System actually modifies files

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   REAL SELF-MODIFICATION" -ForegroundColor Cyan
Write-Host "   System modifies actual files" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Current state
Write-Host "[Step 1] Current Infrastructure" -ForegroundColor Yellow
Write-Host "Checking running services...`n" -ForegroundColor Gray
docker-compose ps --format "table {{.Service}}\t{{.Status}}" 2>$null | Select-Object -First 10

# Step 2: Propose modification
Write-Host "`n[Step 2] Proposing Modification" -ForegroundColor Yellow
Write-Host "Task: Add Grafana monitoring service`n" -ForegroundColor White

$proposal = @{
    prompt = "Add Grafana monitoring service on port 3000"
    auto_apply = $false
} | ConvertTo-Json

try {
    $resp = Invoke-RestMethod -Uri "http://localhost:9004/arch/propose" -Method Post -Body $proposal -ContentType "application/json" -TimeoutSec 30
    
    Write-Host "Proposal Result:" -ForegroundColor Green
    Write-Host "  Change ID: $($resp.change_id)" -ForegroundColor Cyan
    Write-Host "  Safe: $($resp.safe)" -ForegroundColor $(if($resp.safe){'Green'}else{'Red'})
    Write-Host "  Changes: $($resp.changes.Count) modifications" -ForegroundColor White
    
    if ($resp.changes.Count -gt 0) {
        Write-Host "`n  Proposed Changes:" -ForegroundColor Yellow
        $resp.changes | ForEach-Object {
            Write-Host "    - $($_.description)" -ForegroundColor Gray
        }
    }
    
    # Step 3: Apply if safe
    if ($resp.safe -and $resp.change_id) {
        Write-Host "`n[Step 3] Applying Changes to REAL Files" -ForegroundColor Yellow
        Write-Host "Modifying docker-compose.yml...`n" -ForegroundColor Gray
        
        $apply = @{
            change_id = $resp.change_id
            confirm = $true
        } | ConvertTo-Json
        
        try {
            $applyResp = Invoke-RestMethod -Uri "http://localhost:9004/arch/apply" -Method Post -Body $apply -ContentType "application/json" -TimeoutSec 30
            
            Write-Host "  Status: $($applyResp.status)" -ForegroundColor Green
            Write-Host "  Files Modified: $($applyResp.files_modified -join ', ')" -ForegroundColor Cyan
            Write-Host "  Backup Created: $($applyResp.backup_path)" -ForegroundColor Gray
            
            # Step 4: Start new service
            Write-Host "`n[Step 4] Starting New Service" -ForegroundColor Yellow
            Write-Host "Running: docker-compose up -d grafana`n" -ForegroundColor Gray
            
            $output = docker-compose up -d grafana 2>&1
            Write-Host "  $output" -ForegroundColor Gray
            
            Start-Sleep -Seconds 5
            
            # Step 5: Verify
            Write-Host "`n[Step 5] Verification" -ForegroundColor Yellow
            $services = docker-compose ps --format "{{.Service}}" 2>$null
            
            if ($services -match "grafana") {
                Write-Host "  SUCCESS! Grafana is running" -ForegroundColor Green
                Write-Host "  Access at: http://localhost:3000" -ForegroundColor Cyan
                Write-Host "  Credentials: admin/admin" -ForegroundColor Gray
                
                # Show new state
                Write-Host "`n[Step 6] New Infrastructure State" -ForegroundColor Yellow
                docker-compose ps --format "table {{.Service}}\t{{.Status}}" 2>$null | Select-Object -First 12
                
                Write-Host "`n========================================" -ForegroundColor Cyan
                Write-Host "   SELF-MODIFICATION SUCCESSFUL!" -ForegroundColor Green
                Write-Host "========================================" -ForegroundColor Cyan
                Write-Host "`nWhat happened:" -ForegroundColor White
                Write-Host "  1. System analyzed the request" -ForegroundColor Gray
                Write-Host "  2. Generated docker-compose changes" -ForegroundColor Gray
                Write-Host "  3. Modified REAL docker-compose.yml file" -ForegroundColor Gray
                Write-Host "  4. Started the new service" -ForegroundColor Gray
                Write-Host "  5. Verified it's running" -ForegroundColor Gray
                Write-Host "`nThe system ACTUALLY modified itself!" -ForegroundColor Cyan
                
            } else {
                Write-Host "  Service not detected yet (may need more time)" -ForegroundColor Yellow
            }
            
        } catch {
            Write-Host "  Apply failed: $($_.Exception.Message)" -ForegroundColor Red
        }
        
    } else {
        Write-Host "`n[Step 3] Modification Not Applied" -ForegroundColor Yellow
        if (-not $resp.safe) {
            Write-Host "  Reason: Safety checks failed" -ForegroundColor Red
            Write-Host "  This is GOOD - system protects itself!" -ForegroundColor Green
        } else {
            Write-Host "  Reason: No valid change ID" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
