# Quick Start Guide

Get the AI Combiner Stack running in 5 minutes.

## Prerequisites

- Windows 10/11
- Docker Desktop installed and running
- PowerShell 5.1+
- 16GB RAM minimum
- 50GB free disk space

## Installation

### 1. Bootstrap the Stack

Run the automated setup script:

```powershell
.\scripts\bootstrap.ps1
```

This will:
- Pull Docker images (Ollama, ChromaDB)
- Build custom services (RAG API, MCP Gateway)
- Start all containers
- Download LLM models (llama2:7b, nomic-embed-text)
- Run health checks

**Note**: First run takes 10-20 minutes depending on internet speed.

### 2. Verify Installation

```powershell
.\scripts\health-check.ps1
```

You should see all services marked as healthy.

### 3. Configure MCP in Kiro

Create or edit `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "local-rag": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "ai-mcp-gateway",
        "node",
        "/app/index.js"
      ],
      "disabled": false,
      "autoApprove": ["rag_query", "rag_inspect", "rag_health"]
    }
  }
}
```

Restart Kiro or reconnect MCP from the MCP panel.

## Usage

### Ingest Documents

```powershell
.\scripts\ingest-docs.ps1 -Path C:\dev\my-project\docs
```

### Test Query

```powershell
.\scripts\test-query.ps1 -Query "What is the architecture?"
```

### Use in Kiro

In Kiro chat:
```
@kiro Use rag_query to find information about authentication
```

## What's Running?

- **RAG API**: http://localhost:9001/docs (OpenAPI docs, includes embedded ChromaDB)
- **MCP Gateway**: http://localhost:9002 (internal)
- **Ollama**: http://localhost:11434
- **MongoDB**: mongodb://localhost:27017 (Qwen history)

## Next Steps

- Read [Architecture Documentation](docs/ARCHITECTURE.md)
- Configure [Qwen Integration](docs/MCP-SETUP.md#integration-with-qwen)
- Set up [Automated Backups](scripts/backup.ps1)

## Troubleshooting

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues.

## Stopping Services

```powershell
docker compose down
```

## Restarting Services

```powershell
docker compose up -d
```
