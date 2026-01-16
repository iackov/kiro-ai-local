"""
Adaptive Task Planner - Learn from execution history to improve planning
"""
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

class AdaptivePlanner:
    def __init__(self):
        self.execution_history = []
        self.pattern_success_rates = defaultdict(lambda: {"success": 0, "total": 0})
        self.step_performance = defaultdict(list)
        self.learned_optimizations = {}
    
    def record_execution(self, task_description: str, steps: List[str], 
                        results: List[Dict], summary: Dict):
        """Record task execution for learning"""
        execution = {
            "task": task_description,
            "steps": steps,
            "results": results,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        self.execution_history.append(execution)
        
        # Update pattern success rates
        task_pattern = self._extract_pattern(task_description)
        self.pattern_success_rates[task_pattern]["total"] += 1
        if summary.get("status") == "completed":
            self.pattern_success_rates[task_pattern]["success"] += 1
        
        # Record step performance
        for result in results:
            step_type = self._classify_step(result["step"])
            latency = 0
            if "timestamp" in result:
                latency = 100  # Simplified
            self.step_performance[step_type].append({
                "status": result["status"],
                "latency": latency
            })
    
    def _extract_pattern(self, task: str) -> str:
        """Extract task pattern for learning"""
        task_lower = task.lower()
        if "health" in task_lower or "check" in task_lower:
            return "health_check"
        elif "add" in task_lower or "create" in task_lower:
            if "redis" in task_lower or "cache" in task_lower:
                return "add_cache"
            elif "service" in task_lower:
                return "add_service"
            return "create_resource"
        elif "optimize" in task_lower or "improve" in task_lower:
            return "optimization"
        elif "analyze" in task_lower:
            return "analysis"
        elif "fix" in task_lower or "debug" in task_lower:
            return "debugging"
        return "generic"
    
    def _classify_step(self, step: str) -> str:
        """Classify step type"""
        step_lower = step.lower()
        if "health" in step_lower:
            return "health_check"
        elif "metrics" in step_lower or "measure" in step_lower:
            return "metrics"
        elif "analyze" in step_lower:
            return "analysis"
        elif "generate" in step_lower:
            return "generation"
        elif "validate" in step_lower or "verify" in step_lower:
            return "validation"
        elif "apply" in step_lower:
            return "application"
        elif "backup" in step_lower:
            return "backup"
        return "generic"
    
    def suggest_improvements(self, task_description: str, proposed_steps: List[str]) -> Dict:
        """Suggest improvements based on learned patterns"""
        pattern = self._extract_pattern(task_description)
        suggestions = []
        
        # Check if we have history for this pattern
        if pattern in self.pattern_success_rates:
            stats = self.pattern_success_rates[pattern]
            success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
            
            if success_rate < 80:
                suggestions.append({
                    "type": "warning",
                    "message": f"This task pattern has {success_rate:.1f}% success rate. Consider review.",
                    "confidence": "medium"
                })
        
        # Analyze proposed steps
        for i, step in enumerate(proposed_steps):
            step_type = self._classify_step(step)
            
            # Check if this step type often fails
            if step_type in self.step_performance:
                perf = self.step_performance[step_type]
                failures = sum(1 for p in perf if p["status"] == "failed")
                if failures > len(perf) * 0.2:  # More than 20% failure rate
                    suggestions.append({
                        "type": "step_warning",
                        "step_index": i,
                        "step": step,
                        "message": f"Step type '{step_type}' has high failure rate",
                        "confidence": "high"
                    })
        
        # Suggest additional steps based on patterns
        if pattern == "add_service" and not any("backup" in s.lower() for s in proposed_steps):
            suggestions.append({
                "type": "missing_step",
                "message": "Consider adding backup step before applying changes",
                "suggested_step": "Create backup point",
                "insert_before": "Apply configuration",
                "confidence": "high"
            })
        
        if pattern == "optimization" and not any("measure" in s.lower() for s in proposed_steps):
            suggestions.append({
                "type": "missing_step",
                "message": "Add baseline measurement for optimization validation",
                "suggested_step": "Measure current performance baseline",
                "insert_at": 0,
                "confidence": "high"
            })
        
        return {
            "pattern": pattern,
            "suggestions": suggestions,
            "historical_success_rate": self._get_success_rate(pattern),
            "total_executions": self.pattern_success_rates[pattern]["total"]
        }
    
    def _get_success_rate(self, pattern: str) -> float:
        """Get success rate for pattern"""
        if pattern not in self.pattern_success_rates:
            return 0.0
        stats = self.pattern_success_rates[pattern]
        return (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
    
    def optimize_steps(self, steps: List[str]) -> List[str]:
        """Optimize step order and content based on learning"""
        optimized = steps.copy()
        
        # Remove redundant steps
        seen_types = set()
        filtered = []
        for step in optimized:
            step_type = self._classify_step(step)
            # Allow multiple health checks but not multiple backups
            if step_type == "backup" and step_type in seen_types:
                continue
            seen_types.add(step_type)
            filtered.append(step)
        
        # Reorder for optimal execution
        # Priority: backup -> validation -> generation -> application -> verification
        priority_order = {
            "backup": 0,
            "validation": 1,
            "generation": 2,
            "application": 3,
            "verification": 4,
            "health_check": 5,
            "metrics": 6,
            "analysis": 7,
            "generic": 8
        }
        
        sorted_steps = sorted(filtered, key=lambda s: priority_order.get(self._classify_step(s), 99))
        
        return sorted_steps
    
    def get_learning_insights(self) -> Dict:
        """Get insights from learning"""
        total_executions = len(self.execution_history)
        successful = sum(1 for e in self.execution_history if e["summary"].get("status") == "completed")
        
        # Find best and worst patterns
        best_pattern = None
        worst_pattern = None
        best_rate = 0
        worst_rate = 100
        
        for pattern, stats in self.pattern_success_rates.items():
            if stats["total"] < 2:  # Need at least 2 executions
                continue
            rate = (stats["success"] / stats["total"] * 100)
            if rate > best_rate:
                best_rate = rate
                best_pattern = pattern
            if rate < worst_rate:
                worst_rate = rate
                worst_pattern = pattern
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful,
            "overall_success_rate": (successful / total_executions * 100) if total_executions > 0 else 0,
            "patterns_learned": len(self.pattern_success_rates),
            "best_pattern": {
                "name": best_pattern,
                "success_rate": best_rate
            } if best_pattern else None,
            "worst_pattern": {
                "name": worst_pattern,
                "success_rate": worst_rate
            } if worst_pattern else None,
            "step_types_tracked": len(self.step_performance)
        }

# Global adaptive planner
adaptive_planner = AdaptivePlanner()
