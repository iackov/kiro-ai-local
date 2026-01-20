#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск всех тестов системы
Организованный тестовый раннер с отчетностью
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Установка кодировки для Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Добавляем путь к тестам
TESTS_DIR = Path(__file__).parent
sys.path.insert(0, str(TESTS_DIR))

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestRunner:
    """Запускает и отслеживает тесты"""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        
    def run_test(self, name: str, path: str) -> Tuple[bool, float, str]:
        """Запустить один тест"""
        print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}TEST: {name}{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")
        
        start = time.time()
        try:
            result = subprocess.run(
                [sys.executable, path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=120
            )
            duration = time.time() - start
            
            # Выводим результат
            try:
                print(result.stdout)
            except UnicodeEncodeError:
                print(result.stdout.encode('ascii', 'replace').decode('ascii'))
            
            if result.stderr:
                print(f"{Colors.YELLOW}STDERR:{Colors.RESET}")
                try:
                    print(result.stderr)
                except UnicodeEncodeError:
                    print(result.stderr.encode('ascii', 'replace').decode('ascii'))
            
            success = result.returncode == 0
            return success, duration, result.stdout
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start
            print(f"{Colors.RED}[X] TIMEOUT: Test exceeded 120 seconds{Colors.RESET}")
            return False, duration, "Timeout"
        except Exception as e:
            duration = time.time() - start
            print(f"{Colors.RED}[X] ERROR: {e}{Colors.RESET}")
            return False, duration, str(e)
    
    def run_category(self, category: str, tests: List[Tuple[str, str]]):
        """Запустить категорию тестов"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}CATEGORY: {category.upper()}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
        
        category_results = []
        
        for name, path in tests:
            if not os.path.exists(path):
                print(f"{Colors.YELLOW}[!] Skipped: {name} (file not found){Colors.RESET}")
                continue
                
            success, duration, output = self.run_test(name, path)
            
            result = {
                "category": category,
                "name": name,
                "success": success,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(result)
            category_results.append(result)
            
            # Статус
            if success:
                print(f"\n{Colors.GREEN}[+] PASS: {name} ({duration:.2f}s){Colors.RESET}")
            else:
                print(f"\n{Colors.RED}[X] FAIL: {name} ({duration:.2f}s){Colors.RESET}")
        
        # Итоги категории
        passed = sum(1 for r in category_results if r["success"])
        total = len(category_results)
        
        print(f"\n{Colors.BOLD}Summary for {category}:{Colors.RESET}")
        print(f"  Passed: {passed}/{total}")
        print(f"  Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%")
    
    def print_summary(self):
        """Вывести итоговую сводку"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}FINAL SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed
        total_time = time.time() - self.start_time
        
        print(f"{Colors.BOLD}Total tests:{Colors.RESET} {total}")
        print(f"{Colors.GREEN}[+] Passed:{Colors.RESET} {passed}")
        print(f"{Colors.RED}[X] Failed:{Colors.RESET} {failed}")
        print(f"{Colors.CYAN}[T] Total time:{Colors.RESET} {total_time:.2f}s")
        print(f"{Colors.BOLD}Success Rate:{Colors.RESET} {(passed/total*100) if total > 0 else 0:.1f}%")
        
        # По категориям
        categories = {}
        for r in self.results:
            cat = r["category"]
            if cat not in categories:
                categories[cat] = {"passed": 0, "total": 0}
            categories[cat]["total"] += 1
            if r["success"]:
                categories[cat]["passed"] += 1
        
        print(f"\n{Colors.BOLD}By category:{Colors.RESET}")
        for cat, stats in categories.items():
            rate = (stats["passed"]/stats["total"]*100) if stats["total"] > 0 else 0
            color = Colors.GREEN if rate >= 80 else Colors.YELLOW if rate >= 50 else Colors.RED
            print(f"  {color}{cat}:{Colors.RESET} {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        # Проваленные тесты
        if failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}Failed tests:{Colors.RESET}")
            for r in self.results:
                if not r["success"]:
                    print(f"  {Colors.RED}[X] {r['category']}/{r['name']}{Colors.RESET}")
        
        # Финальная оценка
        success_rate = (passed/total*100) if total > 0 else 0
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        if success_rate >= 90:
            print(f"{Colors.GREEN}{Colors.BOLD}[+] EXCELLENT! All systems operational!{Colors.RESET}")
        elif success_rate >= 70:
            print(f"{Colors.YELLOW}{Colors.BOLD}[!] GOOD! Most tests passing{Colors.RESET}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}[X] ATTENTION REQUIRED! Many failures{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")
        
        # Сохранение результатов
        self.save_results()
    
    def save_results(self):
        """Сохранить результаты в JSON"""
        output = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": time.time() - self.start_time,
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r["success"]),
                "failed": sum(1 for r in self.results if not r["success"]),
                "success_rate": (sum(1 for r in self.results if r["success"]) / len(self.results) * 100) if self.results else 0
            },
            "results": self.results
        }
        
        output_file = TESTS_DIR / "test-results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"{Colors.CYAN}[S] Results saved: {output_file}{Colors.RESET}")

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Запуск тестов AI Autonomous System")
    parser.add_argument("--unit", action="store_true", help="Только юнит-тесты")
    parser.add_argument("--integration", action="store_true", help="Только интеграционные тесты")
    parser.add_argument("--verification", action="store_true", help="Только проверка возможностей")
    parser.add_argument("--quick", action="store_true", help="Быстрые тесты (без длительных)")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    runner.start_time = time.time()
    
    # Определяем тесты
    unit_tests = [
        ("Tree-of-Thought Engine", str(TESTS_DIR / "unit" / "test-tree-of-thought.py")),
        ("Self-Modification Engine", str(TESTS_DIR / "unit" / "test-self-modification.py")),
        ("Autonomous Optimizer", str(TESTS_DIR / "unit" / "test-autonomous-optimizer.py")),
        ("Proactive Engine", str(TESTS_DIR / "unit" / "test-proactive-engine.py")),
        ("Knowledge Store", str(TESTS_DIR / "unit" / "test-knowledge-store.py")),
    ]
    
    integration_tests = [
        ("Task Execution", str(TESTS_DIR / "integration" / "test-execution.py")),
        ("System Improvements", str(TESTS_DIR / "integration" / "test-improvements.py")),
        ("Full System", str(TESTS_DIR / "integration" / "test-full-system.py")),
    ]
    
    verification_tests = [
        ("README Claims Verification", str(TESTS_DIR / "verification" / "verify-readme-claims.py")),
    ]
    
    # Запускаем выбранные категории
    if args.unit or not (args.integration or args.verification):
        runner.run_category("Unit Tests", unit_tests)
    
    if args.integration or not (args.unit or args.verification):
        runner.run_category("Integration Tests", integration_tests)
    
    if args.verification or not (args.unit or args.integration):
        runner.run_category("Verification Tests", verification_tests)
    
    # Итоги
    runner.print_summary()
    
    # Возвращаем код выхода
    failed = sum(1 for r in runner.results if not r["success"])
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!] Interrupted by user{Colors.RESET}")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}[X] Critical error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        exit(1)
