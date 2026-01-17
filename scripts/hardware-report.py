#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отчёт о железе и системе хоста
Собирает информацию о CPU, RAM, дисках, ОС
"""

import platform
import psutil
import subprocess
import json
from datetime import datetime
from pathlib import Path

def get_size(bytes, suffix="B"):
    """Конвертация байтов в читаемый формат"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor

def get_cpu_info():
    """Информация о процессоре"""
    print("  ✓ Сбор информации о CPU...")
    
    info = {
        "физических_ядер": psutil.cpu_count(logical=False),
        "логических_ядер": psutil.cpu_count(logical=True),
        "частота_мгц": psutil.cpu_freq().current if psutil.cpu_freq() else "N/A",
        "загрузка_процент": psutil.cpu_percent(interval=1),
        "архитектура": platform.machine(),
        "процессор": platform.processor()
    }
    
    return info

def get_memory_info():
    """Информация о памяти"""
    print("  ✓ Сбор информации о RAM...")
    
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    info = {
        "ram": {
            "всего": get_size(mem.total),
            "доступно": get_size(mem.available),
            "используется": get_size(mem.used),
            "процент": mem.percent
        },
        "swap": {
            "всего": get_size(swap.total),
            "используется": get_size(swap.used),
            "процент": swap.percent
        }
    }
    
    return info

def get_disk_info():
    """Информация о дисках"""
    print("  ✓ Сбор информации о дисках...")
    
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "устройство": partition.device,
                "точка_монтирования": partition.mountpoint,
                "файловая_система": partition.fstype,
                "всего": get_size(usage.total),
                "используется": get_size(usage.used),
                "свободно": get_size(usage.free),
                "процент": usage.percent
            })
        except PermissionError:
            continue
    
    return disks

def get_os_info():
    """Информация об ОС"""
    print("  ✓ Сбор информации об ОС...")
    
    info = {
        "система": platform.system(),
        "версия": platform.version(),
        "релиз": platform.release(),
        "платформа": platform.platform(),
        "имя_хоста": platform.node(),
        "python_версия": platform.python_version()
    }
    
    return info

def get_network_info():
    """Информация о сети"""
    print("  ✓ Сбор информации о сети...")
    
    interfaces = []
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == 2:  # IPv4
                interfaces.append({
                    "интерфейс": interface,
                    "ip": addr.address,
                    "маска": addr.netmask
                })
    
    return interfaces

def get_docker_info():
    """Информация о Docker"""
    print("  ✓ Сбор информации о Docker...")
    
    try:
        # Docker version
        version = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Docker info
        info_cmd = subprocess.run(
            ['docker', 'info', '--format', '{{json .}}'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        docker_info = json.loads(info_cmd.stdout) if info_cmd.stdout else {}
        
        return {
            "версия": version.stdout.strip(),
            "контейнеров": docker_info.get('Containers', 0),
            "образов": docker_info.get('Images', 0),
            "драйвер_хранилища": docker_info.get('Driver', 'N/A')
        }
    except Exception as e:
        return {"ошибка": str(e)}

def get_gpu_info():
    """Информация о GPU (если доступно)"""
    print("  ✓ Проверка GPU...")
    
    try:
        # Попытка получить информацию через nvidia-smi
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            gpus = []
            for line in lines:
                parts = line.split(',')
                if len(parts) >= 3:
                    gpus.append({
                        "название": parts[0].strip(),
                        "память": parts[1].strip(),
                        "драйвер": parts[2].strip()
                    })
            return gpus
        else:
            return None
    except:
        return None

def create_report():
    """Создать полный отчёт"""
    print("\n📊 Сбор информации о системе хоста...\n")
    
    report = {
        "дата_создания": datetime.now().isoformat(),
        "cpu": get_cpu_info(),
        "память": get_memory_info(),
        "диски": get_disk_info(),
        "операционная_система": get_os_info(),
        "сеть": get_network_info(),
        "docker": get_docker_info()
    }
    
    # GPU опционально
    gpu = get_gpu_info()
    if gpu:
        report["gpu"] = gpu
    
    return report

def print_report(report):
    """Печать отчёта"""
    print("\n" + "="*70)
    print("🖥️  ОТЧЁТ О СИСТЕМЕ ХОСТА".center(70))
    print("="*70 + "\n")
    
    # ОС
    print("💻 Операционная система:")
    os_info = report['операционная_система']
    print(f"  Система: {os_info['система']} {os_info['релиз']}")
    print(f"  Платформа: {os_info['платформа']}")
    print(f"  Имя хоста: {os_info['имя_хоста']}")
    print(f"  Python: {os_info['python_версия']}")
    
    # CPU
    print(f"\n🔧 Процессор:")
    cpu = report['cpu']
    print(f"  Модель: {cpu['процессор']}")
    print(f"  Архитектура: {cpu['архитектура']}")
    print(f"  Физических ядер: {cpu['физических_ядер']}")
    print(f"  Логических ядер: {cpu['логических_ядер']}")
    print(f"  Частота: {cpu['частота_мгц']:.0f} MHz" if isinstance(cpu['частота_мгц'], (int, float)) else f"  Частота: {cpu['частота_мгц']}")
    print(f"  Загрузка: {cpu['загрузка_процент']}%")
    
    # RAM
    print(f"\n💾 Оперативная память:")
    ram = report['память']['ram']
    print(f"  Всего: {ram['всего']}")
    print(f"  Используется: {ram['используется']} ({ram['процент']}%)")
    print(f"  Доступно: {ram['доступно']}")
    
    swap = report['память']['swap']
    if swap['процент'] > 0:
        print(f"\n  Swap:")
        print(f"    Всего: {swap['всего']}")
        print(f"    Используется: {swap['используется']} ({swap['процент']}%)")
    
    # Диски
    print(f"\n💿 Диски:")
    for disk in report['диски']:
        print(f"\n  {disk['устройство']} ({disk['точка_монтирования']})")
        print(f"    ФС: {disk['файловая_система']}")
        print(f"    Всего: {disk['всего']}")
        print(f"    Используется: {disk['используется']} ({disk['процент']}%)")
        print(f"    Свободно: {disk['свободно']}")
    
    # Сеть
    print(f"\n🌐 Сетевые интерфейсы:")
    for iface in report['сеть']:
        print(f"  {iface['интерфейс']}: {iface['ip']}")
    
    # Docker
    print(f"\n🐳 Docker:")
    docker = report['docker']
    if 'ошибка' not in docker:
        print(f"  Версия: {docker['версия']}")
        print(f"  Контейнеров: {docker['контейнеров']}")
        print(f"  Образов: {docker['образов']}")
        print(f"  Драйвер: {docker['драйвер_хранилища']}")
    else:
        print(f"  ⚠️  Docker недоступен: {docker['ошибка']}")
    
    # GPU
    if 'gpu' in report and report['gpu']:
        print(f"\n🎮 GPU:")
        for i, gpu in enumerate(report['gpu'], 1):
            print(f"  GPU {i}: {gpu['название']}")
            print(f"    Память: {gpu['память']}")
            print(f"    Драйвер: {gpu['драйвер']}")
    
    print("\n" + "="*70 + "\n")

def save_report(report, filename="generated/hardware-report.json"):
    """Сохранить отчёт в файл"""
    Path(filename).parent.mkdir(exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Отчёт сохранён: {filename}")
    
    # Также создать Markdown версию
    md_filename = filename.replace('.json', '.md')
    create_markdown_report(report, md_filename)
    print(f"📄 Markdown версия: {md_filename}")

def create_markdown_report(report, filename):
    """Создать Markdown версию отчёта"""
    
    md = f"""# 🖥️ Отчёт о системе хоста

**Дата создания**: {report['дата_создания']}

---

## 💻 Операционная система

- **Система**: {report['операционная_система']['система']} {report['операционная_система']['релиз']}
- **Платформа**: {report['операционная_система']['платформа']}
- **Имя хоста**: {report['операционная_система']['имя_хоста']}
- **Python**: {report['операционная_система']['python_версия']}

---

## 🔧 Процессор

- **Модель**: {report['cpu']['процессор']}
- **Архитектура**: {report['cpu']['архитектура']}
- **Физических ядер**: {report['cpu']['физических_ядер']}
- **Логических ядер**: {report['cpu']['логических_ядер']}
- **Частота**: {report['cpu']['частота_мгц']} MHz
- **Текущая загрузка**: {report['cpu']['загрузка_процент']}%

---

## 💾 Оперативная память

### RAM
- **Всего**: {report['память']['ram']['всего']}
- **Используется**: {report['память']['ram']['используется']} ({report['память']['ram']['процент']}%)
- **Доступно**: {report['память']['ram']['доступно']}

### Swap
- **Всего**: {report['память']['swap']['всего']}
- **Используется**: {report['память']['swap']['используется']} ({report['память']['swap']['процент']}%)

---

## 💿 Диски

"""
    
    for disk in report['диски']:
        md += f"""
### {disk['устройство']} ({disk['точка_монтирования']})
- **Файловая система**: {disk['файловая_система']}
- **Всего**: {disk['всего']}
- **Используется**: {disk['используется']} ({disk['процент']}%)
- **Свободно**: {disk['свободно']}
"""
    
    md += "\n---\n\n## 🌐 Сетевые интерфейсы\n\n"
    
    for iface in report['сеть']:
        md += f"- **{iface['интерфейс']}**: {iface['ip']} (маска: {iface['маска']})\n"
    
    md += "\n---\n\n## 🐳 Docker\n\n"
    
    docker = report['docker']
    if 'ошибка' not in docker:
        md += f"""- **Версия**: {docker['версия']}
- **Контейнеров**: {docker['контейнеров']}
- **Образов**: {docker['образов']}
- **Драйвер хранилища**: {docker['драйвер_хранилища']}
"""
    else:
        md += f"⚠️ Docker недоступен: {docker['ошибка']}\n"
    
    if 'gpu' in report and report['gpu']:
        md += "\n---\n\n## 🎮 GPU\n\n"
        for i, gpu in enumerate(report['gpu'], 1):
            md += f"""### GPU {i}
- **Название**: {gpu['название']}
- **Память**: {gpu['память']}
- **Драйвер**: {gpu['драйвер']}

"""
    
    md += """---

## 📊 Рекомендации

### Для AI системы:
"""
    
    # Анализ и рекомендации
    ram_gb = float(report['память']['ram']['всего'].split()[0])
    cpu_cores = report['cpu']['логических_ядер']
    
    if ram_gb < 8:
        md += "- ⚠️ **RAM**: Рекомендуется минимум 8GB для комфортной работы\n"
    elif ram_gb < 16:
        md += "- ✅ **RAM**: Достаточно для базовой работы, рекомендуется 16GB для оптимальной производительности\n"
    else:
        md += "- ✅ **RAM**: Отлично! Достаточно памяти для работы с большими моделями\n"
    
    if cpu_cores < 4:
        md += "- ⚠️ **CPU**: Рекомендуется минимум 4 ядра\n"
    elif cpu_cores < 8:
        md += "- ✅ **CPU**: Достаточно для работы системы\n"
    else:
        md += "- ✅ **CPU**: Отлично! Достаточно ядер для параллельной обработки\n"
    
    # Проверка свободного места
    for disk in report['диски']:
        if 'C:' in disk['устройство'] or disk['точка_монтирования'] == '/':
            free_gb = float(disk['свободно'].split()[0])
            if free_gb < 20:
                md += f"- ⚠️ **Диск**: Мало свободного места ({disk['свободно']}), рекомендуется минимум 20GB\n"
            else:
                md += f"- ✅ **Диск**: Достаточно свободного места ({disk['свободно']})\n"
    
    if 'gpu' in report and report['gpu']:
        md += "- ✅ **GPU**: Обнаружен GPU! Можно использовать для ускорения AI моделей\n"
    else:
        md += "- ℹ️ **GPU**: GPU не обнаружен, система будет работать на CPU\n"
    
    md += "\n---\n\n*Отчёт создан автоматически*\n"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md)

def main():
    """Главная функция"""
    print("\n🤖 Сбор информации о системе хоста для AI системы\n")
    
    report = create_report()
    print_report(report)
    save_report(report)
    
    print("✅ Готово!\n")

if __name__ == "__main__":
    main()
