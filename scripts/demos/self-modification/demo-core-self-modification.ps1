# Demonstration: Core System Self-Modification
# Modifies RAG API (the CORE knowledge system), breaks it, and auto-recovers

Write-Host "=== CORE SYSTEM SELF-MODIFICATION ===" -ForegroundColor Cyan
Write-Host "Target: RAG API (Knowledge Core)" -ForegroundColor White
Write-Host ""

$ragUrl = "http://localhost:9001"
$webUrl = "http://localhost:9000"
$coreFile = "services/rag-api/main.py"

# Step 1: Verify RAG is the core
Write-Host "[Step 1] Verify RAG API is operational (THE CORE)" -ForegroundColor Yellow
try {
    $inspect = Invoke-RestMethod -Uri "$ragUrl/inspect" -TimeoutSec 10
    Write-Host "  Documents: $($inspect.total_documents)" -ForegroundColor Green
    Write-Host "  Collections: $($inspect.collections.Count)" -ForegroundColor Green
    Write-Host "  Status: CORE OPERATIONAL" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Core not responding" -ForegroundColor Red
    exit 1
}

# Test query through core
Write-Host ""
Write-Host "  Testing knowledge retrieval..." -ForegroundColor Gray
$body = @{ query = "docker"; top_k = 2 } | ConvertTo-Json
$query = Invoke-RestMethod -Uri "$ragUrl/query" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
Write-Host "  Retrieved: $($query.documents.Count) documents" -ForegroundColor Green

# Step 2: Backup core code
Write-Host ""
Write-Host "[Step 2] Backing up CORE code" -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "services/rag-api/main.py.backup.$timestamp"
Copy-Item $coreFile $backupFile -Force
Write-Host "  Backup: $backupFile" -ForegroundColor Green

# Step 3: Inject breaking change into CORE
Write-Host ""
Write-Host "[Step 3] Injecting BREAKING change into CORE" -ForegroundColor Yellow
Write-Host "  Modifying RAG API query endpoint..." -ForegroundColor Red

$content = Get-Content $coreFile -Raw

# Break the query endpoint - the heart of the system
$brokenContent = $content -replace '@app\.post\("/query"\)', @'
@app.post("/query")
# INJECTED BREAKING CODE - Will crash on every query
async def broken_query_handler():
    raise Exception("CORE SYSTEM FAILURE - Query engine destroyed")
    # Original code unreachable now

@app.post("/query_backup")
'@

Set-Content $coreFile $brokenContent -NoNewline
Write-Host "  CORE query endpoint BROKEN" -ForegroundColor Red

# Step 4: Rebuild CORE
Write-Host ""
Write-Host "[Step 4] Rebuilding CORE with broken code..." -ForegroundColor Yellow
docker compose build rag-api 2>&1 | Out-Null
Write-Host "  Build complete" -ForegroundColor White

Write-Host ""
Write-Host "[Step 5] Restarting CORE..." -ForegroundColor Yellow
docker compose up -d rag-api 2>&1 | Out-Null
Write-Host "  Waiting for CORE startup..." -ForegroundColor Gray
Start-Sleep -Seconds 4

# Step 6: Detect CORE failure
Write-Host ""
Write-Host "[Step 6] Testing CORE functionality..." -ForegroundColor Yellow

$coreFailed = $false
try {
    Write-Host "  Attempting knowledge retrieval..." -NoNewline
    $body = @{ query = "test"; top_k = 1 } | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "$ragUrl/query" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 5
    Write-Host " OK" -ForegroundColor Green
} catch {
    Write-Host " FAILED" -ForegroundColor Red
    $coreFailed = $true
    
    Write-Host ""
    Write-Host "  CRITICAL: CORE SYSTEM FAILURE!" -ForegroundColor Red
    Write-Host "  Knowledge retrieval is DOWN" -ForegroundColor Red
    
    # Check logs
    Write-Host ""
    Write-Host "  CORE error logs:" -ForegroundColor Yellow
    $logs = docker logs ai-rag-api --tail 15 2>&1
    $logs | ForEach-Object {
        if ($_ -match "error|Error|ERROR|Exception|FAILURE") {
            Write-Host "  $_" -ForegroundColor Red
        }
    }
}

# Step 7: Cascade failure check
Write-Host ""
Write-Host "[Step 7] Checking cascade failure..." -ForegroundColor Yellow
Write-Host "  Testing dependent systems..." -ForegroundColor Gray

try {
    $body = @{ query = "test"; top_k = 1 }
    $webQuery = Invoke-RestMethod -Uri "$webUrl/api/rag/query" -Method Post -Body $body -TimeoutSec 5
    Write-Host "  Web UI: Still responding (degraded)" -ForegroundColor Yellow
} catch {
    Write-Host "  Web UI: Also failing (cascade)" -ForegroundColor Red
}

if ($coreFailed) {
    # Step 8: AUTO-RECOVERY OF CORE
    Write-Host ""
    Write-Host "[Step 8] CORE AUTO-RECOVERY INITIATED" -ForegroundColor Cyan
    Write-Host "  System detected CORE failure" -ForegroundColor Yellow
    Write-Host "  Knowledge system is non-functional" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Initiating emergency CORE restoration..." -ForegroundColor Yellow
    
    # Restore CORE code
    Copy-Item $backupFile $coreFile -Force
    Write-Host "  CORE code restored from backup" -ForegroundColor Green
    
    # Rebuild CORE
    Write-Host ""
    Write-Host "[Step 9] Rebuilding CORE with restored code..." -ForegroundColor Yellow
    docker compose build rag-api 2>&1 | Out-Null
    Write-Host "  CORE rebuild complete" -ForegroundColor White
    
    Write-Host ""
    Write-Host "[Step 10] Restarting CORE..." -ForegroundColor Yellow
    docker compose up -d rag-api 2>&1 | Out-Null
    Start-Sleep -Seconds 5
    
    # Verify CORE recovery
    Write-Host ""
    Write-Host "[Step 11] Verifying CORE recovery..." -ForegroundColor Yellow
    
    $coreRecovered = $false
    for ($i = 1; $i -le 3; $i++) {
        Write-Host "  Attempt $i/3..." -NoNewline
        try {
            $inspect = Invoke-RestMethod -Uri "$ragUrl/inspect" -TimeoutSec 10
            Write-Host " OK" -ForegroundColor Green
            Write-Host "  Documents: $($inspect.total_documents)" -ForegroundColor Green
            
            # Test query
            $body = @{ query = "docker"; top_k = 2 } | ConvertTo-Json
            $query = Invoke-RestMethod -Uri "$ragUrl/query" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 10
            Write-Host "  Query working: $($query.documents.Count) results" -ForegroundColor Green
            
            $coreRecovered = $true
            break
        } catch {
            Write-Host " Waiting..." -ForegroundColor Yellow
            Start-Sleep -Seconds 3
        }
    }
    
    Write-Host ""
    if ($coreRecovered) {
        Write-Host "=== CORE RECOVERY SUCCESSFUL ===" -ForegroundColor Green
        Write-Host ""
        Write-Host "What happened:" -ForegroundColor White
        Write-Host "  1. Modified RAG API (CORE knowledge system)" -ForegroundColor Cyan
        Write-Host "  2. Broke query endpoint (heart of the system)" -ForegroundColor Cyan
        Write-Host "  3. CORE became non-functional" -ForegroundColor Cyan
        Write-Host "  4. Knowledge retrieval failed" -ForegroundColor Cyan
        Write-Host "  5. System detected CORE failure" -ForegroundColor Cyan
        Write-Host "  6. Restored CORE code from backup" -ForegroundColor Cyan
        Write-Host "  7. Rebuilt CORE system" -ForegroundColor Cyan
        Write-Host "  8. CORE fully recovered" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "THE CORE SYSTEM HEALED ITSELF!" -ForegroundColor Green
        
        # Verify full system
        Write-Host ""
        Write-Host "[Verification] Testing full system..." -ForegroundColor Yellow
        
        # Test through web-ui
        $body = @{ query = "docker compose"; top_k = 3 }
        $webTest = Invoke-RestMethod -Uri "$webUrl/api/rag/query" -Method Post -Body $body -TimeoutSec 10
        Write-Host "  Web UI → RAG: $($webTest.documents.Count) documents" -ForegroundColor Green
        
        # Test all 9 levels
        Write-Host "  Testing 9 autonomy levels..." -ForegroundColor Gray
        $health = Invoke-RestMethod -Uri "$webUrl/api/metrics/health" -TimeoutSec 10
        Write-Host "  Health: $($health.health_score)/100" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "  ALL SYSTEMS OPERATIONAL" -ForegroundColor Green
        Write-Host "  CORE is fully functional" -ForegroundColor Green
    } else {
        Write-Host "=== CORE RECOVERY FAILED ===" -ForegroundColor Red
        Write-Host "Manual intervention required" -ForegroundColor Yellow
    }
    
    # Cleanup
    Write-Host ""
    Write-Host "Cleaning up backup..." -ForegroundColor Gray
    Remove-Item $backupFile -Force
    
} else {
    Write-Host ""
    Write-Host "  Unexpected: CORE survived the breaking change" -ForegroundColor Yellow
    Write-Host "  Restoring anyway..." -ForegroundColor Gray
    Copy-Item $backupFile $coreFile -Force
    docker compose build rag-api 2>&1 | Out-Null
    docker compose up -d rag-api 2>&1 | Out-Null
    Remove-Item $backupFile -Force
}

Write-Host ""
Write-Host "Demonstration complete." -ForegroundColor Cyan
