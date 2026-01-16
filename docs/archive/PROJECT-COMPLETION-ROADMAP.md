# 🎯 AI Combiner Stack - Project Completion Roadmap

**Original Vision Date:** Start of project  
**Current Status Date:** 2026-01-16  
**Progress:** ~75% Complete

---

## 📊 Original Goals vs Current Status

### ✅ COMPLETED (75%)

| Component | Original Goal | Current Status | Notes |
|-----------|--------------|----------------|-------|
| **MCP Gateway** | MCP protocol for Kiro IDE | ✅ Working | Port 9002, integrated with RAG |
| **RAG Pipeline** | Offline-first, local LLMs | ✅ Working | ChromaDB + Ollama + 19K docs |
| **Local LLM** | Qwen via MCP | ✅ Working | Qwen2.5-Coder 7B loaded |
| **Vector DB** | ChromaDB/LanceDB | ✅ Working | ChromaDB PersistentClient |
| **Document Ingestion** | PDF/Markdown/Code | ✅ Working | 19,103 docs from Qwen history |
| **Docker Isolation** | All services in containers | ✅ Working | Network: ai-local-net |
| **Windows Compatibility** | PS scripts, path handling | ✅ Working | All scripts in PowerShell |
| **Observability** | Logs + metrics | ⚠️ Partial | Logs working, Prometheus added but not tested |
| **MongoDB** | Chat history storage | ✅ Working | Qwen history imported |
| **Kiro IDE Integration** | MCP tools in IDE | ✅ Working | qwen_chat, rag_query tested |

### ⚠️ PARTIAL (15%)

| Component | Original Goal | Current Status | Action Needed |
|-----------|--------------|----------------|---------------|
| **ss-API** | Structured Semantic API | ⚠️ Basic | Need /modify_arch endpoint |
| **Prometheus** | Metrics collection | ⚠️ Added | Not tested, no dashboards |
| **Grafana** | Visualization | ⚠️ Added | Not configured |
| **Redis** | Caching layer | ⚠️ Added | Not integrated with RAG |
| **Hybrid Search** | Dense + sparse scoring | ⚠️ Basic | Only dense embeddings now |

### ❌ MISSING (10%)

| Component | Original Goal | Current Status | Priority |
|-----------|--------------|----------------|----------|
| **Self-Arch-Modify Engine** | NL → Docker patches | ❌ Missing | 🔥 HIGH |
| **Architecture Versioning** | Git-backed state history | ❌ Missing | 🔥 HIGH |
| **Reranker** | BGE-Reranker-v2-Mini | ❌ Missing | 🟡 MEDIUM |
| **Semantic Chunking** | Context-aware splitting | ❌ Missing | 🟡 MEDIUM |
| **Encrypted Logs** | Rotating encrypted logs | ❌ Missing | 🟢 LOW |
| **Auto-rollback** | Safe architecture changes | ❌ Missing | 🔥 HIGH |

---

## 🚀 Phase 1: Complete Core Features (Priority: HIGH)

### 1.1 Self-Architecture Modification Engine

**Goal:** Accept NL prompts → generate Docker Compose patches → apply with confirmation

**Implementation:**
```powershell
# New service: arch-engine
services/arch-engine/
  ├── Dockerfile
  ├── engine.py          # Main orchestrator
  ├── parsers/
  │   ├── intent.py      # NL → structured intent
  │   └── docker.py      # Docker Compose manipulation
  ├── generators/
  │   ├── compose.py     # Generate service definitions
  │   └── config.py      # Generate configs
  └── validators/
      ├── safety.py      # Sandbox checks
      └── resources.py   # CPU/MEM limits
```

**API Endpoints:**
```
POST /arch/propose
  Body: {"prompt": "Add BGE reranker service"}
  Returns: {"diff": "...", "preview": "...", "safe": true}

POST /arch/apply
  Body: {"change_id": "abc123", "confirm": true}
  Returns: {"status": "applied", "rollback_id": "xyz789"}

POST /arch/rollback
  Body: {"rollback_id": "xyz789"}
  Returns: {"status": "rolled_back"}

GET /arch/history
  Returns: [{"id": "...", "prompt": "...", "timestamp": "..."}]
```

**Example Workflow:**
```powershell
# User in Kiro IDE:
@kiro add a reranker service using BGE-Reranker-v2-Mini

# Arch Engine:
1. Parse intent → {action: "add_service", type: "reranker", model: "BGE-Reranker-v2-Mini"}
2. Generate docker-compose patch:
   ```yaml
   reranker:
     image: ghcr.io/bge-reranker-v2-mini:latest
     networks: [ai-local-net]
     ports: ["9003:8003"]
   ```
3. Show diff to user
4. User confirms → apply
5. Save to git: git commit -m "Add reranker service"
```

### 1.2 Architecture Versioning

**Goal:** Git-backed history of all architecture changes

**Implementation:**
```powershell
# New directory structure
.arch-history/
  ├── states/
  │   ├── 2026-01-16-initial.yml
  │   ├── 2026-01-16-add-reranker.yml
  │   └── 2026-01-17-add-redis-cache.yml
  ├── diffs/
  │   ├── 001-add-reranker.diff
  │   └── 002-add-redis-cache.diff
  └── metadata.json
```

**Git Integration:**
```powershell
# Auto-commit on every architecture change
git add docker-compose.yml .arch-history/
git commit -m "[arch-engine] $prompt"
git tag "arch-$(date +%s)"
```

**Rollback Script:**
```powershell
# scripts/arch-rollback.ps1
param([string]$StateId)

# Find state file
$stateFile = ".arch-history/states/$StateId.yml"

# Copy to docker-compose.yml
Copy-Item $stateFile docker-compose.yml

# Restart stack
docker compose down
docker compose up -d

Write-Host "Rolled back to state: $StateId"
```

### 1.3 Safety Guardrails

**Sandbox Checks:**
- ✅ No modifications outside `./ai-combiner/` workspace
- ✅ No privileged containers
- ✅ No host network mode
- ✅ CPU/MEM limits enforced
- ✅ No volume mounts to system directories

**Validation Before Apply:**
```python
def validate_change(compose_patch):
    checks = [
        check_no_privileged(),
        check_resource_limits(),
        check_network_isolation(),
        check_volume_safety(),
        check_port_conflicts()
    ]
    return all(checks)
```

---

## 🎯 Phase 2: Enhance Existing Features (Priority: MEDIUM)

### 2.1 Hybrid Search (Dense + Sparse)

**Current:** Only dense embeddings (ChromaDB)  
**Goal:** Add BM25 sparse retrieval + fusion

**Implementation:**
```python
# services/rag-api/hybrid_search.py
from rank_bm25 import BM25Okapi

class HybridRetriever:
    def __init__(self):
        self.dense = ChromaDBRetriever()
        self.sparse = BM25Retriever()
    
    def search(self, query, top_k=5):
        # Dense results
        dense_results = self.dense.search(query, top_k=20)
        
        # Sparse results
        sparse_results = self.sparse.search(query, top_k=20)
        
        # Reciprocal Rank Fusion
        fused = self.rrf_fusion(dense_results, sparse_results)
        
        return fused[:top_k]
```

### 2.2 Reranker Integration

**Goal:** Add BGE-Reranker-v2-Mini for better relevance

**Docker Service:**
```yaml
reranker:
  image: ghcr.io/bge-reranker-v2-mini:latest
  container_name: ai-reranker
  networks:
    - ai-local-net
  ports:
    - "9003:8003"
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 2G
```

**RAG API Integration:**
```python
# After initial retrieval, rerank top 20 → return top 5
results = chroma.search(query, top_k=20)
reranked = reranker.rerank(query, results)
return reranked[:5]
```

### 2.3 Semantic Chunking

**Current:** Fixed-size chunks (1000 tokens)  
**Goal:** Context-aware splitting (sentence boundaries, code blocks)

**Implementation:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
    keep_separator=True
)
```

---

## 🔧 Phase 3: Observability & Production (Priority: LOW)

### 3.1 Prometheus + Grafana

**Goal:** Full metrics stack with dashboards

**Metrics to Track:**
- RAG query latency (p50, p95, p99)
- Ollama inference time
- ChromaDB search time
- Document ingestion rate
- Cache hit rate (Redis)
- Container resource usage

**Grafana Dashboards:**
- AI Combiner Overview
- RAG Performance
- LLM Inference Metrics
- System Resources

### 3.2 Redis Caching

**Goal:** Cache frequent queries and embeddings

**Integration:**
```python
# Cache query results
@cache(ttl=3600)
def rag_query(query: str):
    return chroma.search(query)

# Cache embeddings
@cache(ttl=86400)
def get_embedding(text: str):
    return ollama.embed(text)
```

### 3.3 Encrypted Logs

**Goal:** Rotating, encrypted logs with retention policy

**Implementation:**
```python
import logging
from cryptography.fernet import Fernet

class EncryptedRotatingFileHandler(RotatingFileHandler):
    def emit(self, record):
        msg = self.format(record)
        encrypted = fernet.encrypt(msg.encode())
        self.stream.write(encrypted + b'\n')
```

---

## 📋 Implementation Priority

### Week 1: Core Self-Modification
- [ ] Arch Engine service skeleton
- [ ] Intent parser (NL → structured)
- [ ] Docker Compose generator
- [ ] Safety validators
- [ ] Git-backed versioning

### Week 2: Architecture Management
- [ ] `/arch/propose` endpoint
- [ ] `/arch/apply` with confirmation
- [ ] `/arch/rollback` mechanism
- [ ] `/arch/history` viewer
- [ ] PowerShell integration scripts

### Week 3: Enhanced RAG
- [ ] Hybrid search (dense + sparse)
- [ ] Reranker service
- [ ] Semantic chunking
- [ ] Redis caching

### Week 4: Observability
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Encrypted logs
- [ ] Performance tuning

---

## 🎉 Success Criteria

### Minimum Viable Product (MVP)
- ✅ RAG pipeline working (DONE)
- ✅ Local LLM inference (DONE)
- ✅ MCP integration (DONE)
- ✅ Docker isolation (DONE)
- ⚠️ Self-arch-modify (IN PROGRESS)

### Production Ready
- ⚠️ Architecture versioning
- ⚠️ Rollback mechanism
- ⚠️ Observability stack
- ⚠️ Performance optimization

### Advanced Features
- ❌ Hybrid search
- ❌ Reranker
- ❌ Semantic chunking
- ❌ Encrypted logs

---

## 🚀 Next Immediate Steps

1. **Create Arch Engine Service**
   ```powershell
   mkdir services/arch-engine
   # Implement intent parser + Docker generator
   ```

2. **Add Architecture Versioning**
   ```powershell
   mkdir .arch-history
   git init .arch-history
   ```

3. **Test Self-Modification**
   ```powershell
   curl -X POST http://localhost:9004/arch/propose \
     -d '{"prompt": "Add Redis cache service"}'
   ```

4. **Integrate with Kiro IDE**
   ```
   @kiro modify architecture: add reranker service
   ```

---

## 📊 Current vs Target Architecture

### Current (75% Complete)
```
[Kiro IDE] <--MCP--> [Qwen MCP]
     |                      |
     +--MCP--> [MCP Gateway :9002]
                      |
                      v
              [RAG API :9001]
                      |
         +------------+------------+
         v                         v
    [Ollama :11434]         [ChromaDB]
         |
         v
    [Qwen2.5-Coder 7B]
```

### Target (100% Complete)
```
[Kiro IDE] <--MCP--> [Qwen MCP]
     |                      |
     +--MCP--> [MCP Gateway :9002]
                      |
         +------------+------------+
         v                         v
   [Arch Engine :9004]      [RAG API :9001]
         |                         |
         v                +--------+--------+
   [Git History]          v                 v
   [Rollback]      [Ollama :11434]    [ChromaDB]
                         |                  |
                         v                  v
                  [Qwen2.5-Coder]    [Reranker :9003]
                         |
                         v
                   [Redis Cache :6379]
                         |
                         v
                  [Prometheus :9090]
                         |
                         v
                   [Grafana :3000]
```

---

## 💡 Philosophy Alignment

**Original Vision:**
> "This system embodies embodied intelligence — it reasons about its own structure as data, and evolves only through reflective, user-guided agency."

**Current Implementation:**
✅ Reasons about structure (RAG over own configs)  
✅ User-guided (MCP prompts from Kiro)  
⚠️ Self-modification (needs Arch Engine)  
✅ Reflective (logs, metrics, history)

**Missing Piece:** The Arch Engine is the key to true "embodied intelligence" - the system must be able to modify its own Docker Compose, validate changes, and roll back safely.

---

**Status:** Ready to implement Phase 1 (Self-Arch-Modify Engine)  
**Estimated Time:** 2-3 weeks for full completion  
**Current Progress:** 75% → Target: 100%
