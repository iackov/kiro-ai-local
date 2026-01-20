#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Общие утилиты для тестирования
Используются всеми тестами для единообразия
"""

import sys
import requests
import time
from typing import Optional, Dict, Any, Callable
from datetime import datetime

# Установка кодировки для Windows
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        # Для старых версий Python
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class Colors:
    """ANSI цветовые коды для консоли"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

class TestResult:
    """Результат теста"""
    def __init__(self, name: str, success: bool, duration: float, message: str = ""):
        self.name = name
        self.success = success
        self.duration = duration
        self.message = message
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "success": self.success,
            "duration": self.duration,
            "message": self.message,
            "timestamp": self.timestamp
        }

class TestRunner:
    """Базовый класс для запуска тестов"""
    
    def __init__(self, name: str):
        self.name = name
        self.results = []
        self.start_time = None
    
    def start(self):
        """Начать тестирование"""
        self.start_time = time.time()
        print_header(f"🧪 {self.name}")
    
    def test(self, name: str, func: Callable) -> bool:
        """Выполнить тест"""
        print_test(name)
        start = time.time()
        
        try:
            result = func()
            duration = time.time() - start
            
            if result:
                self.results.append(TestResult(name, True, duration))
                print_success(f"{name} ({duration:.2f}s)")
                return True
            else:
                self.results.append(TestResult(name, False, duration, "Test returned False"))
                print_error(f"{name} ({duration:.2f}s)")
                return False
                
        except Exception as e:
            duration = time.time() - start
            self.results.append(TestResult(name, False, duration, str(e)))
            print_error(f"{name}: {e}")
            return False
    
    def finish(self):
        """Завершить тестирование"""
        total_time = time.time() - self.start_time
        passed = sum(1 for r in self.results if r.success)
        total = len(self.results)
        
        print_separator()
        print(f"\n{Colors.BOLD}Итоги:{Colors.RESET}")
        print(f"  Всего: {total}")
        print(f"  {Colors.GREEN}✅ Пройдено: {passed}{Colors.RESET}")
        print(f"  {Colors.RED}❌ Провалено: {total - passed}{Colors.RESET}")
        print(f"  ⏱️  Время: {total_time:.2f}s")
        print(f"  📊 Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%")
        
        return passed == total

# === Вывод в консоль ===

def print_header(text: str):
    """Вывести заголовок"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_section(text: str):
    """Вывести секцию"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'-'*70}{Colors.RESET}")

def print_test(name: str):
    """Вывести название теста"""
    print(f"\n{Colors.CYAN}🔍 {name}{Colors.RESET}")

def print_success(message: str):
    """Вывести успех"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    """Вывести ошибку"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str):
    """Вывести предупреждение"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message: str):
    """Вывести информацию"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

def print_separator():
    """Вывести разделитель"""
    print(f"\n{Colors.DIM}{'='*70}{Colors.RESET}")

# === Проверка сервисов ===

def check_service(url: str, timeout: int = 5) -> bool:
    """Проверить доступность сервиса"""
    try:
        resp = requests.get(url, timeout=timeout)
        return resp.status_code == 200
    except:
        return False

def wait_for_service(url: str, max_wait: int = 30, check_interval: int = 1) -> bool:
    """Ждать запуска сервиса"""
    start = time.time()
    while time.time() - start < max_wait:
        if check_service(url):
            return True
        time.sleep(check_interval)
    return False

def check_all_services(base_url: str = "http://localhost:9000") -> Dict[str, bool]:
    """Проверить все сервисы"""
    services = {
        "Web UI": f"{base_url}/api/status",
        "RAG API": f"{base_url}/api/rag/stats",
        "Arch Engine": f"{base_url}/api/arch/history",
    }
    
    results = {}
    for name, url in services.items():
        results[name] = check_service(url)
    
    return results

# === HTTP запросы ===

def safe_get(url: str, timeout: int = 5) -> Optional[Dict[str, Any]]:
    """Безопасный GET запрос"""
    try:
        resp = requests.get(url, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return None

def safe_post(url: str, data: Dict[str, Any] = None, json_data: Dict[str, Any] = None, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """Безопасный POST запрос"""
    try:
        if json_data:
            resp = requests.post(url, json=json_data, timeout=timeout)
        else:
            resp = requests.post(url, data=data, timeout=timeout)
        
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return None

# === Утилиты для тестов ===

def measure_time(func: Callable) -> tuple[Any, float]:
    """Измерить время выполнения функции"""
    start = time.time()
    result = func()
    duration = time.time() - start
    return result, duration

def retry(func: Callable, max_attempts: int = 3, delay: float = 1.0) -> Optional[Any]:
    """Повторить функцию при ошибке"""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(delay)
    return None

def compare_performance(func1: Callable, func2: Callable, name1: str = "Method 1", name2: str = "Method 2"):
    """Сравнить производительность двух функций"""
    result1, time1 = measure_time(func1)
    result2, time2 = measure_time(func2)
    
    print(f"\n{Colors.BOLD}Сравнение производительности:{Colors.RESET}")
    print(f"  {name1}: {time1:.3f}s")
    print(f"  {name2}: {time2:.3f}s")
    
    if time1 < time2:
        speedup = time2 / time1
        print(f"  {Colors.GREEN}✅ {name1} быстрее в {speedup:.2f}x{Colors.RESET}")
    elif time2 < time1:
        speedup = time1 / time2
        print(f"  {Colors.GREEN}✅ {name2} быстрее в {speedup:.2f}x{Colors.RESET}")
    else:
        print(f"  {Colors.YELLOW}⚖️  Одинаковая скорость{Colors.RESET}")
    
    return result1, result2, time1, time2

# === Константы ===

BASE_URL = "http://localhost:9000"
RAG_URL = "http://localhost:9001"
ARCH_URL = "http://localhost:9004"

DEFAULT_TIMEOUT = 10
LONG_TIMEOUT = 60
VERY_LONG_TIMEOUT = 120

# === Декораторы ===

def skip_if_service_down(service_url: str):
    """Пропустить тест если сервис недоступен"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not check_service(service_url):
                print_warning(f"Сервис {service_url} недоступен, тест пропущен")
                return False
            return func(*args, **kwargs)
        return wrapper
    return decorator

def timeout_test(seconds: int):
    """Ограничить время выполнения теста"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Тест превысил {seconds}s")
            
            # Для Windows используем другой подход
            import platform
            if platform.system() == 'Windows':
                # Просто выполняем без таймаута на Windows
                return func(*args, **kwargs)
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wrapper
    return decorator

# === Fixtures ===

class TestFixtures:
    """Общие фикстуры для тестов"""
    
    @staticmethod
    def setup_test_environment():
        """Подготовить окружение для тестов"""
        # Проверить доступность сервисов
        services = check_all_services()
        all_up = all(services.values())
        
        if not all_up:
            print_warning("Не все сервисы доступны:")
            for name, status in services.items():
                icon = "✅" if status else "❌"
                print(f"  {icon} {name}")
        
        return all_up
    
    @staticmethod
    def cleanup_test_data():
        """Очистить тестовые данные"""
        # Можно добавить очистку кэша, временных файлов и т.д.
        pass

# === Экспорт ===

__all__ = [
    'Colors',
    'TestResult',
    'TestRunner',
    'print_header',
    'print_section',
    'print_test',
    'print_success',
    'print_error',
    'print_warning',
    'print_info',
    'print_separator',
    'check_service',
    'wait_for_service',
    'check_all_services',
    'safe_get',
    'safe_post',
    'measure_time',
    'retry',
    'compare_performance',
    'BASE_URL',
    'RAG_URL',
    'ARCH_URL',
    'DEFAULT_TIMEOUT',
    'LONG_TIMEOUT',
    'VERY_LONG_TIMEOUT',
    'skip_if_service_down',
    'timeout_test',
    'TestFixtures',
]
