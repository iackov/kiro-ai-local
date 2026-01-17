#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сбор статистики о системе
Корректная работа с кириллицей через Python
"""

import requests
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class SystemStats:
    """Класс для сбора статистики системы"""
    
    def __init__(self):
        self.base_url = "http://localhost:9000"
        self.stats = {}
    
    def collect_all(self) -> Dict[str, Any]:
        """Собрать всю статистику"""
        print("📊 Сбор статистики системы...\n")
        
        self.stats['timestamp'] = datetime.now().isoformat()
        self.stats['services'] = self.get_services_status()
        self.stats['docker'] = self.get_docker_stats()
        self.stats['ollama'] = self.get_ollama_models()
        self.stats['files'] = self.get_file_stats()
        self.stats['git'] = self.get_git_stats()
        
        return self.stats
    
    def get_services_status(self) -> Dict[str, Any]:
        """Статус сервисов"""
        print("  ✓ Проверка сервисов...")
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_docker_stats(self) -> Dict[str, Any]:
        """Статистика Docker"""
        print("  ✓ Сбор Docker статистики...")
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}},{{.Status}},{{.Image}}'],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        containers.append({
                            'name': parts[0],
                            'status': parts[1],
                            'image': parts[2]
                        })
            
            return {
                'total': len(containers),
                'containers': containers
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_ollama_models(self) -> Dict[str, Any]:
        """Модели Ollama"""
        print("  ✓ Проверка Ollama моделей...")
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            data = response.json()
            
            models = []
            for model in data.get('models', []):
                models.append({
                    'name': model.get('name'),
                    'size': model.get('size', 0) / (1024**3),  # GB
                    'modified': model.get('modified_at')
                })
            
            return {
                'total': len(models),
                'models': models
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_file_stats(self) -> Dict[str, Any]:
        """Статистика файлов"""
        print("  ✓ Подсчёт файлов...")
        
        stats = {
            'python': 0,
            'powershell': 0,
            'markdown': 0,
            'yaml': 0,
            'total_lines': 0
        }
        
        # Подсчёт Python файлов
        for py_file in Path('.').rglob('*.py'):
            if 'venv' not in str(py_file) and '__pycache__' not in str(py_file):
                stats['python'] += 1
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        stats['total_lines'] += len(f.readlines())
                except:
                    pass
        
        # Подсчёт PowerShell файлов
        for ps_file in Path('scripts').glob('*.ps1'):
            stats['powershell'] += 1
        
        # Подсчёт Markdown файлов
        for md_file in Path('.').rglob('*.md'):
            if '.git' not in str(md_file):
                stats['markdown'] += 1
        
        # Подсчёт YAML файлов
        for yaml_file in Path('.').rglob('*.yml'):
            if '.git' not in str(yaml_file):
                stats['yaml'] += 1
        
        return stats
    
    def get_git_stats(self) -> Dict[str, Any]:
        """Git статистика"""
        print("  ✓ Сбор Git статистики...")
        try:
            # Количество коммитов
            commits = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                capture_output=True,
                text=True
            )
            
            # Последний коммит
            last_commit = subprocess.run(
                ['git', 'log', '-1', '--format=%H|%s|%ai'],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            commit_parts = last_commit.stdout.strip().split('|')
            
            return {
                'total_commits': int(commits.stdout.strip()),
                'last_commit': {
                    'hash': commit_parts[0] if len(commit_parts) > 0 else '',
                    'message': commit_parts[1] if len(commit_parts) > 1 else '',
                    'date': commit_parts[2] if len(commit_parts) > 2 else ''
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def print_summary(self):
        """Печать сводки"""
        print("\n" + "="*60)
        print("📊 СВОДКА СТАТИСТИКИ".center(60))
        print("="*60 + "\n")
        
        # Сервисы
        print("🚀 Сервисы:")
        services = self.stats.get('services', {}).get('services', {})
        for name, info in services.items():
            status = "✅" if info.get('status') == 'healthy' else "❌"
            print(f"  {status} {name}: {info.get('status', 'unknown')}")
        
        # Docker
        print(f"\n🐳 Docker:")
        docker = self.stats.get('docker', {})
        print(f"  Контейнеров: {docker.get('total', 0)}")
        
        # Ollama
        print(f"\n🧠 AI Модели:")
        ollama = self.stats.get('ollama', {})
        print(f"  Всего моделей: {ollama.get('total', 0)}")
        for model in ollama.get('models', []):
            print(f"  • {model['name']} ({model['size']:.2f} GB)")
        
        # Файлы
        print(f"\n📁 Файлы:")
        files = self.stats.get('files', {})
        print(f"  Python: {files.get('python', 0)}")
        print(f"  PowerShell: {files.get('powershell', 0)}")
        print(f"  Markdown: {files.get('markdown', 0)}")
        print(f"  YAML: {files.get('yaml', 0)}")
        print(f"  Всего строк кода: {files.get('total_lines', 0):,}")
        
        # Git
        print(f"\n📝 Git:")
        git = self.stats.get('git', {})
        print(f"  Коммитов: {git.get('total_commits', 0)}")
        last = git.get('last_commit', {})
        if last:
            print(f"  Последний: {last.get('message', 'N/A')[:50]}")
            print(f"  Дата: {last.get('date', 'N/A')}")
        
        print("\n" + "="*60 + "\n")
    
    def save_to_file(self, filename: str = "generated/system-stats.json"):
        """Сохранить в файл"""
        Path(filename).parent.mkdir(exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Статистика сохранена: {filename}")

def main():
    """Главная функция"""
    print("\n🤖 Сбор статистики автономной AI системы\n")
    
    collector = SystemStats()
    collector.collect_all()
    collector.print_summary()
    collector.save_to_file()
    
    print("✅ Готово!\n")

if __name__ == "__main__":
    main()
