"""
Metrics collection and analysis for self-monitoring
"""
from datetime import datetime
from collections import defaultdict
from typing import Dict, List
import time
from functools import lru_cache

class MetricsStore:
    """In-memory metrics storage"""
    
    def __init__(self):
        self.queries = []  # All queries
        self.latencies = defaultdict(list)  # Service latencies
        self.errors = defaultdict(int)  # Error counts
        self.patterns = defaultdict(int)  # Query patterns
        self.suggestions_history = []  # Suggestion outcomes
        self.user_preferences = {
            "applied_suggestions": [],
            "dismissed_suggestions": [],
            "preferred_actions": defaultdict(int),
            "avoided_actions": defaultdict(int)
        }
        self.service_health = {}  # Service health tracking
        self.auto_actions = []  # Autonomous actions taken
        self._insights_cache = None  # Cache for insights
        self._insights_cache_time = 0  # Cache timestamp
        self._analysis_cache = None  # Cache for analysis
        self._analysis_cache_time = 0  # Cache timestamp
        
    def record_query(self, service: str, query: str, latency: float, success: bool):
        """Record a query"""
        self.queries.append({
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "query": query,
            "latency": latency,
            "success": success
        })
        
        # Keep only last 1000 queries
        if len(self.queries) > 1000:
            self.queries = self.queries[-1000:]
        
        # Record latency
        self.latencies[service].append(latency)
        if len(self.latencies[service]) > 100:
            self.latencies[service] = self.latencies[service][-100:]
        
        # Record errors
        if not success:
            self.errors[service] += 1
        
        # Detect patterns (simple keyword extraction)
        keywords = query.lower().split()
        for word in keywords:
            if len(word) > 3:  # Ignore short words
                self.patterns[word] += 1
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        total_queries = len(self.queries)
        
        # Calculate average latencies
        avg_latencies = {}
        for service, lats in self.latencies.items():
            if lats:
                avg_latencies[service] = sum(lats) / len(lats)
        
        # Get top patterns
        top_patterns = sorted(
            self.patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Recent queries
        recent = self.queries[-10:] if self.queries else []
        
        return {
            "total_queries": total_queries,
            "avg_latencies": avg_latencies,
            "errors": dict(self.errors),
            "top_patterns": dict(top_patterns),
            "recent_queries": recent
        }
    
    def analyze_performance(self) -> Dict:
        """Analyze performance and detect issues (with caching)"""
        # Cache for 5 seconds
        now = time.time()
        if self._analysis_cache and (now - self._analysis_cache_time) < 5:
            return self._analysis_cache
        
        issues = []
        suggestions = []
        
        # Check RAG latency
        rag_lats = self.latencies.get("rag", [])
        if rag_lats and len(rag_lats) > 5:
            avg_rag = sum(rag_lats) / len(rag_lats)
            if avg_rag > 500:  # >500ms is slow
                issues.append({
                    "type": "performance",
                    "service": "rag",
                    "metric": "latency",
                    "value": avg_rag,
                    "threshold": 500
                })
                
                # Adaptive: Check if user likes Redis suggestions
                redis_preference = self.user_preferences["preferred_actions"].get("Add Redis cache service", 0)
                redis_avoided = self.user_preferences["avoided_actions"].get("Add Redis cache service", 0)
                
                # Adjust priority based on learning
                priority = "high"
                if redis_avoided > redis_preference:
                    priority = "low"  # User doesn't like Redis suggestions
                elif redis_preference > 0:
                    priority = "high"  # User accepted Redis before
                
                suggestions.append({
                    "issue": f"RAG queries averaging {avg_rag:.0f}ms (slow)",
                    "suggestion": "Add Redis cache to speed up repeated queries",
                    "expected_improvement": f"50-80% faster (from {avg_rag:.0f}ms to ~100ms)",
                    "action": "Add Redis cache service",
                    "priority": priority,
                    "learning_adjusted": redis_preference > 0 or redis_avoided > 0
                })
        
        # Check query volume (proactive suggestion)
        if len(self.queries) > 50:
            # Analyze if caching would help
            unique_queries = len(set(q["query"] for q in self.queries))
            repeat_rate = 1 - (unique_queries / len(self.queries))
            
            if repeat_rate > 0.3:  # >30% repeated queries
                # Adaptive: Check cache-related preferences
                cache_actions = [k for k in self.user_preferences["preferred_actions"].keys() if "cache" in k.lower() or "redis" in k.lower()]
                cache_preference_score = sum(self.user_preferences["preferred_actions"].get(k, 0) for k in cache_actions)
                
                priority = "medium"
                if cache_preference_score > 2:
                    priority = "high"  # User likes caching solutions
                
                suggestions.append({
                    "issue": f"High query repetition detected ({repeat_rate*100:.0f}% repeated)",
                    "suggestion": "Add Redis cache - many queries are repeated",
                    "expected_improvement": f"Cache {repeat_rate*100:.0f}% of queries, reduce load significantly",
                    "action": "Add Redis cache service",
                    "priority": priority,
                    "learning_adjusted": cache_preference_score > 0
                })
        
        # Check error rates
        for service, error_count in self.errors.items():
            if error_count > 5:
                issues.append({
                    "type": "reliability",
                    "service": service,
                    "metric": "errors",
                    "value": error_count,
                    "threshold": 5
                })
                suggestions.append({
                    "issue": f"{service} has {error_count} errors",
                    "suggestion": f"Investigate {service} service logs and restart if needed",
                    "expected_improvement": "Improved reliability",
                    "action": f"Check {service} service health",
                    "priority": "high",
                    "learning_adjusted": False
                })
        
        # Check patterns - Docker focus
        docker_queries = self.patterns.get("docker", 0)
        if docker_queries > 10:
            # Adaptive: Check if user dismissed similar suggestions
            optimize_avoided = self.user_preferences["avoided_actions"].get("Optimize RAG for Docker content", 0)
            
            if optimize_avoided == 0:  # Only suggest if not previously dismissed
                suggestions.append({
                    "issue": f"Many Docker-related queries ({docker_queries} times)",
                    "suggestion": "Create Docker-specific RAG collection for faster, more accurate searches",
                    "expected_improvement": "30-40% faster Docker queries, better relevance",
                    "action": "Optimize RAG for Docker content",
                    "priority": "low",
                    "learning_adjusted": False
                })
        
        # Check patterns - Redis interest
        redis_queries = self.patterns.get("redis", 0)
        if redis_queries > 5:
            # Adaptive: Only suggest if user hasn't dismissed Redis before
            redis_dismissed = any("redis" in action.lower() for action in self.user_preferences["dismissed_suggestions"])
            
            if not redis_dismissed:
                suggestions.append({
                    "issue": f"Frequent Redis queries ({redis_queries} times)",
                    "suggestion": "Add Redis service to the stack for experimentation",
                    "expected_improvement": "Enable Redis caching and hands-on learning",
                    "action": "Add Redis cache service",
                    "priority": "medium",
                    "learning_adjusted": True
                })
        
        # Sort suggestions by priority (high > medium > low)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        result = {
            "issues": issues,
            "suggestions": suggestions,
            "health_score": self._calculate_health_score(),
            "insights": self._generate_insights(),
            "learning_applied": any(s.get("learning_adjusted") for s in suggestions)
        }
        
        # Update cache
        self._analysis_cache = result
        self._analysis_cache_time = now
        
        return result
    
    def _generate_insights(self) -> List[str]:
        """Generate insights about usage patterns"""
        insights = []
        
        if len(self.queries) > 0:
            # Most active service
            services = [q["service"] for q in self.queries]
            most_used = max(set(services), key=services.count) if services else None
            if most_used:
                count = services.count(most_used)
                insights.append(f"Most used service: {most_used} ({count} queries)")
            
            # Top topics
            if self.patterns:
                top_topic = max(self.patterns.items(), key=lambda x: x[1])
                insights.append(f"Top topic: '{top_topic[0]}' ({top_topic[1]} mentions)")
            
            # Performance trend
            if len(self.queries) > 10:
                recent_lats = [q["latency"] for q in self.queries[-10:]]
                older_lats = [q["latency"] for q in self.queries[-20:-10]] if len(self.queries) > 20 else recent_lats
                
                if recent_lats and older_lats:
                    recent_avg = sum(recent_lats) / len(recent_lats)
                    older_avg = sum(older_lats) / len(older_lats)
                    
                    if recent_avg < older_avg * 0.9:
                        insights.append(f"Performance improving: {older_avg:.0f}ms → {recent_avg:.0f}ms")
                    elif recent_avg > older_avg * 1.1:
                        insights.append(f"Performance degrading: {older_avg:.0f}ms → {recent_avg:.0f}ms")
        
        return insights
    
    def _calculate_health_score(self) -> int:
        """Calculate overall health score (0-100)"""
        score = 100
        
        # Deduct for high latency
        for service, lats in self.latencies.items():
            if lats:
                avg = sum(lats) / len(lats)
                if avg > 500:
                    score -= 10
                elif avg > 300:
                    score -= 5
        
        # Deduct for errors
        total_errors = sum(self.errors.values())
        if total_errors > 10:
            score -= 20
        elif total_errors > 5:
            score -= 10
        
        return max(0, score)
    
    def record_suggestion_outcome(self, suggestion: Dict, action: str):
        """Record user's response to a suggestion"""
        outcome = {
            "timestamp": datetime.now().isoformat(),
            "suggestion": suggestion,
            "action": action,  # "applied" or "dismissed"
        }
        self.suggestions_history.append(outcome)
        
        # Keep only last 100
        if len(self.suggestions_history) > 100:
            self.suggestions_history = self.suggestions_history[-100:]
        
        # Update preferences
        if action == "applied":
            self.user_preferences["applied_suggestions"].append(suggestion["action"])
            self.user_preferences["preferred_actions"][suggestion["action"]] += 1
        elif action == "dismissed":
            self.user_preferences["dismissed_suggestions"].append(suggestion["action"])
            self.user_preferences["avoided_actions"][suggestion["action"]] += 1
    
    def get_learning_insights(self) -> Dict:
        """Get insights from learning history"""
        if not self.suggestions_history:
            return {
                "total_suggestions": 0,
                "applied_count": 0,
                "dismissed_count": 0,
                "acceptance_rate": 0,
                "insights": []
            }
        
        applied = [s for s in self.suggestions_history if s["action"] == "applied"]
        dismissed = [s for s in self.suggestions_history if s["action"] == "dismissed"]
        
        acceptance_rate = len(applied) / len(self.suggestions_history) if self.suggestions_history else 0
        
        insights = []
        
        # Most accepted action type
        if self.user_preferences["preferred_actions"]:
            top_action = max(
                self.user_preferences["preferred_actions"].items(),
                key=lambda x: x[1]
            )
            insights.append(f"User prefers: {top_action[0]} (applied {top_action[1]} times)")
        
        # Most avoided action type
        if self.user_preferences["avoided_actions"]:
            avoided_action = max(
                self.user_preferences["avoided_actions"].items(),
                key=lambda x: x[1]
            )
            insights.append(f"User avoids: {avoided_action[0]} (dismissed {avoided_action[1]} times)")
        
        # Acceptance trend
        if len(self.suggestions_history) > 5:
            recent = self.suggestions_history[-5:]
            recent_applied = len([s for s in recent if s["action"] == "applied"])
            recent_rate = recent_applied / len(recent)
            
            if recent_rate > 0.7:
                insights.append("User is actively accepting suggestions")
            elif recent_rate < 0.3:
                insights.append("User is cautious with suggestions")
        
        return {
            "total_suggestions": len(self.suggestions_history),
            "applied_count": len(applied),
            "dismissed_count": len(dismissed),
            "acceptance_rate": acceptance_rate,
            "insights": insights,
            "preferred_actions": dict(self.user_preferences["preferred_actions"]),
            "avoided_actions": dict(self.user_preferences["avoided_actions"])
        }
    
    def get_insights(self) -> Dict:
        """Get combined insights (metrics + learning) with caching"""
        # Cache for 3 seconds
        now = time.time()
        if self._insights_cache and (now - self._insights_cache_time) < 3:
            return self._insights_cache
        
        analysis = self.analyze_performance()
        learning = self.get_learning_insights()
        
        result = {
            "insights": analysis["insights"] + learning["insights"],
            "suggestions": analysis["suggestions"],
            "health_score": analysis["health_score"],
            "learning_stats": {
                "total_suggestions": learning["total_suggestions"],
                "acceptance_rate": learning["acceptance_rate"]
            }
        }
        
        # Update cache
        self._insights_cache = result
        self._insights_cache_time = now
        
        return result
    
    def record_service_health(self, service: str, status: str, details: Dict = None):
        """Record service health status"""
        self.service_health[service] = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
    
    def detect_auto_healing_opportunities(self) -> List[Dict]:
        """Detect services that need auto-healing"""
        opportunities = []
        
        # Check for high error rates
        for service, error_count in self.errors.items():
            if error_count > 10:  # High error threshold
                opportunities.append({
                    "type": "auto_heal",
                    "service": service,
                    "issue": f"High error rate: {error_count} errors",
                    "action": f"Restart {service} service",
                    "confidence": "high",
                    "safe": True  # Restart is generally safe
                })
        
        # Check for performance degradation
        for service, lats in self.latencies.items():
            if len(lats) > 20:  # Need enough data
                recent_avg = sum(lats[-10:]) / len(lats[-10:])
                older_avg = sum(lats[-20:-10]) / len(lats[-20:-10])
                
                if recent_avg > older_avg * 2:  # 100% degradation
                    opportunities.append({
                        "type": "auto_optimize",
                        "service": service,
                        "issue": f"Performance degraded: {older_avg:.0f}ms → {recent_avg:.0f}ms",
                        "action": f"Increase {service} memory",
                        "confidence": "medium",
                        "safe": True
                    })
        
        return opportunities
    
    def record_auto_action(self, action: Dict, result: str):
        """Record autonomous action taken"""
        self.auto_actions.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result
        })
        
        # Keep only last 50
        if len(self.auto_actions) > 50:
            self.auto_actions = self.auto_actions[-50:]
    
    def predict_future_issues(self) -> List[Dict]:
        """Predict future issues based on trends (Level 7: Planning)"""
        predictions = []
        
        # Predict latency degradation
        for service, lats in self.latencies.items():
            if len(lats) > 30:
                # Analyze trend
                recent_30 = lats[-30:]
                first_10 = sum(recent_30[:10]) / 10
                last_10 = sum(recent_30[-10:]) / 10
                
                if last_10 > first_10 * 1.2:  # 20% degradation
                    # Predict when it will become critical
                    degradation_rate = (last_10 - first_10) / 20  # per query
                    queries_until_critical = (1000 - last_10) / degradation_rate if degradation_rate > 0 else 999
                    
                    predictions.append({
                        "type": "latency_degradation",
                        "service": service,
                        "current": round(last_10, 0),
                        "trend": "increasing",
                        "predicted_critical_in": f"{int(queries_until_critical)} queries",
                        "recommended_action": f"Increase {service} resources proactively",
                        "confidence": "medium",
                        "urgency": "low" if queries_until_critical > 100 else "high"
                    })
        
        # Predict error rate increase
        for service, error_count in self.errors.items():
            if error_count > 3:
                # Check if errors are accelerating
                recent_queries = [q for q in self.queries[-20:] if q["service"] == service]
                if len(recent_queries) > 10:
                    recent_errors = len([q for q in recent_queries if not q["success"]])
                    error_rate = recent_errors / len(recent_queries)
                    
                    if error_rate > 0.2:  # >20% error rate
                        predictions.append({
                            "type": "error_rate_increase",
                            "service": service,
                            "current_rate": f"{error_rate*100:.0f}%",
                            "trend": "increasing",
                            "predicted_critical_in": "soon",
                            "recommended_action": f"Investigate {service} logs and prepare restart",
                            "confidence": "high",
                            "urgency": "high"
                        })
        
        # Predict resource exhaustion based on patterns
        if len(self.queries) > 100:
            # Check query rate acceleration
            last_50_time = self._calculate_time_span(self.queries[-50:])
            prev_50_time = self._calculate_time_span(self.queries[-100:-50])
            
            if last_50_time > 0 and prev_50_time > 0:
                last_rate = 50 / last_50_time
                prev_rate = 50 / prev_50_time
                
                if last_rate > prev_rate * 1.5:  # 50% increase in rate
                    predictions.append({
                        "type": "load_increase",
                        "current_rate": f"{last_rate:.1f} req/s",
                        "previous_rate": f"{prev_rate:.1f} req/s",
                        "trend": "accelerating",
                        "predicted_critical_in": "10-20 minutes",
                        "recommended_action": "Scale up services or enable caching",
                        "confidence": "medium",
                        "urgency": "medium"
                    })
        
        return predictions
    
    def _calculate_time_span(self, queries: List[Dict]) -> float:
        """Calculate time span of queries in seconds"""
        if len(queries) < 2:
            return 0
        
        from datetime import datetime
        first = datetime.fromisoformat(queries[0]["timestamp"])
        last = datetime.fromisoformat(queries[-1]["timestamp"])
        return (last - first).total_seconds()
    
    def generate_action_plan(self) -> Dict:
        """Generate proactive action plan (Level 7: Planning)"""
        predictions = self.predict_future_issues()
        analysis = self.analyze_performance()
        
        # Prioritize actions
        immediate_actions = []
        planned_actions = []
        
        # From predictions
        for pred in predictions:
            if pred["urgency"] == "high":
                immediate_actions.append({
                    "priority": "immediate",
                    "reason": pred["type"],
                    "action": pred["recommended_action"],
                    "confidence": pred["confidence"]
                })
            else:
                planned_actions.append({
                    "priority": "planned",
                    "reason": pred["type"],
                    "action": pred["recommended_action"],
                    "confidence": pred["confidence"],
                    "schedule": pred.get("predicted_critical_in", "future")
                })
        
        # From current issues
        for issue in analysis["issues"]:
            immediate_actions.append({
                "priority": "immediate",
                "reason": f"{issue['service']} {issue['type']}",
                "action": f"Address {issue['service']} {issue['metric']} issue",
                "confidence": "high"
            })
        
        # From suggestions
        for suggestion in analysis["suggestions"]:
            if suggestion["priority"] == "high":
                immediate_actions.append({
                    "priority": "immediate",
                    "reason": suggestion["issue"],
                    "action": suggestion["action"],
                    "confidence": "high"
                })
            else:
                planned_actions.append({
                    "priority": "planned",
                    "reason": suggestion["issue"],
                    "action": suggestion["action"],
                    "confidence": "medium",
                    "schedule": "when convenient"
                })
        
        return {
            "predictions": predictions,
            "immediate_actions": immediate_actions,
            "planned_actions": planned_actions,
            "total_actions": len(immediate_actions) + len(planned_actions),
            "requires_attention": len(immediate_actions) > 0
        }

# Global metrics store
metrics_store = MetricsStore()
