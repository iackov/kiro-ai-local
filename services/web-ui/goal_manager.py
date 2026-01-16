"""
Goal-Oriented Behavior - Level 9
System can set and achieve goals autonomously
"""
from typing import Dict, List
from datetime import datetime
from enum import Enum

class GoalStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Goal:
    """Represents a system goal"""
    
    def __init__(self, goal_id: str, description: str, priority: str = "medium"):
        self.goal_id = goal_id
        self.description = description
        self.priority = priority  # low, medium, high, critical
        self.status = GoalStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self.steps = []
        self.progress = 0.0
        self.result = None
    
    def to_dict(self) -> Dict:
        return {
            "goal_id": self.goal_id,
            "description": self.description,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "steps": self.steps,
            "progress": self.progress,
            "result": self.result
        }

class GoalManager:
    """Manages system goals and their execution"""
    
    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.goal_counter = 0
        
        # Predefined goal templates
        self.goal_templates = {
            "optimize_performance": {
                "description": "Optimize system performance",
                "steps": [
                    "Analyze current performance metrics",
                    "Identify bottlenecks",
                    "Apply optimizations",
                    "Verify improvements"
                ]
            },
            "ensure_reliability": {
                "description": "Ensure system reliability",
                "steps": [
                    "Check all services health",
                    "Review error rates",
                    "Apply auto-healing if needed",
                    "Verify stability"
                ]
            },
            "reduce_latency": {
                "description": "Reduce query latency",
                "steps": [
                    "Measure current latency",
                    "Enable caching",
                    "Optimize queries",
                    "Verify latency reduction"
                ]
            },
            "scale_up": {
                "description": "Scale up system capacity",
                "steps": [
                    "Analyze resource usage",
                    "Identify services to scale",
                    "Increase resources",
                    "Verify capacity increase"
                ]
            }
        }
    
    def create_goal(self, description: str, priority: str = "medium", template: str = None) -> Goal:
        """Create a new goal"""
        self.goal_counter += 1
        goal_id = f"goal_{self.goal_counter}"
        
        goal = Goal(goal_id, description, priority)
        
        # Apply template if specified
        if template and template in self.goal_templates:
            template_data = self.goal_templates[template]
            goal.steps = template_data["steps"].copy()
        
        self.goals[goal_id] = goal
        return goal
    
    def start_goal(self, goal_id: str) -> bool:
        """Start executing a goal"""
        if goal_id not in self.goals:
            return False
        
        goal = self.goals[goal_id]
        goal.status = GoalStatus.IN_PROGRESS
        goal.started_at = datetime.now().isoformat()
        return True
    
    def update_progress(self, goal_id: str, progress: float, step_completed: str = None):
        """Update goal progress"""
        if goal_id not in self.goals:
            return
        
        goal = self.goals[goal_id]
        goal.progress = min(progress, 100.0)
        
        if step_completed:
            goal.steps.append({
                "step": step_completed,
                "completed_at": datetime.now().isoformat()
            })
    
    def complete_goal(self, goal_id: str, result: Dict = None):
        """Mark goal as completed"""
        if goal_id not in self.goals:
            return
        
        goal = self.goals[goal_id]
        goal.status = GoalStatus.COMPLETED
        goal.completed_at = datetime.now().isoformat()
        goal.progress = 100.0
        goal.result = result
    
    def fail_goal(self, goal_id: str, reason: str):
        """Mark goal as failed"""
        if goal_id not in self.goals:
            return
        
        goal = self.goals[goal_id]
        goal.status = GoalStatus.FAILED
        goal.completed_at = datetime.now().isoformat()
        goal.result = {"error": reason}
    
    def get_active_goals(self) -> List[Goal]:
        """Get all active goals"""
        return [
            goal for goal in self.goals.values()
            if goal.status in [GoalStatus.PENDING, GoalStatus.IN_PROGRESS]
        ]
    
    def get_goal(self, goal_id: str) -> Goal:
        """Get specific goal"""
        return self.goals.get(goal_id)
    
    def suggest_goals(self, metrics: Dict, predictions: List[Dict]) -> List[Dict]:
        """Suggest goals based on system state"""
        suggestions = []
        
        # Based on health score
        health_score = metrics.get("health_score", 100)
        if health_score < 80:
            suggestions.append({
                "template": "ensure_reliability",
                "reason": f"Health score is {health_score}/100",
                "priority": "high"
            })
        
        # Based on latency
        avg_latencies = metrics.get("avg_latencies", {})
        for service, latency in avg_latencies.items():
            if latency > 500:
                suggestions.append({
                    "template": "reduce_latency",
                    "reason": f"{service} latency is {latency:.0f}ms",
                    "priority": "medium"
                })
        
        # Based on predictions
        for pred in predictions:
            if pred.get("urgency") == "high":
                if "latency" in pred.get("type", ""):
                    suggestions.append({
                        "template": "optimize_performance",
                        "reason": pred.get("issue", "Performance degradation predicted"),
                        "priority": "high"
                    })
                elif "load" in pred.get("type", ""):
                    suggestions.append({
                        "template": "scale_up",
                        "reason": pred.get("issue", "Load increase predicted"),
                        "priority": "high"
                    })
        
        return suggestions

# Global goal manager
goal_manager = GoalManager()
