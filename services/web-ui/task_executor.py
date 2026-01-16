"""
Task Execution Engine - Autonomous Task Execution
"""
from typing import Dict, List
from datetime import datetime
import uuid

class Task:
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
        """Break task into steps"""
        desc_lower = description.lower()
        
        # Pattern matching for common tasks
        if "health" in desc_lower or "status" in desc_lower:
            return [
                "Check system health",
                "Get metrics",
                "Analyze results"
            ]
        elif "optimize" in desc_lower or "improve" in desc_lower:
            return [
                "Analyze current performance",
                "Identify bottlenecks",
                "Apply optimizations",
                "Verify improvements"
            ]
        elif "add" in desc_lower or "create" in desc_lower:
            return [
                "Parse requirements",
                "Generate configuration",
                "Validate safety",
                "Apply changes"
            ]
        else:
            return [
                "Analyze request",
                "Execute action",
                "Verify result"
            ]
    
    def get_task(self, task_id: str) -> Task:
        return self.tasks.get(task_id)

# Global task executor
task_executor = TaskExecutor()
