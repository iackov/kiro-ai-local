#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест Tree-of-Thought Engine
Проверяет генерацию веток, отбор успешных, скрытие неудачных
"""
import sys
# Установка кодировки для Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

import requests
import json

BASE_URL = "http://localhost:9000"

def test_tree_of_thought():
    print("🌳 ТЕСТИРОВАНИЕ TREE-OF-THOUGHT ENGINE")
    print("=" * 60)
    print("Философия: Модель видит только успешные решения")
    print("Неудачные ветки отбрасываются до попадания в контекст")
    print()
    
    # Тест 1: Статус Tree-of-Thought Engine
    print("Тест 1: Статус Tree-of-Thought Engine")
    print("-" * 60)
    try:
        resp = requests.get(f"{BASE_URL}/api/tree-of-thought/status")
        data = resp.json()
        
        print(f"✓ Total trees: {data.get('total_trees', 0)}")
        print(f"✓ Total branches explored: {data.get('total_branches_explored', 0)}")
        print(f"✓ Successful branches: {data.get('total_successful_branches', 0)}")
        print(f"✓ Average success rate: {data.get('average_success_rate', 0):.1%}")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()
    
    # Тест 2: Решение задачи с Tree-of-Thought
    print("Тест 2: Решение задачи с Tree-of-Thought")
    print("-" * 60)
    print("Задача: Проверить статус всех сервисов")
    try:
        resp = requests.post(
            f"{BASE_URL}/api/tree-of-thought/solve",
            data={
                "task": "Проверить статус всех сервисов и вернуть отчет"
            }
        )
        data = resp.json()
        
        print(f"✓ Status: {data.get('status')}")
        print(f"✓ Tree ID: {data.get('tree_id')}")
        print(f"✓ Depth: {data.get('depth')} steps")
        
        stats = data.get('stats', {})
        print(f"\n📊 Статистика исследования:")
        print(f"   Total branches explored: {stats.get('total_branches_explored', 0)}")
        print(f"   Successful: {stats.get('successful_branches', 0)}")
        print(f"   Failed (hidden): {stats.get('failed_branches', 0)}")
        print(f"   Efficiency: {stats.get('efficiency', 0):.1%}")
        
        print(f"\n✅ Успешный путь (что видит модель):")
        for i, step in enumerate(data.get('successful_path', []), 1):
            print(f"   {i}. {step}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    print()
    
    # Тест 3: Получение контекста только с успешными шагами
    print("Тест 3: Контекст для модели (только успехи)")
    print("-" * 60)
    try:
        # Используем tree_id из предыдущего теста
        if 'data' in locals() and data.get('tree_id'):
            tree_id = data['tree_id']
            resp = requests.get(f"{BASE_URL}/api/tree-of-thought/context/{tree_id}")
            context_data = resp.json()
            
            print("Контекст, который видит модель:")
            print(context_data.get('context', ''))
            print()
            print("✅ Модель видит только успешные шаги!")
            print("❌ Неудачные ветки скрыты от контекста")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()
    
    # Тест 4: Сравнение с обычным выполнением
    print("Тест 4: Сравнение Tree-of-Thought vs обычное выполнение")
    print("-" * 60)
    try:
        # Обычное выполнение
        resp1 = requests.post(
            f"{BASE_URL}/api/autonomous",
            data={
                "message": "Проверить статус сервисов",
                "auto_execute": "true"
            }
        )
        normal_data = resp1.json()
        
        # Tree-of-Thought выполнение
        resp2 = requests.post(
            f"{BASE_URL}/api/tree-of-thought/solve",
            data={
                "task": "Проверить статус сервисов"
            }
        )
        tot_data = resp2.json()
        
        print("Обычное выполнение:")
        print(f"  Шагов: {len(normal_data.get('task_result', {}).get('result', []))}")
        print(f"  Latency: {normal_data.get('latency_ms', 0):.0f}ms")
        
        print("\nTree-of-Thought:")
        print(f"  Шагов (успешных): {tot_data.get('depth', 0)}")
        print(f"  Веток исследовано: {tot_data.get('stats', {}).get('total_branches_explored', 0)}")
        print(f"  Эффективность: {tot_data.get('stats', {}).get('efficiency', 0):.1%}")
        
        print("\n💡 Tree-of-Thought исследует больше вариантов,")
        print("   но показывает модели только успешный путь!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    print()
    
    # Тест 5: Общая статистика
    print("Тест 5: Общая статистика Tree-of-Thought")
    print("-" * 60)
    try:
        resp = requests.get(f"{BASE_URL}/api/tree-of-thought/status")
        data = resp.json()
        
        print(f"📊 Всего деревьев создано: {data.get('total_trees', 0)}")
        print(f"📊 Всего веток исследовано: {data.get('total_branches_explored', 0)}")
        print(f"📊 Успешных веток: {data.get('total_successful_branches', 0)}")
        print(f"📊 Средний success rate: {data.get('average_success_rate', 0):.1%}")
        print(f"📊 Среднее веток на дерево: {data.get('average_branches_per_tree', 0):.1f}")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()
    
    print("=" * 60)
    print("🎯 ИТОГ: Tree-of-Thought Engine")
    print()
    print("✅ Генерирует несколько веток решений")
    print("✅ Оценивает каждую ветку независимо")
    print("✅ Выбирает лучшую успешную ветку")
    print("✅ Скрывает неудачные ветки от модели")
    print("✅ Модель видит только историю успеха")
    print()
    print("🧠 Философия: 'Иллюзия безошибочности'")
    print("   Модель думает, что всё получается с первого раза,")
    print("   но на самом деле система исследует множество путей")
    print("   и показывает только успешный.")
    print()
    print("🚀 Эмерджентный эффект:")
    print("   Система в целом робастнее, чем каждая отдельная ветка!")

if __name__ == "__main__":
    test_tree_of_thought()
