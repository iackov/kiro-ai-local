"""
Self-Improvement Engine - System improves itself based on performance
"""
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

class ImprovementOpportunity:
    def __init__(self, area: str, issue: str, suggestion: str, impact: str, confidence: float):
        self.area = area
        self.issue = issue
        self.suggestion = suggestion
        self.impact = impact  # low, medium, high
        self.confidence = confidence
        self.timestamp = datetime.now().isoformat()
        self.applied = False
    
    def to_dict(self) -> Dict:
        return {
            "area": self.area,
            "issue": self.issue,
            "suggestion": self.suggestion,
            "impact": self.impact,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "applied": self.applied
        }

class SelfImprovementEngine:
    def __init__(self):
        self.opportunities = []
        self.improvements_applied = []
        self.performance_baseline = {}
    
    def analyze_system_performance(self, metrics: Dict, adaptive_insights: Dict, 
                                   decision_insights: Dict) -> List[ImprovementOpportunity]:
        """Analyze system and identify improvement opportunities"""
        opportunities = []
        
        # Analyze success rates
        if adaptive_insights.get("overall_success_rate", 100) < 95:
            opp = ImprovementOpportunity(
                area="execution",
                issue=f"Success rate is {adaptive_insights['overall_success_rate']}%, below optimal 95%",
                suggestion="Improve error handling and retry logic in execution engine",
                impact="high",
                confidence=0.9
            )
            opportunities.append(opp)
        
        # Analyze decision confidence
        avg_confidence = decision_insights.get("avg_confidence", 0)
        if avg_confidence < 0.7:
            opp = ImprovementOpportunity(
                area="decision_making",
                issue=f"Average decision confidence is {avg_confidence}, below optimal 0.7",
                suggestion="Enhance decision rules with more context factors",
                impact="medium",
                confidence=0.8
            )
            opportunities.append(opp)
        
        # Analyze patterns with low success
        if "worst_pattern" in adaptive_insights and adaptive_insights["worst_pattern"]:
            worst = adaptive_insights["worst_pattern"]
            if worst["success_rate"] < 80:
                opp = ImprovementOpportunity(
                    area="task_decomposition",
                    issue=f"Pattern '{worst['name']}' has only {worst['success_rate']}% success",
                    suggestion=f"Refine task decomposition for {worst['name']} pattern",
                    impact="high",
                    confidence=0.85
                )
                opportunities.append(opp)
        
        # Analyze latency
        if metrics.get("avg_latencies"):
            high_latency_services = [
                svc for svc, lat in metrics["avg_latencies"].items() 
                if lat > 1000  # > 1 second
            ]
            if high_latency_services:
                opp = ImprovementOpportunity(
                    area="performance",
                    issue=f"High latency detected in: {', '.join(high_latency_services)}",
                    suggestion="Implement caching or optimize service calls",
                    impact="medium",
                    confidence=0.75
                )
                opportunities.append(opp)
        
        # Analyze error rates
        if metrics.get("errors"):
            high_error_services = [
                svc for svc, count in metrics["errors"].items()
                if count > 5
            ]
            if high_error_services:
                opp = ImprovementOpportunity(
                    area="reliability",
                    issue=f"High error count in: {', '.join(high_error_services)}",
                    suggestion="Add circuit breaker or improve error handling",
                    impact="high",
                    confidence=0.9
                )
                opportunities.append(opp)
        
        # Store opportunities
        self.opportunities.extend(opportunities)
        return opportunities
    
    def prioritize_improvements(self) -> List[ImprovementOpportunity]:
        """Prioritize improvements by impact and confidence"""
        impact_scores = {"high": 3, "medium": 2, "low": 1}
        
        scored = []
        for opp in self.opportunities:
            if not opp.applied:
                score = impact_scores[opp.impact] * opp.confidence
                scored.append((score, opp))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return [opp for score, opp in scored]
    
    def generate_improvement_plan(self) -> Dict:
        """Generate actionable improvement plan"""
        prioritized = self.prioritize_improvements()
        
        immediate = []  # High impact, high confidence
        scheduled = []  # Medium impact or confidence
        backlog = []    # Low impact or confidence
        
        for opp in prioritized:
            if opp.impact == "high" and opp.confidence >= 0.8:
                immediate.append(opp.to_dict())
            elif opp.impact in ["high", "medium"] and opp.confidence >= 0.6:
                scheduled.append(opp.to_dict())
            else:
                backlog.append(opp.to_dict())
        
        return {
            "immediate_actions": immediate,
            "scheduled_improvements": scheduled,
            "backlog": backlog,
            "total_opportunities": len(prioritized)
        }
    
    def apply_improvement(self, opportunity: ImprovementOpportunity) -> Dict:
        """Apply an improvement (simulated for now)"""
        # In real implementation, this would modify code/config
        opportunity.applied = True
        
        improvement_record = {
            "opportunity": opportunity.to_dict(),
            "applied_at": datetime.now().isoformat(),
            "status": "applied",
            "expected_impact": opportunity.impact
        }
        
        self.improvements_applied.append(improvement_record)
        return improvement_record
    
    def measure_improvement_impact(self, before_metrics: Dict, after_metrics: Dict) -> Dict:
        """Measure impact of applied improvements"""
        improvements = []
        
        # Compare success rates
        before_success = before_metrics.get("overall_success_rate", 0)
        after_success = after_metrics.get("overall_success_rate", 0)
        if after_success > before_success:
            improvements.append({
                "metric": "success_rate",
                "before": before_success,
                "after": after_success,
                "improvement": after_success - before_success
            })
        
        # Compare confidence
        before_conf = before_metrics.get("avg_confidence", 0)
        after_conf = after_metrics.get("avg_confidence", 0)
        if after_conf > before_conf:
            improvements.append({
                "metric": "decision_confidence",
                "before": before_conf,
                "after": after_conf,
                "improvement": after_conf - before_conf
            })
        
        return {
            "improvements_detected": len(improvements),
            "improvements": improvements,
            "overall_impact": "positive" if len(improvements) > 0 else "neutral"
        }
    
    def get_improvement_insights(self) -> Dict:
        """Get insights about self-improvement"""
        return {
            "total_opportunities_identified": len(self.opportunities),
            "improvements_applied": len(self.improvements_applied),
            "pending_opportunities": len([o for o in self.opportunities if not o.applied]),
            "areas_analyzed": list(set(o.area for o in self.opportunities)),
            "recent_improvements": [i for i in self.improvements_applied[-5:]]
        }

# Global self-improvement engine
self_improvement_engine = SelfImprovementEngine()
