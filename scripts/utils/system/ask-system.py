#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Попросить систему выполнить задачу"""

import requests
import sys

def ask_system(message, auto_execute=True):
    """Отправить задачу системе"""
    print(f"\n🤖 Отправка задачи системе...")
    print(f"📝 Задача: {message}\n")
    
    data = {
        "message": message,
        "auto_execute": str(auto_execute).lower()
    }
    
    try:
        response = requests.post(
            "http://localhost:9000/api/autonomous",
            data=data,
            timeout=180
        )
        
        result = response.json()
        
        print(f"🎯 Intent: {result.get('intent')}")
        print(f"⚡ Decision: {result.get('execution_plan', {}).get('autonomous_decision', {}).get('action')}")
        
        if result.get('task_result'):
            summary = result['task_result']['summary']
            print(f"📊 Success: {summary.get('success_rate')}%")
            print(f"\n📝 Выполненные шаги:")
            
            for step in result['task_result']['result']:
                status = step.get('status')
                icon = "✅" if status in ['success', 'completed'] else "❌"
                print(f"  {icon} {step.get('step')}")
                
                # Показать дополнительную информацию
                if step.get('data'):
                    data = step['data']
                    if isinstance(data, dict):
                        if 'file_created' in data:
                            print(f"      📄 Файл: {data['file_created']}")
                        if 'lines' in data:
                            print(f"      📏 Строк: {data['lines']}")
        else:
            print("⚠️  Задача не выполнена")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = "Create a Python script that collects hardware information (CPU, RAM, disk, OS, Docker) and saves report to generated/hardware-report.md. Save script to generated/hardware-info.py"
    
    ask_system(message)
