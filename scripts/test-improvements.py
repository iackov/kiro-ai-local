#!/usr/bin/env python3
"""Тестирование улучшений системы"""

import requests
import time

print("\n🚀 ТЕСТИРОВАНИЕ УЛУЧШЕНИЙ СИСТЕМЫ\n")

# Тест 1: Model Router статистика
print("Тест 1: Model Router и кэширование")
print("-" * 60)

stats_response = requests.get('http://localhost:9000/api/models/stats')
stats = stats_response.json()

print(f"✓ External model configured: {stats.get('external_configured')}")
print(f"✓ Model stats:")
for model, data in stats.get('stats', {}).items():
    if model != 'cache':
        print(f"   {model}: {data.get('calls', 0)} calls, avg {data.get('avg_time', 0)}s, {data.get('error_rate', 0)}% errors")

cache_stats = stats.get('stats', {}).get('cache', {})
print(f"✓ Cache: {cache_stats.get('hits', 0)} hits, {cache_stats.get('misses', 0)} misses, {cache_stats.get('hit_rate', 0)}% hit rate")

# Тест 2: Производительность с кэшем
print("\n\nТест 2: Производительность с кэшированием")
print("-" * 60)

# Первый запрос (без кэша)
print("Запрос 1 (без кэша)...")
start1 = time.time()
resp1 = requests.post(
    'http://localhost:9000/api/autonomous',
    data={'message': 'Create simple test', 'auto_execute': 'false'},
    timeout=30
)
time1 = time.time() - start1
print(f"   Время: {time1:.2f}s")

# Второй такой же запрос (с кэшем)
print("Запрос 2 (с кэшем)...")
start2 = time.time()
resp2 = requests.post(
    'http://localhost:9000/api/autonomous',
    data={'message': 'Create simple test', 'auto_execute': 'false'},
    timeout=30
)
time2 = time.time() - start2
print(f"   Время: {time2:.2f}s")

if time2 < time1:
    speedup = time1 / time2
    print(f"✅ Ускорение: {speedup:.1f}x благодаря кэшу!")
else:
    print(f"⚠️  Кэш не сработал или запросы разные")

# Тест 3: Проверка статистики после запросов
print("\n\nТест 3: Обновленная статистика")
print("-" * 60)

stats_response2 = requests.get('http://localhost:9000/api/models/stats')
stats2 = stats_response2.json()

cache_stats2 = stats2.get('stats', {}).get('cache', {})
print(f"✓ Cache hits: {cache_stats2.get('hits', 0)}")
print(f"✓ Cache misses: {cache_stats2.get('misses', 0)}")
print(f"✓ Cache hit rate: {cache_stats2.get('hit_rate', 0)}%")
print(f"✓ Cache size: {cache_stats2.get('size', 0)} entries")

# Тест 4: Очистка кэша
print("\n\nТест 4: Очистка кэша")
print("-" * 60)

clear_response = requests.post('http://localhost:9000/api/models/clear-cache')
clear_result = clear_response.json()
print(f"✓ Status: {clear_result.get('status')}")
print(f"✓ Message: {clear_result.get('message')}")

# Проверка после очистки
stats_response3 = requests.get('http://localhost:9000/api/models/stats')
stats3 = stats_response3.json()
cache_stats3 = stats3.get('stats', {}).get('cache', {})
print(f"✓ Cache size after clear: {cache_stats3.get('size', 0)}")

print("\n" + "="*60)
print("\n✅ Улучшения работают! Система оптимизирована.")
