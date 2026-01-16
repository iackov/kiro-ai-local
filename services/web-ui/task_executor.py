"""
Task Execution Engine - Autonomous Task Execution with Loop Protection
"""
from typing import Dict, List
from datetime import datetime
import uuid

class Task:
    # Anti-loop protection
    MAX_STEPS = 50
    MAX_EXECUTION_TIME = 300  # 5 minutes max per task
    
    def __init__(self, task_id: str, description: str):
        self.task_id = task_id
        self.description = description
        self.status = "pending"  # pending, running, completed, failed
        self.steps = []
        self.current_step = 0
        self.result = None
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self.execution_start_time = None  # For timeout detection
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status,
            "steps": self.steps,
            "current_step": self.current_step,
            "progress": (self.current_step / len(self.steps) * 100) if self.steps else 0,
            "result": self.result,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }

class TaskExecutor:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
    
    def create_task(self, description: str) -> Task:
        task_id = str(uuid.uuid4())[:8]
        task = Task(task_id, description)
        self.tasks[task_id] = task
        return task
    
    def decompose_task(self, description: str) -> List[str]:
        """Break task into steps with intelligent analysis"""
        desc_lower = description.lower()
        
        # Advanced pattern matching with context
        if "health" in desc_lower or "status" in desc_lower:
            return [
                "Check RAG service health",
                "Check Architecture Engine health",
                "Check Ollama service health",
                "Aggregate health metrics",
                "Generate health report"
            ]
        
        elif "optimize" in desc_lower or "improve" in desc_lower:
            if "latency" in desc_lower or "performance" in desc_lower:
                return [
                    "Measure current latencies",
                    "Identify slow services",
                    "Analyze bottlenecks",
                    "Generate optimization plan",
                    "Apply optimizations",
                    "Verify improvements"
                ]
            else:
                return [
                    "Analyze current metrics",
                    "Identify improvement areas",
                    "Generate action plan",
                    "Execute improvements",
                    "Validate results"
                ]
        
        elif "add" in desc_lower or "create" in desc_lower:
            if "service" in desc_lower:
                return [
                    "Parse service requirements",
                    "Check dependencies",
                    "Generate docker-compose config",
                    "Validate safety checks",
                    "Create backup point",
                    "Apply configuration",
                    "Verify service startup"
                ]
            elif "redis" in desc_lower or "cache" in desc_lower:
                return [
                    "Analyze caching needs",
                    "Design cache strategy",
                    "Generate Redis configuration",
                    "Validate integration points",
                    "Apply changes",
                    "Test cache functionality"
                ]
            else:
                return [
                    "Parse requirements",
                    "Design solution",
                    "Generate configuration",
                    "Validate safety",
                    "Apply changes",
                    "Verify functionality"
                ]
        
        elif "fix" in desc_lower or "debug" in desc_lower:
            return [
                "Identify problem symptoms",
                "Analyze error logs",
                "Determine root cause",
                "Generate fix strategy",
                "Apply fix",
                "Verify resolution"
            ]
        
        elif "analyze" in desc_lower or "investigate" in desc_lower:
            return [
                "Gather relevant data",
                "Analyze patterns",
                "Identify insights",
                "Generate recommendations"
            ]
        
        elif "deploy" in desc_lower or "rollout" in desc_lower:
            return [
                "Pre-deployment checks",
                "Create backup",
                "Deploy changes",
                "Health check",
                "Rollback if needed"
            ]
        
        else:
            # Generic intelligent decomposition
            return [
                "Understand request context",
                "Gather required information",
                "Plan execution strategy",
                "Execute primary action",
                "Verify results",
                "Generate summary"
            ]
    
    def get_task(self, task_id: str) -> Task:
        return self.tasks.get(task_id)

# Global task executor
task_executor = TaskExecutor()
