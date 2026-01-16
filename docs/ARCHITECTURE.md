# Architecture Documentation

## System Overview

The AI Combiner Stack is a modular, offline-capable RAG (Retrieval-Augmented Generation) system designed for local development environments.

## Components

### 1. Ollama (LLM Service)
- **Purpose**: Local language model inference
- **Port**: 11434
- **Models**: 
  - `llama2:7b` - Main LLM for generation
  - `nomic-embed-text` - Embedding model for vectors
- **Resources**: 4 CPU cores, 8GB RAM
- **Data**: Persisted in `ollama-data` volume

### 2. ChromaDB (Vector Database)
- **Purpose**: Store and query document embeddings
- **Port**: 8000
- **Features**:
  - Persistent storage
  - Semantic search
  - Metadata filtering
- **Resources**: 2 CPU cores, 4GB RAM
- **Data**: Persisted in `chroma-data` volume

### 3. RAG API (Python FastAPI)
- **Purpose**: Document ingestion, chunking, and retrieval
- **Port**: 8001
- **Endpoints**:
  - `POST /query` - Semantic search
  - `POST /ingest` - Ingest documents
  - `POST /ingest/upload` - Upload single file
  - `GET /inspect` - Database statistics
  - `GET /health` - Health check
  - `DELETE /clear` - Clear database
- **Features**:
  - Semantic chunking with overlap
  - Multi-format support (PDF, Markdown, Code)
  - Structured logging
  - OpenAPI documentation
- **Resources**: 2 CPU cores, 2GB RAM

### 4. MCP Gateway (Node.js)
- **Purpose**: Model Context Protocol server for Kiro integration
- **Port**: 8002 (internal)
- **Tools**:
  - `rag_query` - Query RAG system
  - `rag_ingest` - Ingest documents
  - `rag_inspect` - Get statistics
  - `rag_health` - Health check
- **Resources**: 1 CPU core, 1GB RAM

### 5. MongoDB (Optional)
- **Purpose**: Chat history storage for Qwen MCP
- **Port**: 27017
- **Database**: `qwen_chats`
- **Collections**:
  - `chats` - Chat metadata
  - `messages` - Chat messages
- **Resources**: 1 CPU core, 1GB RAM
- **Data**: Persisted in `mongo-data` volume

## Data Flow

### Document Ingestion
```
User → MCP Gateway → RAG API → Document Loader
                                      ↓
                              Text Splitter
                                      ↓
                              Ollama (embeddings)
                                      ↓
                                  ChromaDB
```

### Query Processing
```
User → MCP Gateway → RAG API → ChromaDB (vector search)
                                      ↓
                              Retrieve top-k chunks
                                      ↓
                              Return to user
```

## Network Architecture

All services run in isolated Docker network `ai-local-net`:

```
┌─────────────────────────────────────────┐
│         Host (Windows 10)               │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Docker Network: ai-local-net    │ │
│  │                                   │ │
│  │  ┌──────────┐  ┌──────────┐     │ │
│  │  │  Ollama  │  │ ChromaDB │     │ │
│  │  │  :11434  │  │  :8000   │     │ │
│  │  └────┬─────┘  └────┬─────┘     │ │
│  │       │             │            │ │
│  │       └──────┬──────┘            │ │
│  │              │                   │ │
│  │        ┌─────▼─────┐             │ │
│  │        │  RAG API  │             │ │
│  │        │   :8001   │             │ │
│  │        └─────┬─────┘             │ │
│  │              │                   │ │
│  │        ┌─────▼─────┐             │ │
│  │        │    MCP    │             │ │
│  │        │  Gateway  │             │ │
│  │        └─────┬─────┘             │ │
│  │              │                   │ │
│  │        ┌─────▼─────┐             │ │
│  │        │  MongoDB  │             │ │
│  │        │  :27017   │             │ │
│  │        │(Qwen hist)│             │ │
│  │        └───────────┘             │ │
│  │                                   │ │
│  └──────────────┼───────────────────┘ │
│                 │                     │
│           ┌─────▼─────┐               │
│           │ Kiro IDE  │               │
│           │ + Qwen    │               │
│           │   MCP     │               │
│           └───────────┘               │
└─────────────────────────────────────────┘
```

## Storage

### Volumes
- `chroma-data`: ChromaDB persistent storage
- `ollama-data`: Ollama models and cache
- `logs-data`: Structured logs from all services
- `mongo-data`: MongoDB database files (Qwen chat history)

### Bind Mounts
- `./services/rag-api:/app` - RAG API code (development)
- `./services/mcp-gateway:/app` - MCP Gateway code (development)
- `./data:/data` - Shared data directory

## Security

### Isolation
- All services run in isolated Docker network
- No direct host access except through exposed ports
- Resource limits prevent resource exhaustion

### Secrets Management
- Environment variables in `.env` (gitignored)
- Docker secrets for sensitive data (optional)
- No hardcoded credentials

### Logging
- Structured JSON logs
- Rotating file handlers (10MB max, 5 backups)
- No PII in logs

## Scalability

### Horizontal Scaling
- RAG API can be scaled with load balancer
- ChromaDB supports clustering (enterprise)
- Ollama can run on multiple GPUs

### Vertical Scaling
- Adjust resource limits in docker-compose.yml
- Use larger models for better quality
- Increase chunk size for longer context

## Monitoring

### Health Checks
- Built-in health endpoints
- Docker health checks
- PowerShell monitoring scripts

### Metrics
- Request latency
- Document count
- Model inference time
- Memory/CPU usage (Docker stats)

## Extensibility

### Adding New Models
1. Pull model: `docker exec ai-ollama ollama pull <model>`
2. Update RAG API to use new model
3. Restart services

### Adding New Document Types
1. Add loader in `rag_engine.py`
2. Update file type list
3. Test ingestion

### Custom MCP Tools
1. Add tool definition in `mcp-gateway/index.js`
2. Implement handler
3. Restart MCP gateway

## Backup & Recovery

### Backup Strategy
- Automated backups via `scripts/backup.ps1`
- Git-tracked configurations
- Volume snapshots for data

### Recovery
- Rollback via `scripts/rollback.ps1`
- Point-in-time recovery from backups
- Idempotent bootstrap process
