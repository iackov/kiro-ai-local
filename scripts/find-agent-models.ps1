# Find Best Agent Models for RTX 4060 Ti 8GB

Write-Host ""
Write-Host "=== Agent Models for RTX 4060 Ti 8GB ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Your GPU: RTX 4060 Ti with 8GB VRAM" -ForegroundColor Yellow
Write-Host ""

Write-Host "Recommended Models for Agent Reasoning:" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1] Qwen2.5-Coder (7B) - RECOMMENDED" -ForegroundColor Green
Write-Host "    Size: ~4.7GB" -ForegroundColor Gray
Write-Host "    Best for: Code generation, reasoning" -ForegroundColor Gray
Write-Host "    Command: ollama pull qwen2.5-coder:7b" -ForegroundColor White
Write-Host ""

Write-Host "[2] DeepSeek-Coder-V2 (16B) - Quantized" -ForegroundColor Green
Write-Host "    Size: ~9GB (Q4 quantization)" -ForegroundColor Gray
Write-Host "    Best for: Advanced coding, reasoning" -ForegroundColor Gray
Write-Host "    Command: ollama pull deepseek-coder-v2:16b-lite-instruct-q4_0" -ForegroundColor White
Write-Host ""

Write-Host "[3] Llama 3.2 (3B)" -ForegroundColor Yellow
Write-Host "    Size: ~2GB" -ForegroundColor Gray
Write-Host "    Best for: Fast inference, general tasks" -ForegroundColor Gray
Write-Host "    Command: ollama pull llama3.2:3b" -ForegroundColor White
Write-Host ""

Write-Host "[4] Phi-3 (3.8B)" -ForegroundColor Yellow
Write-Host "    Size: ~2.3GB" -ForegroundColor Gray
Write-Host "    Best for: Reasoning, small but capable" -ForegroundColor Gray
Write-Host "    Command: ollama pull phi3:3.8b" -ForegroundColor White
Write-Host ""

Write-Host "[5] Mistral (7B)" -ForegroundColor Yellow
Write-Host "    Size: ~4.1GB" -ForegroundColor Gray
Write-Host "    Best for: General purpose, good reasoning" -ForegroundColor Gray
Write-Host "    Command: ollama pull mistral:7b" -ForegroundColor White
Write-Host ""

Write-Host "About Youtu-LLM:" -ForegroundColor Cyan
Write-Host "  - Youtu-LLM is from Tencent" -ForegroundColor White
Write-Host "  - Not yet available in Ollama library" -ForegroundColor Yellow
Write-Host "  - May need manual GGUF conversion from HuggingFace" -ForegroundColor Gray
Write-Host ""

Write-Host "Current models installed:" -ForegroundColor Yellow
ollama list
Write-Host ""

Write-Host "Would you like to test one? Run:" -ForegroundColor Cyan
Write-Host "  .\scripts\test-new-model.ps1 -ModelName 'qwen2.5-coder:7b'" -ForegroundColor White
Write-Host ""
