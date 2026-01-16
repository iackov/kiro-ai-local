# 🧠 Architecture Engine - Self-Modifying AI Stack

**Status:** Ready for testing  
**Date:** 2026-01-16  
**Component:** Self-Architecture Modification Engine

---

## 🎯 What is Architecture Engine?

The **Architecture Engine** is the missing piece that enables your AI Combiner Stack to **modify its own structure** through natural language prompts. It's the embodiment of "self-arch-modify by user prompt" from the original vision.

### Key Features

✅ **Natural Language → Docker Compose**  
   - "Add Redis cache service" → generates service definition
   - "Change Ollama memory to 16GB" → modifies resource limits
   - "Remove Grafana" → safely removes service

✅ **Safety Guardrails**  
   - No privileged containers
   - Resource limits enforced
   - No system directory mounts
   - Network isolation validated

✅ **Git-Backed Versioning**  
   - Every change committed to git
   - Tagged with rollback ID
   - Full history tracking

✅ **Rollback Mechanism**  
   - Instant rollback to any previous state
   - Automatic backups before changes
   - Safe failure recovery

---

## 🏗️ Architecture

```
[User in Kiro IDE]
       |
       v
"Add Redis cache service"
       |
       v
[Arch Engine :9004]
       |
   +---+---+
   |       |
   v       v
[Intent] [Safety]
Parser   Validator
   |       |
   +---+---+
       |
       v
[Compose Generator]
       |
       v
[Git Manager]
       |
       v
docker-compose.yml (modified)
```

---

## 🚀 Setup

### 1. Build and Start Arch Engine

```powershell
# Build the service
docker compose build arch-engine

# Start it
docker compose up -d arch-engine

# Check status
docker compose ps arch-engine
```

### 2. Verify Health

```powershell
curl http://localhost:9004/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "arch-engine"
}
```

### 3. Initialize Git History

```powershell
# Create history directory
mkdir .arch-history
cd .arch-history
git init
cd ..

# Commit current state
git add docker-compose.yml
git commit -m "Initial architecture state"
```

---

## 📖 Usage

### Example 1: Add Redis Cache

```powershell
.\scripts\test-arch-engine.ps1 -Prompt "Add Redis cache service"
```

**What happens:**
1. Intent parser extracts: `{action: "add", type: "service", name: "redis"}`
2. Compose generator creates Redis service definition
3. Safety validator checks resource limits, network isolation
4. Shows you the diff and preview
5. Asks for confirmation
6. Applies change and commits to git
7. Returns rollback ID

**Result:**
```yaml
redis:
  image: redis:7-alpine
  container_name: ai-redis
  networks:
    - ai-local-net
  ports:
    - "6379:6379"
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 1G
  restart: unless-stopped
```

### Example 2: Modify Resource Limits

```powershell
.\scripts\test-arch-engine.ps1 -Prompt "Change Ollama memory to 16G"
```

**Result:**
```diff
- ollama.deploy.resources.limits.memory: 8G
+ ollama.deploy.resources.limits.memory: 16G
```

### Example 3: Remove Service

```powershell
.\scripts\test-arch-engine.ps1 -Prompt "Remove MongoDB service"
```

**Result:**
- Service removed from docker-compose.yml
- Change committed to git
- Rollback ID provided

---

## 🔧 API Reference

### POST /arch/propose

Propose an architecture change without applying it.

**Request:**
```json
{
  "prompt": "Add Redis cache service",
  "auto_apply": false
}
```

**Response:**
```json
{
  "change_id": "abc123def456",
  "intent": {
    "action": "add",
    "type": "service",
    "service_name": "redis"
  },
  "diff": "...",
  "preview": "...",
  "safe": true,
  "safety_checks": [...]
}
```

### POST /arch/apply

Apply a proposed change.

**Request:**
```json
{
  "change_id": "abc123def456",
  "confirm": true
}
```

**Response:**
```json
{
  "status": "applied",
  "rollback_id": "20260116_123456_abc123",
  "next_steps": [
    "Run: docker compose down",
    "Run: docker compose up -d"
  ]
}
```

### POST /arch/rollback

Rollback to a previous state.

**Request:**
```json
{
  "rollback_id": "20260116_123456_abc123"
}
```

**Response:**
```json
{
  "status": "rolled_back",
  "restored_state": "20260116_123456_abc123"
}
```

### GET /arch/history

Get history of architecture changes.

**Response:**
```json
{
  "total": 5,
  "changes": [
    {
      "sha": "a1b2c3d4",
      "message": "Add Redis cache service",
      "timestamp": "2026-01-16T12:34:56",
      "author": "arch-engine"
    }
  ]
}
```

---

## 🛡️ Safety Features

### 1. Sandbox Checks

- ✅ No modifications outside `./ai-combiner/` workspace
- ✅ No privileged containers
- ✅ No host network mode
- ✅ CPU/MEM limits enforced
- ✅ No volume mounts to system directories

### 2. Validation Before Apply

Every change is validated:
- Resource limits (max 8 CPU, 16GB RAM)
- Network isolation (only `ai-local-net`)
- Volume safety (no `/`, `/etc`, `/sys`, etc.)
- No privileged mode
- No host network

### 3. Automatic Backups

Before applying any change:
- Current `docker-compose.yml` backed up
- Backup named: `docker-compose.yml.backup.YYYYMMDD_HHMMSS`
- On failure, backup automatically restored

### 4. Git Versioning

Every change:
- Committed to git with descriptive message
- Tagged with rollback ID
- Includes change metadata
- Full history preserved

---

## 🎮 Integration with Kiro IDE

### Via MCP (Future)

```
@kiro modify architecture: add Redis cache service

[Kiro calls arch-engine via MCP]
  → POST /arch/propose
  → Shows diff in IDE
  → User confirms
  → POST /arch/apply
  → Success!
```

### Via Direct API

```powershell
# In Kiro terminal
curl -X POST http://localhost:9004/arch/propose \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Add Redis cache service"}'
```

---

## 📊 Supported Intents

### Add Service
- "Add Redis cache service"
- "Create a Postgres database"
- "Deploy Nginx proxy"

### Remove Service
- "Remove Grafana"
- "Delete MongoDB service"
- "Stop Redis container"

### Modify Resources
- "Change Ollama memory to 16GB"
- "Set RAG API CPU to 2"
- "Update Ollama memory to 12G"

### Modify Ports
- "Change Ollama port to 11435"
- "Expose RAG API on port 9010"

### Add Volumes
- "Add volume /data/cache to Redis"
- "Mount /logs to Ollama"

---

## 🔄 Workflow Example

### Scenario: Add Redis Cache for RAG API

**Step 1: Propose**
```powershell
curl -X POST http://localhost:9004/arch/propose \
  -d '{"prompt": "Add Redis cache service"}'
```

**Step 2: Review**
```
Change ID: abc123def456
Intent: add service (redis)

Diff:
+ Added service: redis
  image: redis:7-alpine
  ports: ["6379:6379"]
  networks: [ai-local-net]

Safety Checks:
  ✓ no_privileged: OK
  ✓ resource_limits: OK
  ✓ network_isolation: OK
  ✓ volume_safety: OK
  ✓ no_host_network: OK
```

**Step 3: Apply**
```powershell
curl -X POST http://localhost:9004/arch/apply \
  -d '{"change_id": "abc123def456", "confirm": true}'
```

**Step 4: Restart Stack**
```powershell
docker compose down
docker compose up -d
```

**Step 5: Verify**
```powershell
docker compose ps redis
curl http://localhost:6379
```

**Step 6: (Optional) Rollback**
```powershell
curl -X POST http://localhost:9004/arch/rollback \
  -d '{"rollback_id": "20260116_123456_abc123"}'
```

---

## 🧪 Testing

### Test Script

```powershell
.\scripts\test-arch-engine.ps1 -Prompt "Add Redis cache service"
```

### Manual Testing

```powershell
# 1. Propose change
$body = '{"prompt": "Add Redis cache service"}' | ConvertTo-Json
$proposal = Invoke-RestMethod -Uri "http://localhost:9004/arch/propose" `
  -Method Post -Body $body -ContentType "application/json"

# 2. Review
$proposal | ConvertTo-Json -Depth 5

# 3. Apply
$applyBody = @{
  change_id = $proposal.change_id
  confirm = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:9004/arch/apply" `
  -Method Post -Body $applyBody -ContentType "application/json"

# 4. Check history
Invoke-RestMethod -Uri "http://localhost:9004/arch/history"
```

---

## 🐛 Troubleshooting

### Arch Engine not starting

```powershell
# Check logs
docker compose logs arch-engine

# Common issues:
# - Docker socket not mounted
# - Git not initialized
# - Permissions on /host volume
```

### Safety check failed

```
Error: "CPU limit 16 exceeds maximum 8"

Solution: Adjust safety limits in validators/safety.py
```

### Git commit failed

```
Error: "Git commit failed: not a git repository"

Solution:
git init
git add docker-compose.yml
git commit -m "Initial state"
```

### Change not applied

```
Error: "Service 'redis' already exists"

Solution: Remove existing service first or modify instead
```

---

## 🎯 Next Steps

### Phase 1: Core Functionality ✅
- [x] Intent parser
- [x] Compose generator
- [x] Safety validator
- [x] Git manager
- [x] REST API
- [x] Docker integration

### Phase 2: Enhanced Intents
- [ ] Add environment variables
- [ ] Modify network settings
- [ ] Add dependencies
- [ ] Configure healthchecks

### Phase 3: MCP Integration
- [ ] MCP server for arch-engine
- [ ] Kiro IDE commands
- [ ] Interactive diff viewer
- [ ] One-click rollback

### Phase 4: Advanced Features
- [ ] Multi-service changes
- [ ] Conditional modifications
- [ ] Template library
- [ ] Change validation with LLM

---

## 💡 Philosophy

> "This system embodies embodied intelligence — it reasons about its own structure as data, and evolves only through reflective, user-guided agency."

The Architecture Engine is the realization of this vision:

- **Reasons about structure:** Parses docker-compose.yml as data
- **Evolves:** Modifies its own infrastructure
- **Reflective:** Git history, safety checks, rollback
- **User-guided:** Requires confirmation, shows diffs
- **Agency:** Can propose and apply changes autonomously

---

**Status:** Ready for production testing  
**Next:** Test with real scenarios, integrate with Kiro IDE MCP
