# Troubleshooting Guide

## Common Issues

### Services Won't Start

**Symptom**: `docker compose up` fails or containers exit immediately

**Solutions**:
1. Check Docker Desktop is running
2. Verify ports are not in use:
   ```powershell
   netstat -ano | findstr "8000 8001 8002 11434"
   ```
3. Check logs:
   ```powershell
   docker compose logs
   ```
4. Reset everything:
   ```powershell
   docker compose down -v
   .\scripts\bootstrap.ps1
   ```

### Ollama Models Not Pulling

**Symptom**: Model download fails or times out

**Solutions**:
1. Check internet connection
2. Increase Docker memory limit (Settings > Resources)
3. Pull manually:
   ```powershell
   docker exec -it ai-ollama ollama pull llama2:7b
   ```

### RAG API Returns Empty Results

**Symptom**: Queries return no documents

**Solutions**:
1. Check if documents are indexed:
   ```powershell
   curl http://localhost:8001/inspect
   ```
2. Ingest documents:
   ```powershell
   .\scripts\ingest-docs.ps1 -Path C:\your\docs
   ```
3. Verify ChromaDB is healthy:
   ```powershell
   curl http://localhost:8000/api/v1/heartbeat
   ```

### MCP Connection Issues

**Symptom**: Kiro can't connect to MCP server

**Solutions**:
1. Verify MCP gateway is running:
   ```powershell
   docker ps | findstr mcp-gateway
   ```
2. Check MCP configuration in `.kiro/settings/mcp.json`
3. Restart MCP server from Kiro's MCP panel
4. Check logs:
   ```powershell
   docker logs ai-mcp-gateway
   ```

### High Memory Usage

**Symptom**: System becomes slow, Docker uses too much RAM

**Solutions**:
1. Reduce Ollama model size (use smaller models)
2. Adjust resource limits in `docker-compose.yml`
3. Clear unused Docker resources:
   ```powershell
   docker system prune -a
   ```

### Path Issues (Windows)

**Symptom**: File ingestion fails with path errors

**Solutions**:
1. Use absolute Windows paths: `C:\dev\docs`
2. Escape backslashes in JSON: `C:\\dev\\docs`
3. Mount host directories in docker-compose.yml if needed

## Logs

View logs for specific services:

```powershell
# All services
docker compose logs -f

# Specific service
docker logs -f ai-rag-api
docker logs -f ai-ollama
docker logs -f ai-chromadb
docker logs -f ai-mcp-gateway

# Last 100 lines
docker logs --tail 100 ai-rag-api
```

## Reset Everything

Complete reset (WARNING: deletes all data):

```powershell
docker compose down -v
Remove-Item -Recurse -Force data, logs
.\scripts\bootstrap.ps1
```

## Performance Tuning

### For Low-End Systems (8GB RAM)
- Use smaller models: `tinyllama:1.1b`
- Reduce chunk size in RAG API
- Limit concurrent requests

### For High-End Systems (32GB+ RAM)
- Use larger models: `llama2:13b` or `mixtral:8x7b`
- Increase worker count
- Enable GPU acceleration (requires NVIDIA GPU + CUDA)

## Getting Help

1. Check logs first
2. Run health check: `.\scripts\health-check.ps1`
3. Review Docker Desktop dashboard
4. Check GitHub issues (if applicable)
