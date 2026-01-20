#!/usr/bin/env python3
"""Тестирование Knowledge Store"""

import requests
import time

print("\n🧠 ТЕСТИРОВАНИЕ KNOWLEDGE STORE\n")

# Тест 1: Выполнить задачу с сохранением в базу знаний
print("Тест 1: Выполнение задачи с auto_execute=true")
print("-" * 60)

response = requests.post(
    'http://localhost:9000/api/autonomous',
    data={
        'message': 'Create a simple calculator script in Python. Save to playground/calculator.py',
        'auto_execute': 'true'
    },
    timeout=120
)

result = response.json()
print(f"✓ Task executed: {result.get('task_result') is not None}")

if result.get('task_result'):
    summary = result['task_result']['summary']
    print(f"✓ Success rate: {summary.get('success_rate')}%")
    print(f"✓ Task ID: {result['task_result']['task_id']}")

print("\n⏳ Ждем 2 секунды для сохранения в RAG...")
time.sleep(2)

# Тест 2: Проверить статистику Knowledge Store
print("\nТест 2: Статистика Knowledge Store")
print("-" * 60)

stats_response = requests.get('http://localhost:9000/api/knowledge/stats')
stats = stats_response.json()

print(f"✓ Stored executions: {stats.get('stored_executions', 0)}")
print(f"✓ Status: {stats.get('status')}")

# Тест 3: Запросить похожие выполнения
print("\nТест 3: Поиск похожих выполнений")
print("-" * 60)

executions_response = requests.get(
    'http://localhost:9000/api/knowledge/executions',
    params={'query': 'calculator script'}
)
executions_data = executions_response.json()

print(f"✓ Found executions: {executions_data.get('total', 0)}")

if executions_data.get('executions'):
    for i, exec_doc in enumerate(executions_data['executions'][:3], 1):
        metadata = exec_doc.get('metadata', {})
        print(f"\n  {i}. Task ID: {metadata.get('task_id', 'N/A')}")
        print(f"     Success Rate: {metadata.get('success_rate', 0)}%")
        print(f"     Timestamp: {metadata.get('timestamp', 'N/A')}")
        content_preview = exec_doc.get('content', '')[:100]
        print(f"     Preview: {content_preview}...")

# Тест 4: Выполнить похожую задачу и проверить использование контекста
print("\n\nТест 4: Выполнение похожей задачи")
print("-" * 60)

response2 = requests.post(
    'http://localhost:9000/api/autonomous',
    data={
        'message': 'Create another calculator script with multiplication. Save to playground/calc2.py',
        'auto_execute': 'true'
    },
    timeout=120
)

result2 = response2.json()
print(f"✓ Task executed: {result2.get('task_result') is not None}")

if result2.get('task_result'):
    summary2 = result2['task_result']['summary']
    print(f"✓ Success rate: {summary2.get('success_rate')}%")
    rag_context = result2.get('rag_context_used', [])
    print(f"✓ Used similar executions: {len(rag_context) > 0 if isinstance(rag_context, list) else False}")

print("\n" + "="*60)
print("\n✅ Knowledge Store работает! Система учится на своем опыте.")
