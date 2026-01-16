"""
Predictive Engine - Predict future issues and take proactive actions
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict

class Prediction:
    def __init__(self, prediction_type: str, description: str, probability: float, 
                 time_horizon: str, recommended_action: str):
        self.prediction_type = prediction_type
        self.description = description
        self.probability = probability  # 0-1
        self.time_horizon = time_horizon  # immediate, short_term, long_term
        self.recommended_action = recommended_action
        self.timestamp = datetime.now().isoformat()
        self.prevented = False
    
    def to_dict(self) -> Dict:
        return {
            "type": self.prediction_type,
            "description": self.description,
            "probability": round(self.probability, 2),
            "time_horizon": self.time_horizon,
            "recommended_action": self.recommended_action,
            "timestamp": self.timestamp,
            "prevented": self.prevented
        }

class PredictiveEngine:
    def __init__(self):
        self.predictions = []
        self.prevented_issues = []
        self.prediction_accuracy = defaultdict(lambda: {"correct": 0, "total": 0})
    
    def analyze_trends(self, metrics: Dict, adaptive_insights: Dict) -> List[Prediction]:
        """Analyze trends and predict future issues"""
        predictions = []
        
        # Predict based on success rate trends
        success_rate = adaptive_insights.get("overall_success_rate", 100)
        if success_rate < 100 and success_rate > 90:
            pred = Prediction(
                "performance_degradation",
                f"Success rate declining to {success_rate}%, may drop below 90% soon",
                0.6,
                "short_term",
                "Review recent failures and improve error handling"
            )
            predictions.append(pred)
        elif success_rate <= 90:
            pred = Prediction(
                "critical_performance",
                f"Success rate at {success_rate}%, critical threshold reached",
                0.9,
                "immediate",
                "Immediate investigation required - system reliability at risk"
            )
            predictions.append(pred)
        
        # Predict based on error patterns
        if metrics.get("errors"):
            total_errors = sum(metrics["errors"].values())
            if total_errors > 10:
                pred = Prediction(
                    "error_spike",
                    f"Error count at {total_errors}, may indicate systemic issue",
                    0.75,
                    "immediate",
                    "Investigate error patterns and implement fixes"
                )
                predictions.append(pred)
        
        # Predict based on latency trends
        if metrics.get("avg_latencies"):
            high_latency = [svc for svc, lat in metrics["avg_latencies"].items() if lat > 1500]
            if high_latency:
                pred = Prediction(
                    "latency_increase",
                    f"Services {', '.join(high_latency)} showing high latency, may worsen",
                    0.7,
                    "short_term",
                    "Optimize slow services or add caching"
                )
                predictions.append(pred)
        
        # Predict based on learning velocity
        if adaptive_insights.get("patterns_learned", 0) < 3:
            pred = Prediction(
                "insufficient_learning",
                "System has limited learning data, predictions may be inaccurate",
                0.8,
                "long_term",
                "Execute more diverse tasks to build learning history"
            )
            predictions.append(pred)
        
        # Predict resource exhaustion
        total_queries = metrics.get("total_queries", 0)
        if total_queries > 100:
            pred = Prediction(
                "resource_pressure",
                f"High query volume ({total_queries}), may need scaling",
                0.5,
                "long_term",
                "Monitor resource usage and plan for scaling"
            )
            predictions.append(pred)
        
        self.predictions.extend(predictions)
        return predictions
    
    def predict_failure_points(self, execution_plan: Dict) -> List[Dict]:
        """Predict which steps in execution plan are likely to fail"""
        failure_points = []
        
        steps = execution_plan.get("steps", [])
        pattern = execution_plan.get("adaptive_suggestions", {}).get("pattern", "generic")
        
        for i, step in enumerate(steps):
            step_lower = step.lower()
            risk_score = 0.1  # Base risk
            
            # High-risk operations
            if any(word in step_lower for word in ["delete", "drop", "remove"]):
                risk_score = 0.8
            elif any(word in step_lower for word in ["modify", "update", "change"]):
                risk_score = 0.5
            elif any(word in step_lower for word in ["generate", "create"]):
                risk_score = 0.3
            
            # Increase risk for production operations
            if "production" in step_lower or "database" in step_lower:
                risk_score = min(risk_score + 0.2, 1.0)
            
            if risk_score > 0.4:
                failure_points.append({
                    "step_index": i,
                    "step": step,
                    "failure_probability": round(risk_score, 2),
                    "mitigation": self._suggest_mitigation(step)
                })
        
        return failure_points
    
    def _suggest_mitigation(self, step: str) -> str:
        """Suggest mitigation for risky step"""
        step_lower = step.lower()
        
        if "delete" in step_lower or "drop" in step_lower:
            return "Add backup before deletion and implement soft delete"
        elif "modify" in step_lower or "update" in step_lower:
            return "Create rollback point and validate changes"
        elif "generate" in step_lower:
            return "Validate generated output before applying"
        else:
            return "Add error handling and retry logic"
    
    def generate_proactive_actions(self, predictions: List[Prediction]) -> List[Dict]:
        """Generate proactive actions based on predictions"""
        actions = []
        
        for pred in predictions:
            if pred.probability > 0.7 and pred.time_horizon == "immediate":
                actions.append({
                    "priority": "high",
                    "action": pred.recommended_action,
                    "reason": pred.description,
                    "auto_executable": pred.prediction_type in ["error_spike", "latency_increase"]
                })
            elif pred.probability > 0.6:
                actions.append({
                    "priority": "medium",
                    "action": pred.recommended_action,
                    "reason": pred.description,
                    "auto_executable": False
                })
        
        return actions
    
    def validate_prediction(self, prediction_type: str, actual_outcome: bool):
        """Validate prediction accuracy"""
        self.prediction_accuracy[prediction_type]["total"] += 1
        if actual_outcome:
            self.prediction_accuracy[prediction_type]["correct"] += 1
    
    def get_prediction_accuracy(self) -> Dict:
        """Get prediction accuracy metrics"""
        accuracy_by_type = {}
        
        for pred_type, stats in self.prediction_accuracy.items():
            if stats["total"] > 0:
                accuracy = stats["correct"] / stats["total"]
                accuracy_by_type[pred_type] = {
                    "accuracy": round(accuracy * 100, 1),
                    "predictions_made": stats["total"],
                    "correct_predictions": stats["correct"]
                }
        
        overall_correct = sum(s["correct"] for s in self.prediction_accuracy.values())
        overall_total = sum(s["total"] for s in self.prediction_accuracy.values())
        overall_accuracy = (overall_correct / overall_total * 100) if overall_total > 0 else 0
        
        return {
            "overall_accuracy": round(overall_accuracy, 1),
            "by_type": accuracy_by_type,
            "total_predictions": overall_total
        }
    
    def get_predictive_insights(self) -> Dict:
        """Get predictive engine insights"""
        active_predictions = [p for p in self.predictions if not p.prevented]
        
        immediate = [p for p in active_predictions if p.time_horizon == "immediate"]
        short_term = [p for p in active_predictions if p.time_horizon == "short_term"]
        long_term = [p for p in active_predictions if p.time_horizon == "long_term"]
        
        return {
            "total_predictions": len(self.predictions),
            "active_predictions": len(active_predictions),
            "prevented_issues": len(self.prevented_issues),
            "by_horizon": {
                "immediate": len(immediate),
                "short_term": len(short_term),
                "long_term": len(long_term)
            },
            "accuracy": self.get_prediction_accuracy(),
            "recent_predictions": [p.to_dict() for p in active_predictions[-5:]]
        }

# Global predictive engine
predictive_engine = PredictiveEngine()
