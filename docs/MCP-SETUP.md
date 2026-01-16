# MCP Setup Guide

## Configuring Kiro to Use Local RAG

### Option 1: Using Docker Container (Recommended)

The MCP gateway runs inside Docker and communicates with the RAG API.

1. **Ensure services are running**:
   ```powershell
   docker ps | findstr mcp-gateway
   ```

2. **Create MCP configuration** in `.kiro/settings/mcp.json`:
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

3. **Restart MCP** from Kiro's MCP panel or restart Kiro

### Option 2: Using Local Node.js

If you prefer running MCP gateway outside Docker:

1. **Install dependencies**:
   ```powershell
   cd services/mcp-gateway
   npm install
   ```

2. **Set environment variables**:
   ```powershell
   $env:RAG_API_URL = "http://localhost:8001"
   ```

3. **Create MCP configuration** in `.kiro/settings/mcp.json`:
   ```json
   {
     "mcpServers": {
       "local-rag": {
         "command": "node",
         "args": ["C:\\path\\to\\ai-combiner\\services\\mcp-gateway\\index.js"],
         "env": {
           "RAG_API_URL": "http://localhost:8001"
         },
         "disabled": false,
         "autoApprove": ["rag_query", "rag_inspect"]
       }
     }
   }
   ```

## Available MCP Tools

### rag_query
Query the RAG system with semantic search.

**Parameters**:
- `query` (string, required): Natural language query
- `top_k` (number, optional): Number of results (default: 5)

**Example**:
```
Use rag_query to search for "authentication implementation"
```

### rag_ingest
Ingest documents from a local path.

**Parameters**:
- `path` (string, required): Windows path to file or directory
- `recursive` (boolean, optional): Process subdirectories (default: true)

**Example**:
```
Use rag_ingest to index documents in C:\dev\my-project\docs
```

### rag_inspect
Get statistics about the RAG database.

**Example**:
```
Use rag_inspect to see how many documents are indexed
```

### rag_health
Check health status of all RAG services.

**Example**:
```
Use rag_health to verify services are running
```

## Testing MCP Integration

1. **Open Kiro IDE**

2. **Check MCP status** in the MCP panel (should show "local-rag" as connected)

3. **Test in chat**:
   ```
   @kiro Use rag_health to check if the RAG system is running
   ```

4. **Ingest some documents**:
   ```
   @kiro Use rag_ingest to index C:\dev\my-docs
   ```

5. **Query the system**:
   ```
   @kiro Use rag_query to find information about authentication
   ```

## Troubleshooting

### MCP Server Won't Connect

1. Check Docker container is running:
   ```powershell
   docker ps | findstr mcp-gateway
   ```

2. Check logs:
   ```powershell
   docker logs ai-mcp-gateway
   ```

3. Verify RAG API is accessible:
   ```powershell
   curl http://localhost:8001/health
   ```

### Tools Not Appearing

1. Restart MCP from Kiro's MCP panel
2. Check MCP configuration syntax
3. Look for errors in Kiro's output panel

### Permission Errors

Add tools to `autoApprove` list in MCP config to skip confirmation prompts.

## Advanced Configuration

### Custom Timeout
```json
{
  "mcpServers": {
    "local-rag": {
      "command": "docker",
      "args": ["exec", "-i", "ai-mcp-gateway", "node", "/app/index.js"],
      "timeout": 60000,
      "disabled": false
    }
  }
}
```

### Environment Variables
```json
{
  "mcpServers": {
    "local-rag": {
      "command": "docker",
      "args": ["exec", "-i", "ai-mcp-gateway", "node", "/app/index.js"],
      "env": {
        "LOG_LEVEL": "debug",
        "RAG_API_URL": "http://rag-api:8001"
      },
      "disabled": false
    }
  }
}
```

## Integration with Qwen

If you have Qwen configured via MCP, you can use both together:

```json
{
  "mcpServers": {
    "qwen": {
      "command": "uvx",
      "args": ["qwen-mcp-server"],
      "env": {
        "QWEN_API_KEY": "your-key"
      },
      "disabled": false
    },
    "local-rag": {
      "command": "docker",
      "args": ["exec", "-i", "ai-mcp-gateway", "node", "/app/index.js"],
      "disabled": false
    }
  }
}
```

Now you can:
1. Use `rag_query` to retrieve relevant context
2. Pass that context to Qwen for generation
3. Get grounded, factual responses based on your documents
