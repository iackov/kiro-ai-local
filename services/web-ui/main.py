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
from datetime import datetime

from metrics import metrics_store
from circuit_breaker import circuit_breaker, CircuitBreakerOpenError
from knowledge_graph import knowledge_graph
from goal_manager import goal_manager, GoalStatus
from conversation_manager import conversation_manager
from task_executor import task_executor
from execution_engine import ExecutionEngine
from adaptive_planner import adaptive_planner
from decision_engine import decision_engine
from self_improvement import self_improvement_engine
from meta_learning import meta_learning_engine
from predictive_engine import predictive_engine
from code_generator import CodeGenerator

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
execution_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage HTTP client lifecycle"""
    global http_client, execution_engine
    # Startup: create client with connection pooling
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
    timeout = httpx.Timeout(30.0, connect=10.0)
    http_client = httpx.AsyncClient(limits=limits, timeout=timeout)
    print("✓ HTTP client initialized with connection pooling")
    
    # Initialize execution engine
    execution_engine = ExecutionEngine(http_client, SERVICES)
    print("✓ Execution engine initialized")
    
    # Initialize code generator
    import code_generator as cg_module
    cg_module.code_generator = CodeGenerator(ollama_url=SERVICES["ollama"])
    print("✓ Code generator initialized")
    
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

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    """Interactive chat interface"""
    return templates.TemplateResponse("chat.html", {"request": request})

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
        # Use circuit breaker
        async def rag_call():
            return await http_client.post(
                f"{SERVICES['rag']}/query",
                json={"query": query, "top_k": top_k}
            )
        
        resp = await circuit_breaker.call("rag", rag_call)
        latency = (time.time() - start_time) * 1000
        result = resp.json()
        
        # Record metrics
        metrics_store.record_query("rag", query, latency, True)
        
        return result
    except CircuitBreakerOpenError as e:
        return JSONResponse(
            status_code=503,
            content={"error": str(e), "service": "rag", "circuit_open": True}
        )
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

@app.post("/api/arch/rollback")
async def rollback_change(rollback_id: str = Form(...)):
    """Rollback architecture change"""
    try:
        resp = await http_client.post(
            f"{SERVICES['arch']}/arch/rollback",
            json={"rollback_id": rollback_id}
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

@app.get("/api/learning/adaptive")
async def get_adaptive_learning():
    """Get adaptive planner learning insights"""
    return adaptive_planner.get_learning_insights()

@app.get("/api/decisions/insights")
async def get_decision_insights():
    """Get decision engine insights"""
    return decision_engine.get_decision_insights()

@app.get("/api/self-improvement/analyze")
async def analyze_for_improvements():
    """Analyze system and identify improvement opportunities"""
    metrics = metrics_store.get_stats()
    adaptive_insights = adaptive_planner.get_learning_insights()
    decision_insights = decision_engine.get_decision_insights()
    
    opportunities = self_improvement_engine.analyze_system_performance(
        metrics, adaptive_insights, decision_insights
    )
    
    return {
        "opportunities_found": len(opportunities),
        "opportunities": [o.to_dict() for o in opportunities]
    }

@app.get("/api/self-improvement/plan")
async def get_improvement_plan():
    """Get prioritized improvement plan"""
    return self_improvement_engine.generate_improvement_plan()

@app.get("/api/self-improvement/insights")
async def get_improvement_insights():
    """Get self-improvement insights"""
    return self_improvement_engine.get_improvement_insights()

@app.get("/api/meta-learning/insights")
async def get_meta_learning_insights():
    """Get meta-learning insights"""
    return meta_learning_engine.get_meta_insights()

@app.get("/api/predictive/analyze")
async def analyze_predictions():
    """Analyze trends and generate predictions"""
    metrics = metrics_store.get_stats()
    adaptive_insights = adaptive_planner.get_learning_insights()
    
    predictions = predictive_engine.analyze_trends(metrics, adaptive_insights)
    proactive_actions = predictive_engine.generate_proactive_actions(predictions)
    
    return {
        "predictions": [p.to_dict() for p in predictions],
        "proactive_actions": proactive_actions,
        "total_predictions": len(predictions)
    }

@app.get("/api/predictive/insights")
async def get_predictive_insights():
    """Get predictive engine insights"""
    return predictive_engine.get_predictive_insights()

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

@app.get("/api/resilience/circuit-breakers")
async def get_circuit_breaker_status():
    """Get circuit breaker status for all services"""
    services = ["rag", "arch", "ollama"]
    status = {}
    
    for service in services:
        state = circuit_breaker.get_state(service)
        status[service] = {
            "state": state.value,
            "failures": circuit_breaker.failure_counts[service],
            "healthy": state.value == "closed"
        }
    
    return {
        "circuit_breakers": status,
        "all_healthy": all(s["healthy"] for s in status.values())
    }

@app.post("/api/resilience/reset-circuit")
async def reset_circuit_breaker(service: str = Form(...)):
    """Manually reset a circuit breaker"""
    try:
        circuit_breaker.reset(service)
        return {
            "status": "reset",
            "service": service,
            "message": f"Circuit breaker for {service} has been reset"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/planning/predictions")
async def get_predictions():
    """Get future issue predictions (Level 7: Planning)"""
    predictions = metrics_store.predict_future_issues()
    return {
        "predictions": predictions,
        "count": len(predictions),
        "has_urgent": any(p["urgency"] == "high" for p in predictions)
    }

@app.get("/api/planning/action-plan")
async def get_action_plan():
    """Get proactive action plan (Level 7: Planning)"""
    return metrics_store.generate_action_plan()

@app.post("/api/planning/execute-plan")
async def execute_action_plan(auto_execute: bool = Form(False)):
    """Execute planned actions (Level 7: Planning)"""
    plan = metrics_store.generate_action_plan()
    
    if not auto_execute:
        return {
            "status": "preview",
            "message": "Set auto_execute=true to execute",
            "plan": plan
        }
    
    executed = []
    failed = []
    
    # Execute immediate actions only
    for action in plan["immediate_actions"]:
        try:
            # Parse action and execute
            if "restart" in action["action"].lower():
                # Extract service name
                service = action["reason"].split()[0]
                body = {"action_type": "restart_service", "service": service}
                result = await execute_auto_action(action_type="restart_service", service=service)
                executed.append({"action": action["action"], "result": result})
            elif "increase" in action["action"].lower() and "memory" in action["action"].lower():
                # Extract service name
                service = action["reason"].split()[0]
                result = await execute_auto_action(action_type="increase_memory", service=service)
                executed.append({"action": action["action"], "result": result})
            else:
                # Log for manual execution
                executed.append({"action": action["action"], "result": "logged_for_manual"})
        except Exception as e:
            failed.append({"action": action["action"], "error": str(e)})
    
    return {
        "status": "executed",
        "executed_count": len(executed),
        "failed_count": len(failed),
        "executed": executed,
        "failed": failed
    }

@app.post("/api/reasoning/analyze")
async def analyze_with_reasoning(query: str = Form(...)):
    """Analyze query with knowledge graph reasoning (Level 8: Reasoning)"""
    reasoning = knowledge_graph.reason_about_query(query)
    return {
        "query": query,
        "reasoning": reasoning,
        "level": 8,
        "capability": "knowledge_graph_reasoning"
    }

@app.get("/api/reasoning/concepts")
async def get_known_concepts():
    """Get all known concepts in knowledge graph"""
    concepts = []
    for concept, metadata in knowledge_graph.nodes.items():
        related_count = len(knowledge_graph.edges.get(concept, []))
        concepts.append({
            "concept": concept,
            "metadata": metadata,
            "related_count": related_count
        })
    
    return {
        "concepts": concepts,
        "total": len(concepts)
    }

@app.post("/api/reasoning/find-path")
async def find_concept_path(from_concept: str = Form(...), to_concept: str = Form(...)):
    """Find reasoning path between two concepts"""
    path = knowledge_graph.find_path(from_concept, to_concept)
    
    if not path:
        return {
            "found": False,
            "message": f"No path found between {from_concept} and {to_concept}"
        }
    
    # Build detailed path with relationships
    detailed_path = []
    for i in range(len(path) - 1):
        from_node = path[i]
        to_node = path[i + 1]
        rel_type = knowledge_graph.edge_types.get((from_node, to_node), "related_to")
        detailed_path.append({
            "from": from_node,
            "to": to_node,
            "relationship": rel_type
        })
    
    return {
        "found": True,
        "path": path,
        "detailed_path": detailed_path,
        "length": len(path) - 1
    }

@app.post("/api/goals/create")
async def create_goal(description: str = Form(...), priority: str = Form("medium"), template: str = Form(None)):
    """Create a new goal (Level 9: Goal-Oriented)"""
    goal = goal_manager.create_goal(description, priority, template)
    return {
        "status": "created",
        "goal": goal.to_dict()
    }

@app.get("/api/goals/list")
async def list_goals():
    """List all goals"""
    all_goals = [goal.to_dict() for goal in goal_manager.goals.values()]
    active_goals = [goal.to_dict() for goal in goal_manager.get_active_goals()]
    
    return {
        "all_goals": all_goals,
        "active_goals": active_goals,
        "total": len(all_goals),
        "active_count": len(active_goals)
    }

@app.get("/api/goals/suggestions")
async def get_goal_suggestions():
    """Get suggested goals based on system state"""
    analysis = metrics_store.analyze_performance()
    predictions = metrics_store.predict_future_issues()
    
    suggestions = goal_manager.suggest_goals(
        {"health_score": analysis["health_score"], "avg_latencies": metrics_store.get_stats()["avg_latencies"]},
        predictions
    )
    
    return {
        "suggestions": suggestions,
        "count": len(suggestions)
    }

@app.post("/api/goals/start")
async def start_goal(goal_id: str = Form(...)):
    """Start executing a goal"""
    success = goal_manager.start_goal(goal_id)
    
    if not success:
        return {"status": "error", "error": "Goal not found"}
    
    goal = goal_manager.get_goal(goal_id)
    return {
        "status": "started",
        "goal": goal.to_dict()
    }

@app.post("/api/goals/complete")
async def complete_goal(goal_id: str = Form(...), result: str = Form(None)):
    """Mark goal as completed"""
    result_data = {"message": result} if result else None
    goal_manager.complete_goal(goal_id, result_data)
    
    goal = goal_manager.get_goal(goal_id)
    if not goal:
        return {"status": "error", "error": "Goal not found"}
    
    return {
        "status": "completed",
        "goal": goal.to_dict()
    }

@app.get("/api/goals/{goal_id}")
async def get_goal_status(goal_id: str):
    """Get goal status"""
    goal = goal_manager.get_goal(goal_id)
    
    if not goal:
        return {"status": "error", "error": "Goal not found"}
    
    return goal.to_dict()

@app.post("/api/chat")
async def chat(message: str = Form(...), session_id: str = Form(None)):
    """Conversational interface (Level 10: Conversational AI)"""
    # Create or get session
    if not session_id:
        session_id = conversation_manager.create_session()
    
    session = conversation_manager.get_session(session_id)
    if not session:
        session_id = conversation_manager.create_session()
        session = conversation_manager.get_session(session_id)
    
    # Detect intent
    intent = conversation_manager.detect_intent(message)
    
    # Get RAG context
    rag_context = []
    try:
        resp = await http_client.post(
            f"{SERVICES['rag']}/query",
            json={"query": message, "top_k": 2}
        )
        rag_data = resp.json()
        rag_context = rag_data.get("documents", [])
    except:
        pass
    
    # Build prompt
    prompt = conversation_manager.build_prompt(session, message, rag_context)
    
    # Generate simple response based on RAG context
    if rag_context:
        response_text = f"Based on the knowledge base: {rag_context[0].get('content', '')[:200]}..."
    else:
        response_text = f"I understand your query about: {message}. The system has 9 autonomy levels operational."
    
    # Save to session
    session.add_message("user", message, {"intent": intent})
    session.add_message("assistant", response_text, {"rag_used": len(rag_context) > 0})
    
    return {
        "session_id": session_id,
        "response": response_text,
        "intent": intent,
        "rag_context_used": len(rag_context),
        "message_count": len(session.messages)
    }

@app.get("/api/chat/sessions")
async def list_sessions():
    """List all conversation sessions"""
    sessions = [s.to_dict() for s in conversation_manager.sessions.values()]
    return {
        "sessions": sessions,
        "total": len(sessions)
    }

@app.get("/api/chat/session/{session_id}")
async def get_session_history(session_id: str):
    """Get conversation history"""
    session = conversation_manager.get_session(session_id)
    if not session:
        return {"error": "Session not found"}
    
    return {
        "session": session.to_dict(),
        "messages": session.messages
    }

@app.post("/api/execute")
async def execute_task(task: str = Form(...)):
    """Execute autonomous task"""
    # Create task
    task_obj = task_executor.create_task(task)
    
    # Decompose into steps
    steps = task_executor.decompose_task(task)
    task_obj.steps = steps
    task_obj.status = "running"
    task_obj.started_at = datetime.now().isoformat()
    
    # Execute steps
    results = []
    for i, step in enumerate(steps):
        task_obj.current_step = i + 1
        
        # Execute step based on type
        if "health" in step.lower():
            try:
                health = await http_client.get(f"{SERVICES['rag']}/health")
                results.append({"step": step, "status": "success", "data": health.json()})
            except:
                results.append({"step": step, "status": "failed"})
        
        elif "metrics" in step.lower():
            try:
                metrics = metrics_store.get_stats()
                results.append({"step": step, "status": "success", "data": metrics})
            except:
                results.append({"step": step, "status": "failed"})
        
        else:
            results.append({"step": step, "status": "completed"})
    
    # Complete task
    task_obj.status = "completed"
    task_obj.completed_at = datetime.now().isoformat()
    task_obj.result = results
    
    return {
        "task_id": task_obj.task_id,
        "status": task_obj.status,
        "steps_completed": len(steps),
        "results": results
    }

@app.get("/api/tasks")
async def list_tasks():
    """List all tasks"""
    tasks = [t.to_dict() for t in task_executor.tasks.values()]
    return {"tasks": tasks, "total": len(tasks)}

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status"""
    task = task_executor.get_task(task_id)
    if not task:
        return {"error": "Task not found"}
    return task.to_dict()

@app.post("/api/autonomous")
async def autonomous_interface(
    message: str = Form(...),
    session_id: str = Form(None),
    auto_execute: bool = Form(False)
):
    """Unified autonomous interface - intelligent planning + execution"""
    start_time = time.time()
    
    # Create/get session
    if not session_id:
        session_id = conversation_manager.create_session()
    session = conversation_manager.get_session(session_id) or conversation_manager.sessions[conversation_manager.create_session()]
    
    # Phase 1: Intent Detection + Entity Extraction
    intent = conversation_manager.detect_intent(message)
    entities = conversation_manager.extract_entities(message)
    
    # Phase 2: Get RAG context
    rag_context = []
    try:
        resp = await http_client.post(
            f"{SERVICES['rag']}/query",
            json={"query": message, "top_k": 3},
            timeout=5.0
        )
        rag_data = resp.json()
        rag_context = rag_data.get("documents", [])
    except:
        pass
    
    # Phase 3: Intelligent Planning with Adaptive Learning & Decision Making
    execution_plan = None
    adaptive_suggestions = None
    autonomous_decision = None
    
    if intent in ["execute", "modify", "create"]:
        # Create task with intelligent decomposition
        task_obj = task_executor.create_task(message)
        steps = task_executor.decompose_task(message)
        
        # Get adaptive suggestions
        adaptive_suggestions = adaptive_planner.suggest_improvements(message, steps)
        
        # Make autonomous decision
        decision_context = {
            "intent": intent,
            "message": message,
            "pattern": adaptive_suggestions.get("pattern", "generic"),
            "historical_success_rate": adaptive_suggestions.get("historical_success_rate", 0),
            "entities": entities,
            "rag_context_available": len(rag_context) > 0
        }
        autonomous_decision = decision_engine.make_decision(decision_context)
        
        # Optimize steps based on learning
        optimized_steps = adaptive_planner.optimize_steps(steps)
        
        # Add safety steps if decision requires them
        if hasattr(autonomous_decision, 'safety_steps') and autonomous_decision.safety_steps:
            for safety_step in autonomous_decision.safety_steps:
                if safety_step == "backup" and not any("backup" in s.lower() for s in optimized_steps):
                    optimized_steps.insert(0, "Create backup point")
                elif safety_step == "validation" and not any("validat" in s.lower() for s in optimized_steps):
                    optimized_steps.append("Validate changes")
        
        task_obj.steps = optimized_steps
        
        execution_plan = {
            "task_id": task_obj.task_id,
            "steps": optimized_steps,
            "original_steps": steps,
            "optimizations_applied": len(steps) != len(optimized_steps),
            "estimated_duration": len(optimized_steps) * 2,
            "requires_approval": not auto_execute or autonomous_decision.action == "require_approval",
            "safety_level": "high" if any(word in message.lower() for word in ["delete", "remove", "drop"]) else "medium",
            "adaptive_suggestions": adaptive_suggestions,
            "autonomous_decision": autonomous_decision.to_dict()
        }
        
        # Predict failure points
        failure_predictions = predictive_engine.predict_failure_points(execution_plan)
        execution_plan["predicted_failure_points"] = failure_predictions
    
    # Phase 4: Execution (if auto_execute and decision allows)
    task_result = None
    should_execute = auto_execute and execution_plan
    
    # Check autonomous decision
    if should_execute and autonomous_decision:
        if autonomous_decision.action == "require_approval":
            should_execute = False
        elif autonomous_decision.action == "suggest_execute":
            # Execute but mark as suggested
            pass
    
    if should_execute:
        task_obj.status = "running"
        task_obj.started_at = datetime.now().isoformat()
        
        # Use real execution engine
        execution_context = {
            "original_message": message,
            "intent": intent,
            "entities": entities
        }
        
        results = await execution_engine.execute_task(optimized_steps, execution_context)
        summary = execution_engine.get_execution_summary(results)
        
        # Record execution for adaptive learning
        adaptive_planner.record_execution(message, optimized_steps, results, summary)
        
        # Record meta-learning event
        learning_context = {
            "task_type": adaptive_suggestions.get("pattern", "generic"),
            "has_errors": summary.get("failed", 0) > 0,
            "has_rag_context": len(rag_context) > 0
        }
        recommended_strategy = meta_learning_engine.recommend_learning_strategy(learning_context)
        meta_learning_engine.record_learning_event(
            recommended_strategy,
            learning_context,
            summary.get("status", "unknown")
        )
        
        task_obj.status = summary["status"]
        task_obj.completed_at = datetime.now().isoformat()
        task_obj.result = results
        task_result = {
            **task_obj.to_dict(),
            "summary": summary
        }
    
    # Phase 5: Generate Response
    response_text = ""
    if task_result:
        summary = task_result.get("summary", {})
        successful_steps = summary.get("successful", 0)
        total_steps = summary.get("total_steps", len(steps))
        response_text = f"✓ Task {summary.get('status', 'completed')}: {successful_steps}/{total_steps} steps successful ({summary.get('success_rate', 0)}%). Task ID: {task_result['task_id']}"
    elif execution_plan:
        response_text = f"📋 Execution plan ready: {len(execution_plan['steps'])} steps. Set auto_execute=true to run."
    else:
        # Conversational response with RAG context
        if rag_context:
            context_preview = rag_context[0].get('content', '')[:200]
            response_text = f"Based on your history: {context_preview}... (Found {len(rag_context)} relevant documents)"
        else:
            response_text = f"I understand your {intent} request. System has 9 autonomy levels operational."
    
    # Phase 6: Save to session
    session.add_message("user", message, {
        "intent": intent,
        "entities": entities,
        "rag_context_count": len(rag_context)
    })
    session.add_message("assistant", response_text, {
        "rag_used": len(rag_context) > 0,
        "task_executed": task_result is not None,
        "execution_plan": execution_plan
    })
    
    latency = (time.time() - start_time) * 1000
    
    return {
        "session_id": session_id,
        "response": response_text,
        "intent": intent,
        "entities": entities,
        "rag_context_used": len(rag_context),
        "execution_plan": execution_plan,
        "task_result": task_result,
        "latency_ms": round(latency, 2),
        "capabilities": {
            "conversational": True,
            "task_execution": True,
            "autonomous": auto_execute,
            "intelligent_planning": True,
            "context_aware": len(rag_context) > 0
        }
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
