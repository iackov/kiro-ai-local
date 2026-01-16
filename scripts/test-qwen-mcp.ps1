# Test Qwen MCP Server
# Проверяет что Qwen MCP настроен и работает

$ErrorActionPreference = "Continue"

Write-Host "=== Qwen MCP Test ===" -ForegroundColor Cyan
Write-Host ""

$allOk = $true

# Test 1: Qwen MCP files
Write-Host "[1/6] Checking Qwen MCP files..." -ForegroundColor Yellow
$qwenPath = "C:\Users\Jack\source\kiro\qwen\src\mcp_server"
if (Test-Path "$qwenPath\qwen_mcp_server.py") {
    Write-Host "  OK qwen_mcp_server.py exists" -ForegroundColor Green
} else {
    Write-Host "  FAIL qwen_mcp_server.py not found" -ForegroundColor Red
    $allOk = $false
}

if (Test-Path "$qwenPath\qwen_client.py") {
    Write-Host "  OK qwen_client.py exists" -ForegroundColor Green
} else {
    Write-Host "  FAIL qwen_client.py not found" -ForegroundColor Red
    $allOk = $false
}

# Test 2: Qwen config
Write-Host "`n[2/6] Checking Qwen config..." -ForegroundColor Yellow
$configPath = "$qwenPath\qwen_config.json"
if (Test-Path $configPath) {
    $config = Get-Content $configPath -Raw | ConvertFrom-Json
    
    if ($config.cookies.cookie_string.Length -gt 100) {
        Write-Host "  OK Cookie present ($($config.cookies.cookie_string.Length) chars)" -ForegroundColor Green
    } else {
        Write-Host "  FAIL Cookie missing or too short" -ForegroundColor Red
        $allOk = $false
    }
    
    Write-Host "  Model: $($config.models.default)" -ForegroundColor White
    Write-Host "  MongoDB: $($config.mongo.uri)" -ForegroundColor White
} else {
    Write-Host "  FAIL Config not found" -ForegroundColor Red
    $allOk = $false
}

# Test 3: Python
Write-Host "`n[3/6] Checking Python..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    Write-Host "  OK Python found: $($pythonCmd.Source)" -ForegroundColor Green
} else {
    Write-Host "  FAIL Python not found" -ForegroundColor Red
    $allOk = $false
}

# Test 4: Kiro MCP config
Write-Host "`n[4/6] Checking Kiro MCP config..." -ForegroundColor Yellow
$mcpConfigPath = "$env:USERPROFILE\.kiro\settings\mcp.json"
if (Test-Path $mcpConfigPath) {
    $mcpConfig = Get-Content $mcpConfigPath -Raw | ConvertFrom-Json
    
    if ($mcpConfig.mcpServers.'qwen-chat') {
        Write-Host "  OK qwen-chat server configured" -ForegroundColor Green
        $disabled = $mcpConfig.mcpServers.'qwen-chat'.disabled
        if ($disabled) {
            Write-Host "  WARNING Server is DISABLED" -ForegroundColor Yellow
        } else {
            Write-Host "  OK Server is ENABLED" -ForegroundColor Green
        }
    } else {
        Write-Host "  FAIL qwen-chat not in config" -ForegroundColor Red
        $allOk = $false
    }
} else {
    Write-Host "  FAIL MCP config not found" -ForegroundColor Red
    $allOk = $false
}

# Test 5: MongoDB
Write-Host "`n[5/6] Checking MongoDB..." -ForegroundColor Yellow
$mongoStatus = docker ps --filter "name=ai-mongodb" --format "{{.Status}}"
if ($mongoStatus -match "Up") {
    Write-Host "  OK MongoDB running" -ForegroundColor Green
    
    # Проверяем базу данных
    $dbTest = docker exec ai-mongodb mongosh --quiet --eval "db.version()" qwen_chats 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK Database accessible" -ForegroundColor Green
    } else {
        Write-Host "  WARNING Database check inconclusive" -ForegroundColor Yellow
    }
} else {
    Write-Host "  FAIL MongoDB not running" -ForegroundColor Red
    $allOk = $false
}

# Test 6: Test MCP server startup (quick test)
Write-Host "`n[6/6] Testing MCP server startup..." -ForegroundColor Yellow
Write-Host "  Attempting to import Qwen MCP modules..." -ForegroundColor Gray

$testScript = @"
import sys
sys.path.insert(0, r'$qwenPath')
try:
    import qwen_mcp_server
    import qwen_client
    print('OK: Qwen MCP modules imported successfully')
    sys.exit(0)
except Exception as e:
    print(f'FAIL: {str(e)}')
    sys.exit(1)
"@

$testScript | Out-File -FilePath "$env:TEMP\test_qwen.py" -Encoding UTF8
$result = & python "$env:TEMP\test_qwen.py" 2>&1
Remove-Item "$env:TEMP\test_qwen.py" -ErrorAction SilentlyContinue

if ($LASTEXITCODE -eq 0) {
    Write-Host "  $result" -ForegroundColor Green
} else {
    Write-Host "  $result" -ForegroundColor Red
    $allOk = $false
}

# Summary
Write-Host ""
if ($allOk) {
    Write-Host "=== All Qwen MCP Tests Passed ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Qwen MCP is ready to use in Kiro IDE!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To use in Kiro:" -ForegroundColor Yellow
    Write-Host "  1. Make sure MCP panel shows 'qwen-chat' as connected" -ForegroundColor White
    Write-Host "  2. Use: @kiro используй qwen_chat чтобы ответить на вопрос" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Host "=== Some Qwen MCP Tests Failed ===" -ForegroundColor Red
    Write-Host ""
    Write-Host "Fix issues above before using Qwen MCP" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
