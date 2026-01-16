# AI Combiner Stack - Complete Demo

## 🎯 What is AI Combiner Stack?

A local AI system that combines:
- **RAG (Retrieval Augmented Generation)** - Search your knowledge base
- **Qwen Chat** - Powerful AI assistant
- **MCP Integration** - Seamless Kiro IDE integration
- **Your Chat History** - 19,103+ documents from your Qwen conversations

## 🏗️ Architecture

```
┌─────────────┐
│  Kiro IDE   │ ← You work here
└──────┬──────┘
       │ MCP Protocol
       ├──────────────────┐
       │                  │
       v                  v
┌─────────────┐    ┌─────────────┐
│ Qwen MCP    │    │  RAG MCP    │
│  Server     │    │   Server    │
└──────┬──────┘    └──────┬──────┘
       │                  │
       v                  v
┌─────────────┐    ┌─────────────┐
│ Qwen Chat   │    │  RAG API    │
│ :3000       │    │  :9001      │
└─────────────┘    └──────┬──────┘
                          │
                          v
                   ┌─────────────┐
                   │  ChromaDB   │
                   │  + Ollama   │
                   └─────────────┘
```

## 🚀 How It Works

### 1. **RAG Search** (Memory Layer)
```powershell
# Search your Qwen history
curl -X POST http://localhost:9001/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Docker setup", "top_k": 5}'
```

**Result**: Finds relevant conversations from your 19,103 documents

### 2. **Qwen Chat** (Intelligence Layer)
```powershell
# Ask Qwen (via MCP in Kiro)
@kiro ask Qwen to create a Flask app
```

**Result**: Qwen generates code/answers

### 3. **Combined Power** (RAG + Qwen)
```powershell
# In Kiro IDE
@kiro search my Docker notes and create docker-compose for Python app
```

**What happens**:
1. Kiro calls `rag_query("Docker Python")`
2. Gets context from YOUR previous conversations
3. Calls `qwen_chat()` with context + your question
4. Qwen responds with **personalized, context-aware** answer

## 💡 Real Examples

### Example 1: Code Generation with Memory

**Without RAG**:
```
You: "Create a Flask app"
Qwen: "Here's a generic Flask example..."
```

**With RAG**:
```
You: "Create a Flask app"
Kiro: [searches your history, finds you prefer port 5000, alpine images]
Qwen: "Based on your previous setup, here's a Flask app on port 5000 
       with alpine base image, matching your coding style..."
```

### Example 2: Learning from Your History

**Scenario**: You forgot how you solved a problem 3 months ago

```
You: "How did I set up Docker networking last time?"
Kiro: [searches 19,103 documents]
      [finds conversation from 3 months ago]
      "You used bridge network with custom subnet 172.20.0.0/16..."
```

## 📊 Current Stats

- **Documents in RAG**: 19,103
- **Qwen Chats Imported**: 331
- **Search Speed**: ~200-300ms
- **Services Running**: RAG API ✓, Ollama ✓

## 🎮 Usage in Kiro IDE

### Via MCP Tools:

1. **Search History**:
   ```
   @kiro use rag_query to find my Python examples
   ```

2. **Ask Qwen**:
   ```
   @kiro use qwen_chat to explain async/await
   ```

3. **Combined**:
   ```
   @kiro find my Docker notes and ask Qwen to improve them
   ```

## 🔧 Quick Commands

### Check Status:
```powershell
.\scripts\full-system-check.ps1
```

### Test RAG Search:
```powershell
.\scripts\test-qwen-history-search.ps1
```

### Demo Full Stack:
```powershell
.\scripts\demo-full-stack.ps1
```

### Real Scenario Demo:
```powershell
.\scripts\demo-real-scenario.ps1
```

## 🎯 Key Benefits

1. **Memory**: AI remembers ALL your conversations (19,103 docs)
2. **Context-Aware**: Answers personalized to YOUR style
3. **Local**: Everything runs on your machine
4. **Fast**: Search in ~200ms
5. **Integrated**: Works seamlessly in Kiro IDE via MCP

## 🔄 Workflow Example

```
1. You: "Create a web scraper"
   
2. Kiro searches your history:
   - Finds you used BeautifulSoup before
   - Finds you prefer async requests
   - Finds your error handling patterns
   
3. Qwen generates code:
   - Uses BeautifulSoup (your preference)
   - Implements async (your style)
   - Includes error handling (your pattern)
   
4. Result: Code that matches YOUR coding style!
```

## 📈 What's Imported

From your Qwen export (`chat-export-1768528571495.json`):
- 331 chats
- Topics: Docker, Python, AI, Physics, Music, Philosophy, etc.
- All searchable and available as context

## 🎊 The Magic

**Traditional AI**: Generic answers, no memory

**AI Combiner Stack**: 
- Remembers everything you discussed
- Learns your preferences
- Provides personalized answers
- Combines search + generation
- All local, all private

---

**Your AI now has a MEMORY! 🧠**
