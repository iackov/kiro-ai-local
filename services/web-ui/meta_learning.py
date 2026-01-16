"""
Meta-Learning Engine - System learns how to learn better
"""
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

class LearningStrategy:
    def __init__(self, name: str, description: str, effectiveness: float):
        self.name = name
        self.description = description
        self.effectiveness = effectiveness  # 0-1 score
        self.times_used = 0
        self.successes = 0
    
    def update_effectiveness(self, success: bool):
        self.times_used += 1
        if success:
            self.successes += 1
        # Recalculate effectiveness
        self.effectiveness = self.successes / self.times_used if self.times_used > 0 else 0.5
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "effectiveness": round(self.effectiveness, 2),
            "times_used": self.times_used,
            "success_rate": round((self.successes / self.times_used * 100) if self.times_used > 0 else 0, 1)
        }

class MetaLearningEngine:
    def __init__(self):
        self.learning_strategies = self._initialize_strategies()
        self.learning_history = []
        self.meta_insights = {}
    
    def _initialize_strategies(self) -> Dict[str, LearningStrategy]:
        """Initialize learning strategies"""
        return {
            "pattern_recognition": LearningStrategy(
                "pattern_recognition",
                "Learn from task patterns and their success rates",
                0.8
            ),
            "error_analysis": LearningStrategy(
                "error_analysis",
                "Learn from failures to avoid similar mistakes",
                0.75
            ),
            "context_adaptation": LearningStrategy(
                "context_adaptation",
                "Adapt behavior based on context (RAG, entities, etc)",
                0.85
            ),
            "feedback_integration": LearningStrategy(
                "feedback_integration",
                "Learn from user feedback and corrections",
                0.7
            ),
            "performance_optimization": LearningStrategy(
                "performance_optimization",
                "Learn optimal execution paths and shortcuts",
                0.65
            )
        }
    
    def record_learning_event(self, strategy_name: str, context: Dict, outcome: str):
        """Record a learning event"""
        event = {
            "strategy": strategy_name,
            "context": context,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat(),
            "success": outcome in ["success", "completed"]
        }
        
        self.learning_history.append(event)
        
        # Update strategy effectiveness
        if strategy_name in self.learning_strategies:
            self.learning_strategies[strategy_name].update_effectiveness(event["success"])
    
    def analyze_learning_effectiveness(self) -> Dict:
        """Analyze how well the system is learning"""
        if len(self.learning_history) < 5:
            return {
                "status": "insufficient_data",
                "message": "Need more learning events to analyze"
            }
        
        # Analyze learning curve
        recent_events = self.learning_history[-20:]
        success_rate = sum(1 for e in recent_events if e["success"]) / len(recent_events)
        
        # Compare with earlier events
        if len(self.learning_history) > 40:
            earlier_events = self.learning_history[-40:-20]
            earlier_success = sum(1 for e in earlier_events if e["success"]) / len(earlier_events)
            improvement = success_rate - earlier_success
        else:
            improvement = 0
        
        # Identify best strategies
        best_strategies = sorted(
            self.learning_strategies.values(),
            key=lambda s: s.effectiveness,
            reverse=True
        )[:3]
        
        return {
            "current_success_rate": round(success_rate * 100, 1),
            "improvement_trend": round(improvement * 100, 1),
            "learning_velocity": "fast" if improvement > 0.1 else "moderate" if improvement > 0 else "slow",
            "best_strategies": [s.to_dict() for s in best_strategies],
            "total_learning_events": len(self.learning_history)
        }
    
    def recommend_learning_strategy(self, context: Dict) -> str:
        """Recommend best learning strategy for given context"""
        task_type = context.get("task_type", "generic")
        has_errors = context.get("has_errors", False)
        has_context = context.get("has_rag_context", False)
        
        # Rule-based recommendation
        if has_errors:
            return "error_analysis"
        elif has_context:
            return "context_adaptation"
        elif task_type in ["health_check", "analysis"]:
            return "pattern_recognition"
        else:
            # Use most effective strategy
            best = max(self.learning_strategies.values(), key=lambda s: s.effectiveness)
            return best.name
    
    def optimize_learning_process(self) -> Dict:
        """Optimize the learning process itself"""
        optimizations = []
        
        # Find underperforming strategies
        for strategy in self.learning_strategies.values():
            if strategy.times_used > 5 and strategy.effectiveness < 0.6:
                optimizations.append({
                    "type": "improve_strategy",
                    "strategy": strategy.name,
                    "current_effectiveness": strategy.effectiveness,
                    "suggestion": f"Strategy '{strategy.name}' needs improvement"
                })
        
        # Find unused strategies
        unused = [s for s in self.learning_strategies.values() if s.times_used == 0]
        if unused:
            optimizations.append({
                "type": "activate_strategies",
                "strategies": [s.name for s in unused],
                "suggestion": "Activate unused learning strategies"
            })
        
        # Check learning velocity
        analysis = self.analyze_learning_effectiveness()
        if analysis.get("learning_velocity") == "slow":
            optimizations.append({
                "type": "accelerate_learning",
                "suggestion": "Increase learning rate or try different strategies"
            })
        
        return {
            "optimizations_found": len(optimizations),
            "optimizations": optimizations
        }
    
    def get_meta_insights(self) -> Dict:
        """Get meta-learning insights"""
        strategies_summary = {
            name: strategy.to_dict()
            for name, strategy in self.learning_strategies.items()
        }
        
        effectiveness_analysis = self.analyze_learning_effectiveness()
        optimization_suggestions = self.optimize_learning_process()
        
        return {
            "strategies": strategies_summary,
            "effectiveness": effectiveness_analysis,
            "optimizations": optimization_suggestions,
            "meta_level": "learning_to_learn"
        }

# Global meta-learning engine
meta_learning_engine = MetaLearningEngine()
