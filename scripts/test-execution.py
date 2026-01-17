#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тестирование выполнения задач"""

import requests
import json

print("\n🧪 ТЕСТИРОВАНИЕ ВЫПОЛНЕНИЯ ЗАДАЧ\n")

# Тест 1: С auto_execute=true
print("Тест 1: Create code with auto_execute=true")
print("-" * 60)

response = requests.post(
    'http://localhost:9000/api/autonomous',
    data={
        'message': 'Create a simple hello world program. Save to playground/hello.py',
        'auto_execute': 'true'
    },
    timeout=120
)

result = response.json()

print(f"✓ Intent: {result.get('intent')}")
print(f"✓ Auto-execute capability: {result.get('capabilities', {}).get('autonomous')}")

if result.get('execution_plan'):
    plan = result['execution_plan']
    decision = plan.get('autonomous_decision', {})
    print(f"✓ Decision: {decision.get('action')}")
    print(f"✓ Requires approval: {plan.get('requires_approval')}")
    print(f"✓ Steps planned: {len(plan.get('steps', []))}")
    print(f"✓ Safety level: {plan.get('safety_level')}")

print(f"\n{'✅ ЗАДАЧА ВЫПОЛНЕНА!' if result.get('task_result') else '❌ ЗАДАЧА НЕ ВЫПОЛНЕНА'}")

if result.get('task_result'):
    summary = result['task_result']['summary']
    print(f"  Success rate: {summary.get('success_rate')}%")
    print(f"  Steps: {summary.get('successful')}/{summary.get('total_steps')}")
    print(f"\n  Выполненные шаги:")
    for step in result['task_result']['result']:
        status_icon = '✅' if step['status'] in ['success', 'completed'] else '❌'
        print(f"    {status_icon} {step['step']}")
else:
    print(f"  Response: {result.get('response')}")

print("\n" + "="*60 + "\n")

# Проверка созданного файла
print("📁 Проверка созданного файла:")
import subprocess
check = subprocess.run(
    ['docker', 'exec', 'ai-web-ui', 'ls', '-la', '/app/playground/'],
    capture_output=True,
    text=True
)
if 'hello.py' in check.stdout:
    print("✅ Файл hello.py создан в контейнере!")
    # Показать содержимое
    content = subprocess.run(
        ['docker', 'exec', 'ai-web-ui', 'cat', '/app/playground/hello.py'],
        capture_output=True,
        text=True
    )
    print("\nСодержимое:")
    print(content.stdout)
else:
    print("❌ Файл не найден")
    print(check.stdout)

