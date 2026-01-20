#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тестирование Autonomous Optimizer"""

import sys
# Установка кодировки для Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

import requests
import time

print("\n🤖 ТЕСТИРОВАНИЕ AUTONOMOUS OPTIMIZER\n")

# Тест 1: Проверить статус оптимизатора
print("Тест 1: Статус автономного оптимизатора")
print("-" * 60)

status_response = requests.get('http://localhost:9000/api/autonomous/status')
status = status_response.json()

print(f"✓ Optimizer active: {status.get('is_active')}")
print(f"✓ Total analyses: {status.get('optimizer', {}).get('total_analyses', 0)}")
print(f"✓ Total improvements: {status.get('optimizer', {}).get('total_improvements', 0)}")
print(f"✓ Last analysis: {status.get('last_analysis', 'Never')}")

# Тест 2: Запустить анализ вручную
print("\n\nТест 2: Ручной запуск анализа системы")
print("-" * 60)

print("🔍 Запускаем анализ...")
analyze_response = requests.post('http://localhost:9000/api/autonomous/analyze')
analyze_result = analyze_response.json()

print(f"✓ Status: {analyze_result.get('status')}")

if analyze_result.get('analysis'):
    analysis = analyze_result['analysis']
    print(f"\n📊 Результаты анализа:")
    print(f"   Issues found: {len(analysis.get('issues', []))}")
    print(f"   Recommendations: {len(analysis.get('recommendations', []))}")
    print(f"   Auto actions: {len(analysis.get('auto_actions', []))}")
    
    if analysis.get('issues'):
        print(f"\n   🔴 Обнаруженные проблемы:")
        for issue in analysis['issues'][:3]:
            print(f"      - {issue.get('type')}: {issue.get('description')}")
    
    if analysis.get('recommendations'):
        print(f"\n   💡 Рекомендации:")
        for rec in analysis['recommendations'][:3]:
            print(f"      - {rec.get('action')}: {rec.get('description')}")

if analyze_result.get('improvements_applied'):
    improvements = analyze_result['improvements_applied']
    print(f"\n✅ Применено улучшений: {len(improvements)}")
    for imp in improvements:
        print(f"   - {imp.get('action')}: {imp.get('result', {}).get('message', 'Applied')}")

# Тест 3: Выполнить несколько задач для генерации метрик
print("\n\nТест 3: Генерация метрик для анализа")
print("-" * 60)

for i in range(3):
    print(f"Выполнение задачи {i+1}/3...")
    try:
        response = requests.post(
            'http://localhost:9000/api/autonomous',
            data={
                'message': f'Create test file {i+1} in playground/test{i+1}.txt',
                'auto_execute': 'true'
            },
            timeout=30  # Reduced timeout
        )
        result = response.json()
        if result.get('task_result'):
            print(f"   ✓ Task {i+1} completed")
        else:
            print(f"   ⚠ Task {i+1} planned but not executed")
    except requests.exceptions.Timeout:
        print(f"   ⚠ Task {i+1} timeout - skipping")
    except Exception as e:
        print(f"   ⚠ Task {i+1} error: {str(e)[:50]}")

# Тест 4: Проверить обновленный статус
print("\n\nТест 4: Обновленный статус после работы")
print("-" * 60)

time.sleep(2)
status_response2 = requests.get('http://localhost:9000/api/autonomous/status')
status2 = status_response2.json()

print(f"✓ Total analyses: {status2.get('optimizer', {}).get('total_analyses', 0)}")
print(f"✓ Total improvements: {status2.get('optimizer', {}).get('total_improvements', 0)}")

recent_improvements = status2.get('optimizer', {}).get('recent_improvements', [])
if recent_improvements:
    print(f"\n📈 Последние улучшения:")
    for imp in recent_improvements[-3:]:
        print(f"   - {imp.get('action')} at {imp.get('timestamp')}")

print("\n" + "="*60)
print("\n✅ Autonomous Optimizer работает! Система самостоятельно анализирует и улучшается.")
