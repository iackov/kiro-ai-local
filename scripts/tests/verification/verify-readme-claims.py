"""
Проверка всех заявленных возможностей из README.md
Комплексный тест системы
"""
import requests
import time
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:9000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")

def print_test(name: str):
    print(f"{Colors.BLUE}🔍 {name}{Colors.RESET}")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.RESET}")


class SystemVerifier:
    """Проверка заявленных возможностей системы"""
    
    def __init__(self):
        self.results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }
        self.tests = []
    
    def test(self, name: str, func) -> bool:
        """Выполнить тест"""
        print_test(name)
        try:
            result = func()
            if result:
                self.results["passed"] += 1
                self.tests.append((name, "PASS", None))
                return True
            else:
                self.results["failed"] += 1
                self.tests.append((name, "FAIL", "Test returned False"))
                return False
        except Exception as e:
            self.results["failed"] += 1
            self.tests.append((name, "FAIL", str(e)))
            print_error(f"Error: {e}")
            return False
    
    def verify_all(self):
        """Проверить все заявленные возможности"""
        
        print_header("🚀 ПРОВЕРКА ЗАЯВЛЕННЫХ ВОЗМОЖНОСТЕЙ ИЗ README")
        
        # 1. Проверка сервисов
        print_header("📦 1. ПРОВЕРКА СЕРВИСОВ")
        self.test("Web UI (port 9000)", self.check_web_ui)
        self.test("RAG API (port 9001)", self.check_rag_api)
        self.test("Arch Engine (port 9004)", self.check_arch_engine)
        
        # 2. Проверка 6 уровней автономности
        print_header("🎓 2. ПРОВЕРКА 6 УРОВНЕЙ АВТОНОМНОСТИ")
        self.test("Level 1: Basic RAG", self.check_level1_rag)
        self.test("Level 2: Multi-Service Orchestration", self.check_level2_orchestration)
        self.test("Level 3: Architecture Engine", self.check_level3_arch)
        self.test("Level 4: Self-Monitoring", self.check_level4_monitoring)
        self.test("Level 5: Adaptive Learning", self.check_level5_learning)
        self.test("Level 6: Auto-Healing", self.check_level6_healing)
        
        # 3. Проверка Tree-of-Thought
        print_header("🌳 3. ПРОВЕРКА TREE-OF-THOUGHT ENGINE")
        self.test("Tree-of-Thought Status", self.check_tot_status)
        self.test("Tree-of-Thought Solve", self.check_tot_solve)
        self.test("Tree-of-Thought Context", self.check_tot_context)
        
        # 4. Проверка Self-Modification
        print_header("🔧 4. ПРОВЕРКА SELF-MODIFICATION ENGINE")
        self.test("Self-Modification Status", self.check_selfmod_status)
        self.test("Self-Modification Safety", self.check_selfmod_safety)
        
        # 5. Проверка Autonomous Optimizer
        print_header("🤖 5. ПРОВЕРКА AUTONOMOUS OPTIMIZER")
        self.test("Autonomous Optimizer Status", self.check_optimizer_status)
        self.test("Autonomous Analysis", self.check_optimizer_analysis)
        
        # 6. Проверка Proactive Engine
        print_header("🔮 6. ПРОВЕРКА PROACTIVE ENGINE")
        self.test("Proactive Engine Status", self.check_proactive_status)
        self.test("Proactive Predictions", self.check_proactive_predictions)
        
        # 7. Проверка Knowledge Store
        print_header("📚 7. ПРОВЕРКА KNOWLEDGE STORE")
        self.test("Knowledge Store Stats", self.check_knowledge_stats)
        self.test("Knowledge Store Executions", self.check_knowledge_executions)
        
        # 8. Проверка метрик
        print_header("📊 8. ПРОВЕРКА МЕТРИК И МОНИТОРИНГА")
        self.test("Production Metrics", self.check_production_metrics)
        self.test("Health Score", self.check_health_score)
        self.test("Circuit Breakers", self.check_circuit_breakers)
        
        # 9. Проверка автономного выполнения
        print_header("⚡ 9. ПРОВЕРКА АВТОНОМНОГО ВЫПОЛНЕНИЯ")
        self.test("Autonomous Interface", self.check_autonomous_interface)
        self.test("Task Execution", self.check_task_execution)
        
        # Итоги
        self.print_summary()
    
    # === Проверка сервисов ===
    
    def check_web_ui(self) -> bool:
        """Проверка Web UI"""
        try:
            resp = requests.get(f"{BASE_URL}/api/status", timeout=5)
            if resp.status_code == 200:
                print_success("Web UI доступен")
                return True
        except:
            print_error("Web UI недоступен")
        return False
    
    def check_rag_api(self) -> bool:
        """Проверка RAG API"""
        try:
            resp = requests.get(f"{BASE_URL}/api/rag/stats", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                doc_count = data.get("total_documents", 0)
                print_success(f"RAG API работает ({doc_count} документов)")
                return True
        except:
            print_error("RAG API недоступен")
        return False
    
    def check_arch_engine(self) -> bool:
        """Проверка Architecture Engine"""
        try:
            resp = requests.get(f"{BASE_URL}/api/arch/history", timeout=5)
            if resp.status_code == 200:
                print_success("Architecture Engine работает")
                return True
        except:
            print_error("Architecture Engine недоступен")
        return False
    
    # === Проверка уровней автономности ===
    
    def check_level1_rag(self) -> bool:
        """Level 1: Basic RAG"""
        try:
            resp = requests.post(
                f"{BASE_URL}/api/rag/query",
                data={"query": "docker", "top_k": 3},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                docs = data.get("documents", [])
                print_success(f"RAG поиск работает (найдено {len(docs)} документов)")
                return len(docs) > 0
        except Exception as e:
            print_error(f"RAG поиск не работает: {e}")
        return False
    
    def check_level2_orchestration(self) -> bool:
        """Level 2: Multi-Service Orchestration"""
        try:
            resp = requests.post(
                f"{BASE_URL}/api/combined/query",
                data={"query": "docker compose", "top_k": 3},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                services = data.get("services_used", [])
                print_success(f"Оркестрация работает (использовано {len(services)} сервисов)")
                return len(services) > 0
        except Exception as e:
            print_error(f"Оркестрация не работает: {e}")
        return False
    
    def check_level3_arch(self) -> bool:
        """Level 3: Architecture Engine"""
        try:
            resp = requests.post(
                f"{BASE_URL}/api/arch/propose",
                data={"prompt": "Add test service", "auto_apply": "false"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                safe = data.get("safe", False)
                print_success(f"Architecture Engine работает (safe={safe})")
                return True
        except Exception as e:
            print_error(f"Architecture Engine не работает: {e}")
        return False
    
    def check_level4_monitoring(self) -> bool:
        """Level 4: Self-Monitoring"""
        try:
            resp = requests.get(f"{BASE_URL}/api/metrics/insights", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                health = data.get("health_score", 0)
                print_success(f"Self-Monitoring работает (health={health})")
                return health > 0
        except Exception as e:
            print_error(f"Self-Monitoring не работает: {e}")
        return False
    
    def check_level5_learning(self) -> bool:
        """Level 5: Adaptive Learning"""
        try:
            resp = requests.get(f"{BASE_URL}/api/learning/adaptive", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                patterns = data.get("learned_patterns", 0)
                print_success(f"Adaptive Learning работает ({patterns} паттернов)")
                return True
        except Exception as e:
            print_error(f"Adaptive Learning не работает: {e}")
        return False
    
    def check_level6_healing(self) -> bool:
        """Level 6: Auto-Healing"""
        try:
            resp = requests.get(f"{BASE_URL}/api/auto/opportunities", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                opps = data.get("opportunities", [])
                print_success(f"Auto-Healing работает ({len(opps)} возможностей)")
                return True
        except Exception as e:
            print_error(f"Auto-Healing не работает: {e}")
        return False
    
    # === Проверка Tree-of-Thought ===
    
    def check_tot_status(self) -> bool:
        """Tree-of-Thought Status"""
        try:
            resp = requests.get(f"{BASE_URL}/api/tree-of-thought/status", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                trees = data.get("total_trees", 0)
                print_success(f"Tree-of-Thought работает ({trees} деревьев)")
                return True
        except Exception as e:
            print_error(f"Tree-of-Thought не работает: {e}")
        return False
    
    def check_tot_solve(self) -> bool:
        """Tree-of-Thought Solve"""
        try:
            resp = requests.post(
                f"{BASE_URL}/api/tree-of-thought/solve",
                data={"task": "Test task"},
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status")
                branches = data.get("stats", {}).get("total_branches_explored", 0)
                print_success(f"Tree-of-Thought решает задачи ({branches} веток)")
                return status == "completed"
        except Exception as e:
            print_error(f"Tree-of-Thought solve не работает: {e}")
        return False
    
    def check_tot_context(self) -> bool:
        """Tree-of-Thought Context"""
        try:
            # Сначала создаем дерево
            resp1 = requests.post(
                f"{BASE_URL}/api/tree-of-thought/solve",
                data={"task": "Test context"},
                timeout=15
            )
            if resp1.status_code == 200:
                tree_id = resp1.json().get("tree_id")
                
                # Получаем контекст
                resp2 = requests.get(
                    f"{BASE_URL}/api/tree-of-thought/context/{tree_id}",
                    timeout=5
                )
                if resp2.status_code == 200:
                    context = resp2.json().get("context", "")
                    print_success("Tree-of-Thought контекст работает")
                    return len(context) > 0
        except Exception as e:
            print_error(f"Tree-of-Thought context не работает: {e}")
        return False
    
    # === Проверка Self-Modification ===
    
    def check_selfmod_status(self) -> bool:
        """Self-Modification Status"""
        try:
            resp = requests.get(f"{BASE_URL}/api/self-modification/status", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                safe_zones = len(data.get("safe_zones", []))
                protected = len(data.get("protected_files", []))
                print_success(f"Self-Modification работает ({safe_zones} зон, {protected} защищено)")
                return safe_zones > 0
        except Exception as e:
            print_error(f"Self-Modification не работает: {e}")
        return False
    
    def check_selfmod_safety(self) -> bool:
        """Self-Modification Safety"""
        try:
            resp = requests.post(
                f"{BASE_URL}/api/self-modification/propose",
                data={
                    "file_path": "services/web-ui/main.py",
                    "modification_type": "optimize",
                    "description": "Test modification"
                },
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                approved = data.get("approved", False)
                # Должно быть отклонено (main.py защищен)
                if not approved:
                    print_success("Self-Modification защита работает")
                    return True
                else:
                    print_warning("Self-Modification одобрил изменение защищенного файла")
                    return False
        except Exception as e:
            print_error(f"Self-Modification safety не работает: {e}")
        return False
    
    # === Проверка Autonomous Optimizer ===
    
    def check_optimizer_status(self) -> bool:
        """Autonomous Optimizer Status"""
        try:
            resp = requests.get(f"{BASE_URL}/api/autonomous/status", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                is_active = data.get("is_active", False)
                print_success(f"Autonomous Optimizer работает (active={is_active})")
                return is_active
        except Exception as e:
            print_error(f"Autonomous Optimizer не работает: {e}")
        return False
    
    def check_optimizer_analysis(self) -> bool:
        """Autonomous Analysis"""
        try:
            resp = requests.post(f"{BASE_URL}/api/autonomous/analyze", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status")
                print_success(f"Autonomous Analysis работает (status={status})")
                return status == "completed"
        except Exception as e:
            print_error(f"Autonomous Analysis не работает: {e}")
        return False
    
    # === Проверка Proactive Engine ===
    
    def check_proactive_status(self) -> bool:
        """Proactive Engine Status"""
        try:
            resp = requests.get(f"{BASE_URL}/api/proactive/status", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                stats = data.get("stats", {})
                predictions = stats.get("total_predictions", 0)
                print_success(f"Proactive Engine работает ({predictions} предсказаний)")
                return True
        except Exception as e:
            print_error(f"Proactive Engine не работает: {e}")
        return False
    
    def check_proactive_predictions(self) -> bool:
        """Proactive Predictions"""
        try:
            resp = requests.post(f"{BASE_URL}/api/proactive/predict", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status")
                predictions = data.get("predictions", 0)
                print_success(f"Proactive Predictions работает ({predictions} предсказаний)")
                return status == "completed"
        except Exception as e:
            print_error(f"Proactive Predictions не работает: {e}")
        return False
    
    # === Проверка Knowledge Store ===
    
    def check_knowledge_stats(self) -> bool:
        """Knowledge Store Stats"""
        try:
            resp = requests.get(f"{BASE_URL}/api/knowledge/stats", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                stored = data.get("stored_executions", 0)
                print_success(f"Knowledge Store работает ({stored} выполнений)")
                return True
        except Exception as e:
            print_error(f"Knowledge Store не работает: {e}")
        return False
    
    def check_knowledge_executions(self) -> bool:
        """Knowledge Store Executions"""
        try:
            resp = requests.get(f"{BASE_URL}/api/knowledge/executions", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                total = data.get("total", 0)
                print_success(f"Knowledge Store executions работает ({total} записей)")
                return True
        except Exception as e:
            print_error(f"Knowledge Store executions не работает: {e}")
        return False
    
    # === Проверка метрик ===
    
    def check_production_metrics(self) -> bool:
        """Production Metrics"""
        try:
            resp = requests.get(f"{BASE_URL}/api/production/metrics", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                health = data.get("health", {}).get("score", 0)
                print_success(f"Production Metrics работает (health={health})")
                return health > 0
        except Exception as e:
            print_error(f"Production Metrics не работает: {e}")
        return False
    
    def check_health_score(self) -> bool:
        """Health Score"""
        try:
            resp = requests.get(f"{BASE_URL}/api/metrics/health", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                score = data.get("health_score", 0)
                status = data.get("status", "unknown")
                print_success(f"Health Score: {score}/100 ({status})")
                return score > 50
        except Exception as e:
            print_error(f"Health Score не работает: {e}")
        return False
    
    def check_circuit_breakers(self) -> bool:
        """Circuit Breakers"""
        try:
            resp = requests.get(f"{BASE_URL}/api/resilience/circuit-breakers", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                all_healthy = data.get("all_healthy", False)
                print_success(f"Circuit Breakers работают (all_healthy={all_healthy})")
                return True
        except Exception as e:
            print_error(f"Circuit Breakers не работают: {e}")
        return False
    
    # === Проверка автономного выполнения ===
    
    def check_autonomous_interface(self) -> bool:
        """Autonomous Interface"""
        try:
            resp = requests.post(
                f"{BASE_URL}/api/autonomous",
                data={
                    "message": "Test autonomous execution",
                    "auto_execute": "false"
                },
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                response = data.get("response", "")
                print_success("Autonomous Interface работает")
                return len(response) > 0
        except Exception as e:
            print_error(f"Autonomous Interface не работает: {e}")
        return False
    
    def check_task_execution(self) -> bool:
        """Task Execution"""
        try:
            resp = requests.post(
                f"{BASE_URL}/api/execute",
                data={"task": "Check system health"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status")
                print_success(f"Task Execution работает (status={status})")
                return status == "completed"
        except Exception as e:
            print_error(f"Task Execution не работает: {e}")
        return False
    
    def print_summary(self):
        """Вывести итоги"""
        print_header("📊 ИТОГИ ПРОВЕРКИ")
        
        total = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.BOLD}Всего тестов:{Colors.RESET} {total}")
        print(f"{Colors.GREEN}✅ Пройдено:{Colors.RESET} {self.results['passed']}")
        print(f"{Colors.RED}❌ Провалено:{Colors.RESET} {self.results['failed']}")
        print(f"{Colors.YELLOW}⚠️  Предупреждений:{Colors.RESET} {self.results['warnings']}")
        print(f"\n{Colors.BOLD}Success Rate:{Colors.RESET} {success_rate:.1f}%")
        
        # Детальный отчет
        if self.results["failed"] > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}Провалившиеся тесты:{Colors.RESET}")
            for name, status, error in self.tests:
                if status == "FAIL":
                    print(f"  {Colors.RED}❌ {name}{Colors.RESET}")
                    if error:
                        print(f"     {Colors.YELLOW}{error}{Colors.RESET}")
        
        # Финальная оценка
        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
        if success_rate >= 90:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ОТЛИЧНО! Система работает как заявлено!{Colors.RESET}")
        elif success_rate >= 70:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  ХОРОШО! Большинство функций работает{Colors.RESET}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ ТРЕБУЕТСЯ ВНИМАНИЕ! Много проблем{Colors.RESET}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")


def main():
    """Главная функция"""
    verifier = SystemVerifier()
    verifier.verify_all()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Прервано пользователем{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Критическая ошибка: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
