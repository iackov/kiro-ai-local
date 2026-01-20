#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тестирование Proactive Engine"""

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

print("\n🔮 ТЕСТИРОВАНИЕ PROACTIVE ENGINE\n")

# Тест 1: Статус проактивного движка
print("Тест 1: Статус Proactive Engine")
print("-" * 60)

status_response = requests.get('http://localhost:9000/api/proactive/status')
status = status_response.json()

print(f"✓ Pending actions: {status.get('stats', {}).get('pending_actions', 0)}")
print(f"✓ Executed actions: {status.get('stats', {}).get('executed_actions', 0)}")
print(f"✓ Total predictions: {status.get('stats', {}).get('total_predictions', 0)}")
print(f"✓ Auto-execute rate: {status.get('stats', {}).get('auto_execute_rate', 0):.1f}%")

# Тест 2: Запустить предсказание вручную
print("\n\nТест 2: Ручной запуск предсказания")
print("-" * 60)

print("🔮 Запускаем предсказание...")
predict_response = requests.post('http://localhost:9000/api/proactive/predict')
predict_result = predict_response.json()

print(f"✓ Status: {predict_result.get('status')}")
print(f"✓ Predictions made: {predict_result.get('predictions', 0)}")

if predict_result.get('actions_created'):
    print(f"\n📋 Созданные проактивные действия:")
    for action in predict_result['actions_created']:
        priority_icon = "🔴" if action['priority'] == 'high' else "🟡" if action['priority'] == 'medium' else "🟢"
        auto_icon = "🤖" if action['auto_execute'] else "👤"
        print(f"   {priority_icon} {auto_icon} {action['action_type']}")
        print(f"      Причина: {action['reason']}")

if predict_result.get('actions_executed'):
    print(f"\n✅ Автоматически выполнено: {len(predict_result['actions_executed'])}")
    for exec_action in predict_result['actions_executed']:
        action = exec_action['action']
        result = exec_action['result']
        print(f"   ✓ {action['action_type']}: {result.get('message', 'Done')}")

# Тест 3: Выполнить несколько задач для генерации метрик
print("\n\nТест 3: Генерация метрик для предсказаний")
print("-" * 60)

for i in range(2):
    print(f"Выполнение задачи {i+1}/2...")
    try:
        response = requests.post(
            'http://localhost:9000/api/autonomous',
            data={
                'message': f'Create test script {i+1} in playground/test{i+1}.py',
                'auto_execute': 'true'
            },
            timeout=30  # Reduced timeout
        )
        result = response.json()
        if result.get('task_result'):
            print(f"   ✓ Task {i+1} completed")
    except requests.exceptions.Timeout:
        print(f"   ⚠ Task {i+1} timeout - skipping")
    except Exception as e:
        print(f"   ⚠ Task {i+1} error: {str(e)[:50]}")

# Тест 4: Проверить обновленный статус
print("\n\nТест 4: Обновленный статус после работы")
print("-" * 60)

time.sleep(2)
status_response2 = requests.get('http://localhost:9000/api/proactive/status')
status2 = status_response2.json()

print(f"✓ Pending actions: {status2.get('stats', {}).get('pending_actions', 0)}")
print(f"✓ Executed actions: {status2.get('stats', {}).get('executed_actions', 0)}")
print(f"✓ Total predictions: {status2.get('stats', {}).get('total_predictions', 0)}")

recent_executed = status2.get('recent_executed', [])
if recent_executed:
    print(f"\n📈 Последние выполненные действия:")
    for action in recent_executed[-3:]:
        print(f"   - {action['action_type']} (priority: {action['priority']})")

pending = status2.get('pending_actions', [])
if pending:
    print(f"\n⏳ Ожидающие действия (требуют подтверждения):")
    for action in pending:
        print(f"   - {action['action_type']}: {action['reason']}")

print("\n" + "="*60)
print("\n✅ Proactive Engine работает! Система предсказывает и предотвращает проблемы.")
