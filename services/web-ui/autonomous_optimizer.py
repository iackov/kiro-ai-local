"""
Autonomous Optimizer - Self-analysis and self-improvement
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio

class AutonomousOptimizer:
    def __init__(self):
        self.analysis_history = []
        self.improvements_applied = []
        self.last_analysis = None
        self.optimization_interval = 300  # 5 минут
        
    async def analyze_system_performance(self, metrics_store, adaptive_planner, decision_engine) -> Dict:
        """Автоматический анализ производительности системы"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "issues": [],
            "recommendations": [],
            "auto_actions": []
        }
        
        # Получаем метрики
        stats = metrics_store.get_stats()
        performance = metrics_store.analyze_performance()
        
        # Анализ 1: Success Rate
        if stats.get("total_queries", 0) > 10:
            success_rate = (stats["total_queries"] - sum(stats["errors"].values())) / stats["total_queries"] * 100
            
            if success_rate < 80:
                analysis["issues"].append({
                    "type": "low_success_rate",
                    "severity": "high",
                    "value": success_rate,
                    "description": f"Success rate {success_rate:.1f}% ниже порога 80%"
                })
                analysis["recommendations"].append({
                    "action": "review_failed_tasks",
                    "priority": "high",
                    "description": "Проанализировать причины неудачных выполнений"
                })
        
        # Анализ 2: Latency
        avg_latencies = stats.get("avg_latencies", {})
        for service, latency in avg_latencies.items():
            if latency > 1000:  # > 1 секунды
                analysis["issues"].append({
                    "type": "high_latency",
                    "severity": "medium",
                    "service": service,
                    "value": latency,
                    "description": f"Сервис {service} имеет высокую задержку {latency:.0f}ms"
                })
                analysis["auto_actions"].append({
                    "action": "optimize_service",
                    "service": service,
                    "description": f"Оптимизировать производительность {service}"
                })
        
        # Анализ 3: Error Rate
        total_errors = sum(stats.get("errors", {}).values())
        if total_errors > 5:
            analysis["issues"].append({
                "type": "high_error_rate",
                "severity": "high",
                "value": total_errors,
                "description": f"Обнаружено {total_errors} ошибок"
            })
            analysis["recommendations"].append({
                "action": "investigate_errors",
                "priority": "high",
                "description": "Исследовать причины ошибок"
            })
        
        # Анализ 4: Adaptive Learning
        adaptive_insights = adaptive_planner.get_learning_insights()
        if adaptive_insights.get("total_patterns", 0) < 5:
            analysis["recommendations"].append({
                "action": "increase_learning_data",
                "priority": "medium",
                "description": "Недостаточно данных для обучения, выполнить больше задач"
            })
        
        # Анализ 5: Decision Quality
        decision_insights = decision_engine.get_decision_insights()
        if decision_insights.get("total_decisions", 0) > 0:
            decision_types = decision_insights.get("decision_types", {})
            require_approval_count = decision_types.get("require_approval", 0)
            total_decisions = decision_insights["total_decisions"]
            
            if require_approval_count / total_decisions > 0.5:
                analysis["issues"].append({
                    "type": "too_many_approvals",
                    "severity": "medium",
                    "value": require_approval_count / total_decisions * 100,
                    "description": f"{require_approval_count / total_decisions * 100:.1f}% решений требуют подтверждения"
                })
                analysis["auto_actions"].append({
                    "action": "adjust_decision_thresholds",
                    "description": "Скорректировать пороги принятия решений для большей автономности"
                })
        
        self.analysis_history.append(analysis)
        self.last_analysis = datetime.now()
        
        return analysis
    
    async def apply_auto_improvements(self, analysis: Dict, http_client) -> List[Dict]:
        """Автоматически применить улучшения"""
        applied = []
        
        for action in analysis.get("auto_actions", []):
            try:
                if action["action"] == "optimize_service":
                    # Здесь можно добавить реальную оптимизацию
                    result = await self._optimize_service(action["service"])
                    applied.append({
                        "action": action["action"],
                        "service": action["service"],
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                
                elif action["action"] == "adjust_decision_thresholds":
                    result = await self._adjust_decision_thresholds()
                    applied.append({
                        "action": action["action"],
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                
            except Exception as e:
                print(f"✗ Failed to apply improvement: {e}")
        
        self.improvements_applied.extend(applied)
        return applied
    
    async def _optimize_service(self, service: str) -> Dict:
        """Оптимизация сервиса"""
        # Placeholder для реальной оптимизации
        return {
            "success": True,
            "message": f"Service {service} optimization scheduled",
            "actions": ["cache_warming", "connection_pooling"]
        }
    
    async def _adjust_decision_thresholds(self) -> Dict:
        """Корректировка порогов принятия решений"""
        # Placeholder для реальной корректировки
        return {
            "success": True,
            "message": "Decision thresholds adjusted for higher autonomy",
            "changes": {
                "confidence_threshold": "lowered by 0.05",
                "auto_execute_threshold": "increased"
            }
        }
    
    def should_run_analysis(self) -> bool:
        """Проверить, нужно ли запустить анализ"""
        if self.last_analysis is None:
            return True
        
        time_since_last = datetime.now() - self.last_analysis
        return time_since_last.total_seconds() >= self.optimization_interval
    
    def get_optimization_report(self) -> Dict:
        """Получить отчет об оптимизации"""
        return {
            "total_analyses": len(self.analysis_history),
            "total_improvements": len(self.improvements_applied),
            "last_analysis": self.last_analysis.isoformat() if self.last_analysis else None,
            "recent_improvements": self.improvements_applied[-5:] if self.improvements_applied else [],
            "optimization_interval_seconds": self.optimization_interval
        }
    
    async def continuous_optimization_loop(self, metrics_store, adaptive_planner, decision_engine, http_client):
        """Непрерывный цикл оптимизации"""
        print("🔄 Starting continuous optimization loop...")
        
        while True:
            try:
                if self.should_run_analysis():
                    print("🔍 Running autonomous system analysis...")
                    
                    # Анализ
                    analysis = await self.analyze_system_performance(
                        metrics_store, adaptive_planner, decision_engine
                    )
                    
                    print(f"✓ Analysis complete: {len(analysis['issues'])} issues, {len(analysis['recommendations'])} recommendations")
                    
                    # Автоматическое применение улучшений
                    if analysis.get("auto_actions"):
                        print(f"🔧 Applying {len(analysis['auto_actions'])} auto-improvements...")
                        applied = await self.apply_auto_improvements(analysis, http_client)
                        print(f"✓ Applied {len(applied)} improvements")
                
                # Ждем перед следующим циклом
                await asyncio.sleep(self.optimization_interval)
                
            except Exception as e:
                print(f"✗ Optimization loop error: {e}")
                await asyncio.sleep(60)  # Ждем минуту при ошибке

# Global optimizer
autonomous_optimizer = AutonomousOptimizer()
