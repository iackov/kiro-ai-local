# Test Qwen via MCP tools in Kiro
# This will test if Qwen MCP is actually working

Write-Host "=== Testing Qwen MCP via Kiro ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. In Kiro IDE, check MCP panel:" -ForegroundColor White
Write-Host "   - qwen-chat should show 'Connected'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. In Kiro chat, send this message:" -ForegroundColor White
Write-Host '   @kiro используй qwen_chat с сообщением "Test: respond with OK"' -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Expected result:" -ForegroundColor White
Write-Host "   - Qwen should respond (any response means API works)" -ForegroundColor Gray
Write-Host "   - If you get response -> Cookies are VALID" -ForegroundColor Green
Write-Host "   - If you get error -> Cookies are EXPIRED" -ForegroundColor Red
Write-Host ""
Write-Host "4. Report back:" -ForegroundColor White
Write-Host "   - Did Qwen respond? (yes/no)" -ForegroundColor Gray
Write-Host ""
Write-Host "If Qwen responded successfully, cookies are valid and we can proceed" -ForegroundColor Yellow
Write-Host "with importing chat history!" -ForegroundColor Yellow
Write-Host ""
