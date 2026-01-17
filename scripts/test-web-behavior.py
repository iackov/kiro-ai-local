#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Эмуляция поведения веб-интерфейса"""

import requests
import json

print("\n🌐 ЭМУЛЯЦИЯ ВЕБ-ИНТЕРФЕЙСА\n")

# Эмулируем точно то же, что делает JavaScript в chat.html
print("Отправка запроса как в веб-интерфейсе...")
print("-" * 60)

# Создаем FormData как в JavaScript
form_data = {
    'message': 'Создай тестовый скрипт на Python и исполни его. Выведи результат его работы сюда - в этот чат.',
    'auto_execute': 'true'  # Переключатель включен
}

print(f"📤 Отправляем:")
print(f"   message: {form_data['message'][:50]}...")
print(f"   auto_execute: {form_data['auto_execute']}")
print()

response = requests.post(
    'http://localhost:9000/api/autonomous',
    data=form_data,
    timeout=120
)

result = response.json()

print(f"📥 Получен ответ:")
print(f"   Status: {response.status_code}")
print(f"   Intent: {result.get('intent')}")
print(f"   Response: {result.get('response')[:100]}...")
print()

# Проверяем execution_plan
if result.get('execution_plan'):
    plan = result['execution_plan']
    print(f"📋 План выполнения:")
    print(f"   Task ID: {plan.get('task_id')}")
    print(f"   Steps: {len(plan.get('steps', []))}")
    print(f"   Requires approval: {plan.get('requires_approval')}")
    print(f"   Decision: {plan.get('autonomous_decision', {}).get('action')}")
    print()
    
    print(f"   Шаги:")
    for i, step in enumerate(plan.get('steps', []), 1):
        print(f"      {i}. {step}")
    print()

# Проверяем task_result
if result.get('task_result'):
    print(f"✅ ЗАДАЧА ВЫПОЛНЕНА!")
    task = result['task_result']
    summary = task.get('summary', {})
    print(f"   Success rate: {summary.get('success_rate')}%")
    print(f"   Status: {summary.get('status')}")
    print(f"   Steps: {summary.get('successful')}/{summary.get('total_steps')}")
    print()
    
    print(f"   Результаты шагов:")
    for step in task.get('result', []):
        status_icon = '✅' if step['status'] in ['success', 'completed'] else '❌'
        print(f"      {status_icon} {step['step']}")
        if step.get('result'):
            print(f"         → {step['result']}")
else:
    print(f"❌ ЗАДАЧА НЕ ВЫПОЛНЕНА")
    print(f"   Причина: План создан, но не выполнен")
    print(f"   Требуется: Set auto_execute=true to run")

print("\n" + "="*60)

# Дополнительная диагностика
print("\n🔍 ДИАГНОСТИКА:")
print(f"   capabilities.autonomous: {result.get('capabilities', {}).get('autonomous')}")
print(f"   execution_plan exists: {result.get('execution_plan') is not None}")
print(f"   task_result exists: {result.get('task_result') is not None}")

if result.get('execution_plan') and not result.get('task_result'):
    print(f"\n⚠️  ПРОБЛЕМА: План создан, но задача не выполнена!")
    print(f"   Возможные причины:")
    print(f"   1. autonomous_decision.action == 'require_approval'")
    print(f"   2. auto_execute_bool не парсится правильно")
    print(f"   3. Логика should_execute блокирует выполнение")
