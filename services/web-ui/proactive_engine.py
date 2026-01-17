"""
Proactive Action Engine - Predictive actions before problems occur
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio

class ProactiveAction:
    def __init__(self, action_type: str, reason: str, priority: str, auto_execute: bool = False):
        self.action_type = action_type
        self.reason = reason
        self.priority = priority
        self.auto_execute = auto_execute
        self.created_at = datetime.now()
        self.executed = False
        self.result = None
    
    def to_dict(self) -> Dict:
        return {
            "action_type": self.action_type,
            "reason": self.reason,
            "priority": self.priority,
            "auto_execute": self.auto_execute,
            "created_at": self.created_at.isoformat(),
            "executed": self.executed,
            "result": self.result
        }

class ProactiveEngine:
    def __init__(self):
        self.pending_actions = []
        self.executed_actions = []
        self.prediction_history = []
        
    async def predict_and_act(self, metrics_store, knowledge_store, http_client) -> List[ProactiveAction]:
        """Предсказать проблемы и создать проактивные действия"""
        actions = []
        
        stats = metrics_store.get_stats()
        
        # Предсказание 1: Рост количества ошибок
        errors_trend = self._analyze_error_trend(stats)
        if errors_trend == "increasing":
            action = ProactiveAction(
                action_type="preemptive_restart",
                reason="Обнаружен рост количества ошибок, превентивный перезапуск может предотвратить сбой",
                priority="medium",
                auto_execute=False  # Требует подтверждения для критичных действий
            )
            actions.append(action)
        
        # Предсказание 2: Деградация производительности
        latency_trend = self._analyze_latency_trend(stats)
        if latency_trend == "degrading":
            action = ProactiveAction(
                action_type="cache_warmup",
                reason="Производительность снижается, прогрев кэша может улучшить отклик",
                priority="low",
                auto_execute=True  # Безопасное действие
            )
            actions.append(action)
        
        # Предсказание 3: Недостаток данных для обучения
        if stats.get("total_queries", 0) < 20:
            action = ProactiveAction(
                action_type="generate_training_data",
                reason="Недостаточно данных для эффективного обучения, генерация тестовых задач",
                priority="low",
                auto_execute=True
            )
            actions.append(action)
        
        # Предсказание 4: Устаревшие знания в RAG
        if knowledge_store:
            knowledge_age = await self._check_knowledge_freshness(knowledge_store, http_client)
            if knowledge_age > 3600:  # Старше 1 часа
                action = ProactiveAction(
                    action_type="refresh_knowledge",
                    reason="Знания в базе устарели, обновление может улучшить качество ответов",
                    priority="low",
                    auto_execute=True
                )
                actions.append(action)
        
        # Предсказание 5: Потенциальная перегрузка
        if stats.get("total_queries", 0) > 100:
            avg_latency = sum(stats.get("avg_latencies", {}).values()) / max(len(stats.get("avg_latencies", {})), 1)
            if avg_latency > 500:
                action = ProactiveAction(
                    action_type="scale_resources",
                    reason="Высокая нагрузка и задержка, масштабирование ресурсов предотвратит деградацию",
                    priority="high",
                    auto_execute=False
                )
                actions.append(action)
        
        # Сохраняем предсказания
        self.prediction_history.append({
            "timestamp": datetime.now().isoformat(),
            "predictions": len(actions),
            "actions": [a.to_dict() for a in actions]
        })
        
        # Добавляем в очередь
        self.pending_actions.extend(actions)
        
        return actions
    
    def _analyze_error_trend(self, stats: Dict) -> str:
        """Анализ тренда ошибок"""
        total_errors = sum(stats.get("errors", {}).values())
        total_queries = stats.get("total_queries", 1)
        
        error_rate = total_errors / total_queries
        
        if error_rate > 0.1:  # > 10% ошибок
            return "increasing"
        return "stable"
    
    def _analyze_latency_trend(self, stats: Dict) -> str:
        """Анализ тренда задержки"""
        avg_latencies = stats.get("avg_latencies", {})
        if not avg_latencies or len(avg_latencies) == 0:
            return "stable"
        
        avg_latency = sum(avg_latencies.values()) / len(avg_latencies)
        
        if avg_latency > 1000:  # > 1 секунды
            return "degrading"
        return "stable"
    
    async def _check_knowledge_freshness(self, knowledge_store, http_client) -> int:
        """Проверка свежести знаний (возвращает возраст в секундах)"""
        try:
            stats = knowledge_store.get_stats()
            # Упрощенная проверка - в реальности нужно проверять timestamp последнего добавления
            if stats.get("stored_executions", 0) == 0:
                return 7200  # 2 часа если нет данных
            return 1800  # 30 минут по умолчанию
        except:
            return 0
    
    async def execute_proactive_actions(self, http_client) -> List[Dict]:
        """Выполнить проактивные действия"""
        executed = []
        
        for action in self.pending_actions[:]:
            if action.auto_execute and not action.executed:
                try:
                    result = await self._execute_action(action, http_client)
                    action.executed = True
                    action.result = result
                    
                    executed.append({
                        "action": action.to_dict(),
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    self.executed_actions.append(action)
                    self.pending_actions.remove(action)
                    
                    print(f"✓ Proactive action executed: {action.action_type}")
                    
                except Exception as e:
                    print(f"✗ Failed to execute proactive action: {e}")
        
        return executed
    
    async def _execute_action(self, action: ProactiveAction, http_client) -> Dict:
        """Выполнить конкретное действие"""
        if action.action_type == "cache_warmup":
            return await self._cache_warmup(http_client)
        
        elif action.action_type == "generate_training_data":
            return await self._generate_training_data(http_client)
        
        elif action.action_type == "refresh_knowledge":
            return await self._refresh_knowledge(http_client)
        
        elif action.action_type == "preemptive_restart":
            return {"success": True, "message": "Scheduled for manual approval"}
        
        elif action.action_type == "scale_resources":
            return {"success": True, "message": "Scaling recommendation created"}
        
        return {"success": False, "message": "Unknown action type"}
    
    async def _cache_warmup(self, http_client) -> Dict:
        """Прогрев кэша"""
        # Placeholder - в реальности делать запросы к часто используемым данным
        return {
            "success": True,
            "message": "Cache warmed up",
            "items_cached": 10
        }
    
    async def _generate_training_data(self, http_client) -> Dict:
        """Генерация тренировочных данных"""
        # Placeholder - в реальности создавать тестовые задачи
        return {
            "success": True,
            "message": "Training data generated",
            "tasks_created": 5
        }
    
    async def _refresh_knowledge(self, http_client) -> Dict:
        """Обновление базы знаний"""
        # Placeholder - в реальности обновлять устаревшие документы
        return {
            "success": True,
            "message": "Knowledge base refreshed",
            "documents_updated": 3
        }
    
    def get_pending_actions(self) -> List[Dict]:
        """Получить ожидающие действия"""
        return [a.to_dict() for a in self.pending_actions if not a.executed]
    
    def get_executed_actions(self, limit: int = 10) -> List[Dict]:
        """Получить выполненные действия"""
        return [a.to_dict() for a in self.executed_actions[-limit:]]
    
    def get_stats(self) -> Dict:
        """Статистика проактивных действий"""
        total_executed = len(self.executed_actions)
        auto_executed = len([a for a in self.executed_actions if a.auto_execute])
        
        return {
            "pending_actions": len([a for a in self.pending_actions if not a.executed]),
            "executed_actions": total_executed,
            "total_predictions": len(self.prediction_history),
            "auto_execute_rate": (auto_executed / total_executed * 100) if total_executed > 0 else 0
        }
    
    async def continuous_proactive_loop(self, metrics_store, knowledge_store, http_client):
        """Непрерывный цикл проактивных действий"""
        print("🔮 Starting proactive action loop...")
        
        while True:
            try:
                # Предсказываем и создаем действия
                actions = await self.predict_and_act(metrics_store, knowledge_store, http_client)
                
                if actions:
                    print(f"🔮 Predicted {len(actions)} potential issues, created proactive actions")
                
                # Выполняем автоматические действия
                executed = await self.execute_proactive_actions(http_client)
                
                if executed:
                    print(f"✓ Executed {len(executed)} proactive actions")
                
                # Ждем перед следующим циклом (10 минут)
                await asyncio.sleep(600)
                
            except Exception as e:
                print(f"✗ Proactive loop error: {e}")
                await asyncio.sleep(60)

# Global proactive engine
proactive_engine = ProactiveEngine()
