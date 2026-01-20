#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Комплексный многоэтапный тест всей системы
Проверяет все уровни автономности и интеграцию компонентов
"""

import requests
import time
import json
from datetime import datetime

class SystemTester:
    def __init__(self, base_url='http://localhost:9000'):
        self.base_url = base_url
        self.test_results = []
        self.start_time = None
        
    def log(self, message, level='INFO'):
        """Логирование с временной меткой"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
    
    def test_step(self, name, func):
        """Выполнить тестовый шаг"""
        self.log(f"Starting: {name}", "TEST")
        start = time.time()
        try:
            result = func()
            duration = time.time() - start
            self.test_results.append({
                "name": name,
                "status": "PASS" if result else "FAIL",
                "duration": duration,
                "result": result
            })
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status}: {name} ({duration:.2f}s)", "RESULT")
            return result
        except Exception as e:
            duration = time.time() - start
            self.test_results.append({
                "name": name,
                "status": "ERROR",
                "duration": duration,
                "error": str(e)
            })
            self.log(f"❌ ERROR: {name} - {str(e)}", "ERROR")
            return False
    
    def print_summary(self):
        """Вывести итоговую сводку"""
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        errors = len([r for r in self.test_results if r["status"] == "ERROR"])
        total_time = time.time() - self.start_time
        
        print("\n" + "="*70)
        print("📊 ИТОГОВАЯ СВОДКА ТЕСТИРОВАНИЯ")
        print("="*70)
        print(f"Всего тестов: {total}")
        print(f"✅ Успешно: {passed}")
        print(f"❌ Провалено: {failed}")
        print(f"⚠️  Ошибки: {errors}")
        print(f"⏱️  Общее время: {total_time:.2f}s")
        print(f"📈 Success Rate: {(passed/total*100):.1f}%")
        print("="*70)
        
        if failed > 0 or errors > 0:
            print("\n❌ Проваленные тесты:")
            for r in self.test_results:
                if r["status"] in ["FAIL", "ERROR"]:
                    print(f"   - {r['name']}: {r.get('error', 'Failed')}")

def main():
    tester = SystemTester()
    tester.start_time = time.time()
    
    print("\n" + "="*70)
    print("🚀 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ AI AUTONOMOUS SYSTEM")
    print("="*70 + "\n")
    
    # ========== ЭТАП 1: БАЗОВАЯ ИНФРАСТРУКТУРА ==========
    print("\n📦 ЭТАП 1: БАЗОВАЯ ИНФРАСТРУКТУРА")
    print("-" * 70)
    
    def test_services_health():
        """Проверка здоровья всех сервисов"""
        resp = requests.get(f'{tester.base_url}/api/status', timeout=5)
        status = resp.json()
        all_healthy = all(s.get('status') == 'healthy' for s in status.values())
        tester.log(f"Services: {', '.join([f'{k}={v.get('status')}' for k,v in status.items()])}")
        return all_healthy
    
    def test_dashboard_accessible():
        """Проверка доступности dashboard"""
        resp = requests.get(f'{tester.base_url}/dashboard', timeout=5)
        return resp.status_code == 200
    
    def test_chat_accessible():
        """Проверка доступности чата"""
        resp = requests.get(f'{tester.base_url}/chat', timeout=5)
        return resp.status_code == 200
    
    tester.test_step("1.1 Проверка здоровья сервисов", test_services_health)
    tester.test_step("1.2 Доступность Dashboard", test_dashboard_accessible)
    tester.test_step("1.3 Доступность Chat", test_chat_accessible)
    
    # ========== ЭТАП 2: АВТОНОМНОЕ ВЫПОЛНЕНИЕ ==========
    print("\n🤖 ЭТАП 2: АВТОНОМНОЕ ВЫПОЛНЕНИЕ ЗАДАЧ")
    print("-" * 70)
    
    task_id = None
    
    def test_task_execution():
        """Выполнение задачи с auto_execute"""
        nonlocal task_id
        resp = requests.post(
            f'{tester.base_url}/api/autonomous',
            data={
                'message': 'Create a simple hello world program. Save to playground/hello.py',
                'auto_execute': 'true'
            },
            timeout=120
        )
        result = resp.json()
        if result.get('task_result'):
            task_id = result['task_result'].get('task_id')
            summary = result['task_result']['summary']
            tester.log(f"Task executed: {summary.get('successful')}/{summary.get('total_steps')} steps")
            return summary.get('success_rate', 0) == 100
        return False
    
    def test_intent_detection():
        """Проверка определения намерений"""
        resp = requests.post(
            f'{tester.base_url}/api/autonomous',
            data={'message': 'Create test file', 'auto_execute': 'false'},
            timeout=30
        )
        result = resp.json()
        intent = result.get('intent')
        tester.log(f"Detected intent: {intent}")
        return intent == 'create'
    
    def test_decision_making():
        """Проверка принятия решений"""
        resp = requests.post(
            f'{tester.base_url}/api/autonomous',
            data={'message': 'Create safe test', 'auto_execute': 'true'},
            timeout=30
        )
        result = resp.json()
        if result.get('execution_plan'):
            decision = result['execution_plan'].get('autonomous_decision', {})
            tester.log(f"Decision: {decision.get('action')}, confidence: {decision.get('confidence')}")
            return decision.get('action') in ['auto_execute', 'suggest_execute']
        return False
    
    tester.test_step("2.1 Автономное выполнение задачи", test_task_execution)
    tester.test_step("2.2 Определение намерений", test_intent_detection)
    tester.test_step("2.3 Принятие решений", test_decision_making)
    
    # ========== ЭТАП 3: KNOWLEDGE STORE ==========
    print("\n🧠 ЭТАП 3: KNOWLEDGE STORE И ОБУЧЕНИЕ")
    print("-" * 70)
    
    def test_knowledge_store_active():
        """Проверка активности Knowledge Store"""
        resp = requests.get(f'{tester.base_url}/api/knowledge/stats', timeout=5)
        stats = resp.json()
        tester.log(f"Stored executions: {stats.get('stored_executions', 0)}")
        return stats.get('status') == 'active'
    
    def test_knowledge_storage():
        """Проверка сохранения знаний"""
        resp = requests.get(f'{tester.base_url}/api/knowledge/stats', timeout=5)
        stats = resp.json()
        return stats.get('stored_executions', 0) > 0
    
    def test_rag_query():
        """Проверка запросов к RAG"""
        resp = requests.post(
            'http://localhost:9001/query',
            json={'query': 'hello world', 'top_k': 3},
            timeout=10
        )
        result = resp.json()
        tester.log(f"RAG results: {result.get('total_results', 0)} documents")
        return resp.status_code == 200
    
    tester.test_step("3.1 Knowledge Store активен", test_knowledge_store_active)
    tester.test_step("3.2 Сохранение результатов", test_knowledge_storage)
    tester.test_step("3.3 Запросы к RAG", test_rag_query)
    
    # ========== ЭТАП 4: САМОАНАЛИЗ И ОПТИМИЗАЦИЯ ==========
    print("\n🔍 ЭТАП 4: САМОАНАЛИЗ И ОПТИМИЗАЦИЯ")
    print("-" * 70)
    
    def test_autonomous_optimizer():
        """Проверка автономного оптимизатора"""
        resp = requests.get(f'{tester.base_url}/api/autonomous/status', timeout=5)
        status = resp.json()
        optimizer = status.get('optimizer', {})
        tester.log(f"Analyses: {optimizer.get('total_analyses', 0)}, Improvements: {optimizer.get('total_improvements', 0)}")
        return status.get('is_active') == True
    
    def test_manual_analysis():
        """Ручной запуск анализа"""
        resp = requests.post(f'{tester.base_url}/api/autonomous/analyze', timeout=30)
        result = resp.json()
        if result.get('status') == 'completed':
            analysis = result.get('analysis', {})
            tester.log(f"Issues: {len(analysis.get('issues', []))}, Recommendations: {len(analysis.get('recommendations', []))}")
            return True
        return False
    
    def test_metrics_collection():
        """Проверка сбора метрик"""
        resp = requests.get(f'{tester.base_url}/api/production/metrics', timeout=5)
        metrics = resp.json()
        tester.log(f"Total requests: {metrics.get('performance', {}).get('total_requests', 0)}")
        return resp.status_code == 200
    
    tester.test_step("4.1 Autonomous Optimizer активен", test_autonomous_optimizer)
    tester.test_step("4.2 Ручной анализ системы", test_manual_analysis)
    tester.test_step("4.3 Сбор метрик", test_metrics_collection)
    
    # ========== ЭТАП 5: ПРОАКТИВНЫЕ ДЕЙСТВИЯ ==========
    print("\n🔮 ЭТАП 5: ПРОАКТИВНЫЕ ДЕЙСТВИЯ")
    print("-" * 70)
    
    def test_proactive_engine():
        """Проверка проактивного движка"""
        resp = requests.get(f'{tester.base_url}/api/proactive/status', timeout=5)
        status = resp.json()
        stats = status.get('stats', {})
        tester.log(f"Predictions: {stats.get('total_predictions', 0)}, Executed: {stats.get('executed_actions', 0)}")
        return resp.status_code == 200
    
    def test_proactive_prediction():
        """Запуск предсказания"""
        resp = requests.post(f'{tester.base_url}/api/proactive/predict', timeout=30)
        result = resp.json()
        if result.get('status') == 'completed':
            tester.log(f"Predictions: {result.get('predictions', 0)}, Executed: {len(result.get('actions_executed', []))}")
            return True
        return False
    
    tester.test_step("5.1 Proactive Engine активен", test_proactive_engine)
    tester.test_step("5.2 Создание предсказаний", test_proactive_prediction)
    
    # ========== ЭТАП 6: ИНТЕГРАЦИЯ И КОНТЕКСТ ==========
    print("\n🔗 ЭТАП 6: ИНТЕГРАЦИЯ И КОНТЕКСТ")
    print("-" * 70)
    
    def test_context_awareness():
        """Проверка понимания контекста"""
        # Создаем сессию
        resp1 = requests.post(
            f'{tester.base_url}/api/autonomous',
            data={'message': 'Create test', 'auto_execute': 'false'},
            timeout=30
        )
        session_id = resp1.json().get('session_id')
        
        # Запрашиваем контекст
        resp2 = requests.post(
            f'{tester.base_url}/api/autonomous',
            data={'message': 'What did you do?', 'session_id': session_id, 'auto_execute': 'false'},
            timeout=30
        )
        result = resp2.json()
        tester.log(f"Context response length: {len(result.get('response', ''))}")
        return len(result.get('response', '')) > 0
    
    def test_adaptive_learning():
        """Проверка адаптивного обучения"""
        resp = requests.get(f'{tester.base_url}/api/learning/adaptive', timeout=5)
        insights = resp.json()
        tester.log(f"Patterns learned: {insights.get('total_patterns', 0)}")
        return resp.status_code == 200
    
    tester.test_step("6.1 Понимание контекста", test_context_awareness)
    tester.test_step("6.2 Адаптивное обучение", test_adaptive_learning)
    
    # ========== ЭТАП 7: ПРОИЗВОДИТЕЛЬНОСТЬ ==========
    print("\n⚡ ЭТАП 7: ПРОИЗВОДИТЕЛЬНОСТЬ")
    print("-" * 70)
    
    def test_response_time():
        """Проверка времени отклика"""
        start = time.time()
        resp = requests.get(f'{tester.base_url}/api/status', timeout=5)
        duration = (time.time() - start) * 1000
        tester.log(f"Response time: {duration:.0f}ms")
        return duration < 1000  # < 1 секунды
    
    def test_concurrent_requests():
        """Проверка параллельных запросов"""
        import concurrent.futures
        
        def make_request():
            resp = requests.get(f'{tester.base_url}/api/status', timeout=5)
            return resp.status_code == 200
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        success_count = sum(results)
        tester.log(f"Concurrent requests: {success_count}/5 successful")
        return success_count == 5
    
    tester.test_step("7.1 Время отклика", test_response_time)
    tester.test_step("7.2 Параллельные запросы", test_concurrent_requests)
    
    # ========== ИТОГОВАЯ СВОДКА ==========
    tester.print_summary()
    
    # Сохранение результатов
    with open('test-results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_duration': time.time() - tester.start_time,
            'results': tester.test_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Результаты сохранены в test-results.json")
    
    # Возвращаем код выхода
    failed = len([r for r in tester.test_results if r["status"] != "PASS"])
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
