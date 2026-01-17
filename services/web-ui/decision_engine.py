"""
Decision Engine - Context-aware autonomous decision making
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

class Decision:
    def __init__(self, decision_type: str, action: str, confidence: float, reasoning: List[str]):
        self.decision_type = decision_type
        self.action = action
        self.confidence = confidence
        self.reasoning = reasoning
        self.timestamp = datetime.now().isoformat()
        self.executed = False
        self.result = None
    
    def to_dict(self) -> Dict:
        return {
            "type": self.decision_type,
            "action": self.action,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp,
            "executed": self.executed,
            "result": self.result
        }

class DecisionEngine:
    def __init__(self):
        self.decisions_history = []
        self.decision_rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict:
        """Initialize decision-making rules"""
        return {
            "auto_execute": {
                "high_confidence_threshold": 0.9,
                "medium_confidence_threshold": 0.7,
                "low_risk_patterns": ["health_check", "analysis", "metrics"],
                "high_risk_patterns": ["delete", "drop", "remove", "modify_production"]
            },
            "safety": {
                "require_backup": ["add_service", "modify_config", "modify_production", "create_resource"],
                "require_validation": ["generate_config", "modify_architecture", "modify_production"],
                "max_retries": 3
            },
            "optimization": {
                "auto_optimize_threshold": 0.8,  # Success rate threshold
                "min_executions_for_learning": 3
            }
        }
    
    def make_decision(self, context: Dict) -> Decision:
        """Make autonomous decision based on context"""
        intent = context.get("intent", "query")
        message = context.get("message", "")
        pattern = context.get("pattern", "generic")
        historical_success_rate = context.get("historical_success_rate", 0)
        entities = context.get("entities", {})
        rag_context_available = context.get("rag_context_available", False)
        
        reasoning = []
        confidence = 0.5
        
        # Decision 1: Should we auto-execute?
        if intent in ["execute", "modify", "create"]:  # Added "create"
            # Check risk level
            is_high_risk = any(risk in message.lower() for risk in self.decision_rules["auto_execute"]["high_risk_patterns"])
            is_low_risk = pattern in self.decision_rules["auto_execute"]["low_risk_patterns"]
            
            # NEW: Create operations in safe zones are low risk
            if intent == "create":
                safe_zones = ["playground/", "generated/", "experiments/", "tic-tac-toe/", "demos/", "examples/"]
                is_in_safe_zone = any(zone in message.lower() for zone in safe_zones)
                
                # If creating code/script without specifying dangerous location, assume safe
                code_creation_keywords = ["script", "code", "program", "game", "app", "function",
                                         "скрипт", "код", "программ", "игр", "приложение", "функци"]
                is_code_creation = any(keyword in message.lower() for keyword in code_creation_keywords)
                
                # Check if it's NOT modifying production/system files
                dangerous_targets = ["production", "system", "config", "/etc/", "/var/", "docker-compose",
                                    "продакшн", "система", "конфиг"]
                is_dangerous = any(target in message.lower() for target in dangerous_targets)
                
                if is_in_safe_zone or (is_code_creation and not is_dangerous):
                    confidence = 0.95
                    reasoning.append("Code creation without dangerous targets - auto-approved")
                    action = "auto_execute"
                    return Decision(intent, action, confidence, reasoning)
            
            if is_high_risk:
                confidence = 0.3
                reasoning.append("High-risk operation detected - requires manual approval")
                action = "require_approval"
            elif is_low_risk:
                confidence = 0.9
                reasoning.append("Low-risk operation - safe for auto-execution")
                action = "auto_execute"
            else:
                # Check historical success rate
                if historical_success_rate >= 90:
                    confidence = 0.85
                    reasoning.append(f"High historical success rate ({historical_success_rate}%)")
                    action = "auto_execute"
                elif historical_success_rate >= 70:
                    confidence = 0.7
                    reasoning.append(f"Moderate success rate ({historical_success_rate}%)")
                    action = "suggest_execute"
                else:
                    confidence = 0.5
                    reasoning.append(f"Low success rate ({historical_success_rate}%) - recommend review")
                    action = "require_approval"
            
            # Boost confidence if RAG context available
            if rag_context_available:
                confidence = min(confidence + 0.1, 1.0)
                reasoning.append("RAG context available - increased confidence")
        
        elif intent == "query":
            confidence = 0.95
            reasoning.append("Query intent - safe to respond")
            action = "respond"
        
        elif intent == "analyze":
            confidence = 0.9
            reasoning.append("Analysis intent - safe to execute")
            action = "auto_execute"
        
        else:
            confidence = 0.6
            reasoning.append("Generic intent - moderate confidence")
            action = "suggest_execute"
        
        # Decision 2: Should we add safety steps?
        safety_steps = []
        if pattern in self.decision_rules["safety"]["require_backup"]:
            safety_steps.append("backup")
            reasoning.append("Backup required for this operation type")
        
        if pattern in self.decision_rules["safety"]["require_validation"]:
            safety_steps.append("validation")
            reasoning.append("Validation required for this operation type")
        
        # Decision 3: Should we optimize?
        should_optimize = False
        if historical_success_rate < self.decision_rules["optimization"]["auto_optimize_threshold"] * 100:
            should_optimize = True
            reasoning.append("Success rate below threshold - optimization recommended")
        
        decision = Decision(
            decision_type="execution",
            action=action,
            confidence=confidence,
            reasoning=reasoning
        )
        
        # Add metadata
        decision.safety_steps = safety_steps
        decision.should_optimize = should_optimize
        
        self.decisions_history.append(decision)
        return decision
    
    def evaluate_step_decision(self, step: str, context: Dict) -> Dict:
        """Decide if a step should be executed, skipped, or modified"""
        step_lower = step.lower()
        
        # Skip redundant steps
        if "backup" in step_lower and context.get("backup_created"):
            return {
                "action": "skip",
                "reason": "Backup already created",
                "confidence": 0.95
            }
        
        # Modify risky steps
        if "delete" in step_lower or "drop" in step_lower:
            return {
                "action": "modify",
                "reason": "High-risk operation - add safety check",
                "modified_step": f"Safely {step} with backup",
                "confidence": 0.8
            }
        
        # Execute normally
        return {
            "action": "execute",
            "reason": "Normal execution",
            "confidence": 0.9
        }
    
    def should_retry(self, step: str, attempt: int, error: str) -> bool:
        """Decide if step should be retried"""
        max_retries = self.decision_rules["safety"]["max_retries"]
        
        if attempt >= max_retries:
            return False
        
        # Retry on transient errors
        transient_errors = ["timeout", "connection", "temporary", "unavailable"]
        if any(err in error.lower() for err in transient_errors):
            return True
        
        # Don't retry on permanent errors
        permanent_errors = ["not found", "invalid", "forbidden", "unauthorized"]
        if any(err in error.lower() for err in permanent_errors):
            return False
        
        return True
    
    def get_decision_insights(self) -> Dict:
        """Get insights from decision history"""
        total = len(self.decisions_history)
        if total == 0:
            return {
                "total_decisions": 0,
                "avg_confidence": 0,
                "decision_types": {}
            }
        
        avg_confidence = sum(d.confidence for d in self.decisions_history) / total
        
        decision_types = {}
        for decision in self.decisions_history:
            action = decision.action
            if action not in decision_types:
                decision_types[action] = 0
            decision_types[action] += 1
        
        return {
            "total_decisions": total,
            "avg_confidence": round(avg_confidence, 2),
            "decision_types": decision_types,
            "recent_decisions": [d.to_dict() for d in self.decisions_history[-5:]]
        }

# Global decision engine
decision_engine = DecisionEngine()
