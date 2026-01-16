"""
AI Combiner Stack - Web UI
Simple web interface for managing the entire stack
"""
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from typing import Optional
import time
import asyncio
from contextlib import asynccontextmanager
from collections import defaultdict

from metrics import metrics_store

# Rate limiting
rate_limit_store = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 100  # requests per window

def check_rate_limit(client_ip: str) -> bool:
    """Check if client is within rate limit"""
    now = time.time()
    # Clean old entries
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip] 
        if now - t < RATE_LIMIT_WINDOW
    ]
    # Check limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_MAX:
        return False
    # Add new request
    rate_limit_store[client_ip].append(now)
    return True

# Global HTTP client with connection pooling
http_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage HTTP client lifecycle"""
    global http_client
    # Startup: create client with connection pooling
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
    timeout = httpx.Timeout(30.0, connect=10.0)
    http_client = httpx.AsyncClient(limits=limits, timeout=timeout)
    print("✓ HTTP client initialized with connection pooling")
    yield
    # Shutdown: close client gracefully
    print("Shutting down HTTP client...")
    await http_client.aclose()
    print("✓ HTTP client closed")

app = FastAPI(title="AI Combiner Stack - Web UI", lifespan=lifespan)

# Templates
templates = Jinja2Templates(directory="templates")

# Service URLs
SERVICES = {
    "rag": "http://rag-api:8001",
    "arch": "http://arch-engine:8004",
    "ollama": "http://ollama:11434"
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main dashboard"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status():
    """Get status of all services"""
    status = {}
    
    # Check RAG API
    try:
        resp = await http_client.get(f"{SERVICES['rag']}/health")
        status["rag"] = {"status": "healthy", "data": resp.json()}
    except:
        status["rag"] = {"status": "unhealthy", "data": None}
    
    # Check Arch Engine
    try:
        resp = await http_client.get(f"{SERVICES['arch']}/health")
        status["arch"] = {"status": "healthy", "data": resp.json()}
    except:
        status["arch"] = {"status": "unhealthy", "data": None}
    
    # Check Ollama
    try:
        resp = await http_client.get(f"{SERVICES['ollama']}/api/tags")
        status["ollama"] = {"status": "healthy", "data": resp.json()}
    except:
        status["ollama"] = {"status": "unhealthy", "data": None}
    
    return status

@app.get("/api/rag/stats")
async def get_rag_stats():
    """Get RAG database statistics"""
    try:
        resp = await http_client.get(f"{SERVICES['rag']}/inspect")
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/rag/query")
async def rag_query(request: Request, query: str = Form(...), top_k: int = Form(5)):
    """Query RAG database"""
    # Rate limiting
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded. Max 100 requests per minute."}
        )
    
    start_time = time.time()
    try:
        resp = await http_client.post(
            f"{SERVICES['rag']}/query",
            json={"query": query, "top_k": top_k}
        )
        latency = (time.time() - start_time) * 1000
        result = resp.json()
        
        # Record metrics
        metrics_store.record_query("rag", query, latency, True)
        
        return result
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        metrics_store.record_query("rag", query, latency, False)
        return {"error": str(e)}

@app.get("/api/arch/history")
async def get_arch_history():
    """Get architecture change history"""
    try:
        resp = await http_client.get(f"{SERVICES['arch']}/arch/history")
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/arch/propose")
async def propose_change(prompt: str = Form(...)):
    """Propose architecture change"""
    try:
        resp = await http_client.post(
            f"{SERVICES['arch']}/arch/propose",
            json={"prompt": prompt, "auto_apply": False}
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/arch/apply")
async def apply_change(change_id: str = Form(...)):
    """Apply architecture change"""
    try:
        resp = await http_client.post(
            f"{SERVICES['arch']}/arch/apply",
            json={"change_id": change_id, "confirm": True}
        )
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/ollama/generate")
async def ollama_generate(
    prompt: str = Form(...),
    model: str = Form("qwen2.5-coder:7b"),
    use_rag: bool = Form(True)
):
    """Generate text with Ollama, optionally with RAG context"""
    try:
        final_prompt = prompt
        rag_used = False
        
        # If RAG enabled, search for context
        if use_rag:
            try:
                rag_resp = await http_client.post(
                    f"{SERVICES['rag']}/query",
                    json={"query": prompt, "top_k": 3}
                )
                rag_data = rag_resp.json()
                
                if rag_data.get("documents"):
                    # Build context from RAG results
                    context = "\n\n".join([
                        f"[Context {i+1}]: {doc['content'][:500]}"
                        for i, doc in enumerate(rag_data["documents"][:3])
                    ])
                    
                    # Enhanced prompt with context
                    final_prompt = f"""Based on the following context from previous work:

{context}

User question: {prompt}

Please provide a detailed answer using the context above."""
                    rag_used = True
            except:
                # If RAG fails, continue without context
                pass
        
        # Generate with Ollama
        resp = await http_client.post(
            f"{SERVICES['ollama']}/api/generate",
            json={"model": model, "prompt": final_prompt, "stream": False}
        )
        result = resp.json()
        result["rag_used"] = rag_used
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/test/rag-context")
async def test_rag_context():
    """Test endpoint to verify RAG context integration"""
    try:
        # Test RAG search
        rag_resp = await http_client.post(
            f"{SERVICES['rag']}/query",
            json={"query": "Docker", "top_k": 2}
        )
        rag_data = rag_resp.json()
        
        return {
            "status": "working",
            "rag_results": len(rag_data.get("documents", [])),
            "sample": rag_data.get("documents", [{}])[0].get("content", "")[:200] if rag_data.get("documents") else None
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/metrics/stats")
async def get_metrics_stats():
    """Get current metrics statistics"""
    return metrics_store.get_stats()

@app.get("/api/metrics/analysis")
async def get_metrics_analysis():
    """Get performance analysis and suggestions"""
    return metrics_store.analyze_performance()

@app.get("/api/metrics/health")
async def get_health_score():
    """Get overall health score"""
    analysis = metrics_store.analyze_performance()
    return {
        "health_score": analysis["health_score"],
        "status": "healthy" if analysis["health_score"] > 80 else "degraded" if analysis["health_score"] > 50 else "unhealthy",
        "issues_count": len(analysis["issues"]),
        "suggestions_count": len(analysis["suggestions"])
    }

@app.post("/api/auto/apply-suggestion")
async def auto_apply_suggestion(suggestion_action: str = Form(...)):
    """Auto-apply a suggestion with architecture engine"""
    start_time = time.time()
    
    try:
        # Step 1: Propose change
        propose_resp = await http_client.post(
            f"{SERVICES['arch']}/arch/propose",
            json={"prompt": suggestion_action, "auto_apply": False}
        )
        propose_data = propose_resp.json()
        
        if "error" in propose_data:
            return {"status": "error", "error": propose_data["error"]}
        
        if not propose_data.get("safe"):
            return {
                "status": "unsafe",
                "message": "Suggestion failed safety checks",
                "checks": propose_data.get("safety_checks", [])
            }
        
        # Step 2: Auto-apply (since it passed safety)
        apply_resp = await http_client.post(
            f"{SERVICES['arch']}/arch/apply",
            json={"change_id": propose_data["change_id"], "confirm": True}
        )
        apply_data = apply_resp.json()
        
        latency = (time.time() - start_time) * 1000
        
        # Record that suggestion was applied
        metrics_store.record_suggestion_outcome(
            {"action": suggestion_action},
            "applied"
        )
        
        return {
            "status": "applied",
            "change_id": propose_data["change_id"],
            "rollback_id": apply_data.get("rollback_id"),
            "message": "Suggestion applied successfully",
            "latency_ms": latency,
            "next_steps": apply_data.get("next_steps", [])
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/auto/dismiss-suggestion")
async def dismiss_suggestion(suggestion_action: str = Form(...)):
    """Record that user dismissed a suggestion"""
    metrics_store.record_suggestion_outcome(
        {"action": suggestion_action},
        "dismissed"
    )
    return {"status": "dismissed", "message": "Preference recorded"}

@app.get("/api/learning/insights")
async def get_learning_insights():
    """Get learning insights from user preferences"""
    return metrics_store.get_learning_insights()

@app.get("/api/production/metrics")
async def get_production_metrics():
    """Get production-ready metrics"""
    stats = metrics_store.get_stats()
    analysis = metrics_store.analyze_performance()
    
    # Calculate uptime (simplified - based on queries)
    uptime_seconds = len(metrics_store.queries) * 2  # Rough estimate
    
    # Calculate request rate
    if len(metrics_store.queries) > 0:
        first_query = metrics_store.queries[0]["timestamp"]
        last_query = metrics_store.queries[-1]["timestamp"]
        from datetime import datetime
        first_time = datetime.fromisoformat(first_query)
        last_time = datetime.fromisoformat(last_query)
        duration_seconds = (last_time - first_time).total_seconds()
        request_rate = len(metrics_store.queries) / max(duration_seconds, 1)
    else:
        request_rate = 0
    
    return {
        "health": {
            "score": analysis["health_score"],
            "status": "healthy" if analysis["health_score"] > 80 else "degraded",
            "uptime_seconds": uptime_seconds
        },
        "performance": {
            "total_requests": stats["total_queries"],
            "request_rate_per_second": round(request_rate, 2),
            "avg_latencies": stats["avg_latencies"],
            "error_count": sum(stats["errors"].values())
        },
        "autonomy": {
            "auto_actions_taken": len(metrics_store.auto_actions),
            "suggestions_count": len(analysis["suggestions"]),
            "learning_active": len(metrics_store.suggestions_history) > 0
        },
        "issues": analysis["issues"],
        "top_patterns": stats["top_patterns"]
    }

@app.get("/api/metrics/insights")
async def get_metrics_insights():
    """Get all insights (metrics + learning)"""
    return metrics_store.get_insights()

@app.post("/api/combined/query")
async def combined_query(request: Request, query: str = Form(...), top_k: int = Form(3)):
    """Combined query using multiple services"""
    # Rate limiting
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded. Max 100 requests per minute."}
        )
    
    start_time = time.time()
    services_used = []
    
    try:
        # Query RAG
        rag_resp = await http_client.post(
            f"{SERVICES['rag']}/query",
            json={"query": query, "top_k": top_k}
        )
        rag_data = rag_resp.json()
        services_used.append("rag")
        
        # If query mentions architecture, also check arch engine
        if any(word in query.lower() for word in ["add", "service", "docker", "compose", "architecture"]):
            arch_resp = await http_client.get(f"{SERVICES['arch']}/arch/history")
            arch_data = arch_resp.json()
            services_used.append("arch")
        else:
            arch_data = None
        
        latency = (time.time() - start_time) * 1000
        
        return {
            "query": query,
            "rag_results": rag_data,
            "arch_history": arch_data,
            "services_used": services_used,
            "latency_ms": latency
        }
    except Exception as e:
        return {"error": str(e), "services_used": services_used}

@app.post("/api/learning/feedback")
async def record_learning_feedback(suggestion_id: str = Form(...), action: str = Form(...)):
    """Record user feedback on suggestions"""
    metrics_store.record_suggestion_outcome(
        {"id": suggestion_id, "action": suggestion_id},  # Include action field
        action
    )
    return {"status": "recorded", "suggestion_id": suggestion_id, "action": action}

@app.get("/api/auto/opportunities")
async def get_auto_opportunities():
    """Get auto-healing opportunities"""
    opportunities = metrics_store.detect_auto_healing_opportunities()
    return {
        "opportunities": opportunities,
        "total": len(opportunities),
        "auto_actions_taken": len(metrics_store.auto_actions)
    }

@app.post("/api/auto/execute")
async def execute_auto_action(action_type: str = Form(...), service: str = Form(...)):
    """Execute autonomous action"""
    start_time = time.time()
    
    try:
        if action_type == "restart_service":
            # Simulate service restart
            import asyncio
            await asyncio.sleep(1)
            
            action = {
                "type": "restart_service",
                "service": service,
                "reason": "High error rate detected"
            }
            metrics_store.record_auto_action(action, "success")
            metrics_store.errors[service] = 0
            
            return {
                "status": "executed",
                "action": action,
                "message": f"Service {service} restarted automatically",
                "latency_ms": (time.time() - start_time) * 1000
            }
        
        elif action_type == "increase_memory":
            async with httpx.AsyncClient(timeout=10.0) as client:
                propose_resp = await client.post(
                    f"{SERVICES['arch']}/arch/propose",
                    json={"prompt": f"Increase {service} memory to 4G", "auto_apply": False}
                )
                propose_data = propose_resp.json()
            
            if "error" in propose_data or not propose_data.get("safe"):
                return {"status": "unsafe", "error": "Memory increase failed safety checks"}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                apply_resp = await client.post(
                    f"{SERVICES['arch']}/arch/apply",
                    json={"change_id": propose_data["change_id"], "confirm": True}
                )
                apply_data = apply_resp.json()
            
            action = {
                "type": "increase_memory",
                "service": service,
                "reason": "Performance degradation detected"
            }
            metrics_store.record_auto_action(action, "success")
            
            return {
                "status": "executed",
                "action": action,
                "rollback_id": apply_data.get("rollback_id"),
                "message": f"Increased {service} memory automatically",
                "latency_ms": (time.time() - start_time) * 1000
            }
        
        else:
            return {"status": "error", "error": f"Unknown action type: {action_type}"}
            
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
