#!/usr/bin/env python3
"""Тестирование Self-Modification - финальный уровень автономности"""

import requests

print("\n🔄 ТЕСТИРОВАНИЕ SELF-MODIFICATION ENGINE\n")
print("⚠️  ВНИМАНИЕ: Это финальный уровень автономности!")
print("Система может модифицировать свой собственный код.\n")

# Тест 1: Статус системы самомодификации
print("Тест 1: Статус Self-Modification Engine")
print("-" * 60)

status_response = requests.get('http://localhost:9000/api/self-modification/status')
status = status_response.json()

stats = status.get('stats', {})
print(f"✓ Total modifications: {stats.get('total_modifications', 0)}")
print(f"✓ Successful: {stats.get('successful', 0)}")
print(f"✓ Success rate: {stats.get('success_rate', 0):.1f}%")
print(f"✓ Safe zones: {stats.get('safe_zones', 0)} files")
print(f"✓ Protected files: {stats.get('protected_files', 0)} files")

print(f"\n📁 Безопасные зоны для модификации:")
for zone in status.get('safe_zones', [])[:5]:
    print(f"   ✓ {zone}")

print(f"\n🔒 Защищенные файлы:")
for protected in status.get('protected_files', []):
    print(f"   🛡️  {protected}")

# Тест 2: Предложение модификации (безопасной)
print("\n\nТест 2: Предложение безопасной модификации")
print("-" * 60)

proposal_response = requests.post(
    'http://localhost:9000/api/self-modification/propose',
    data={
        'file_path': 'services/web-ui/adaptive_planner.py',
        'modification_type': 'optimize_code',
        'description': 'Optimize learning algorithm for better performance'
    }
)
proposal = proposal_response.json()

print(f"✓ Approved: {proposal.get('approved')}")
print(f"✓ Risk level: {proposal.get('risk_level')}")
print(f"✓ Backup created: {proposal.get('backup_path', 'N/A')}")
print(f"✓ Requires confirmation: {proposal.get('requires_confirmation', False)}")

if proposal.get('approved'):
    print(f"✅ Модификация одобрена! Система может улучшить себя.")
else:
    print(f"❌ Модификация отклонена: {proposal.get('reason')}")

# Тест 3: Попытка модифицировать защищенный файл
print("\n\nТест 3: Попытка модифицировать защищенный файл")
print("-" * 60)

protected_proposal = requests.post(
    'http://localhost:9000/api/self-modification/propose',
    data={
        'file_path': 'docker-compose.yml',
        'modification_type': 'modify_logic',
        'description': 'Try to modify protected file'
    }
)
protected_result = protected_proposal.json()

print(f"✓ Approved: {protected_result.get('approved')}")
print(f"✓ Reason: {protected_result.get('reason')}")

if not protected_result.get('approved'):
    print(f"✅ Защита работает! Критичные файлы защищены.")
else:
    print(f"❌ ОШИБКА: Система разрешила модификацию защищенного файла!")

# Тест 4: Автономное самоулучшение
print("\n\nТест 4: Автономное самоулучшение")
print("-" * 60)

print("🤖 Запускаем автономное самоулучшение...")
improve_response = requests.post('http://localhost:9000/api/self-modification/autonomous')
improve_result = improve_response.json()

print(f"✓ Status: {improve_result.get('status')}")

if improve_result.get('improvements'):
    improvements = improve_result['improvements']
    print(f"✓ Improvements proposed: {improvements.get('improvements_proposed', 0)}")
    
    if improvements.get('improvements'):
        print(f"\n💡 Предложенные улучшения:")
        for imp in improvements['improvements']:
            print(f"   - {imp['type']}: {imp['reason']}")

# Тест 5: История модификаций
print("\n\nТест 5: История модификаций")
print("-" * 60)

status_response2 = requests.get('http://localhost:9000/api/self-modification/status')
status2 = status_response2.json()

history = status2.get('history', [])
if history:
    print(f"✓ История содержит {len(history)} записей:")
    for i, mod in enumerate(history, 1):
        print(f"   {i}. {mod.get('file_path')} - {mod.get('modification_type')} ({mod.get('risk_level')} risk)")
else:
    print(f"✓ История пуста (модификации еще не применялись)")

print("\n" + "="*60)
print("\n🎯 ИТОГ: Self-Modification Engine готов!")
print("Система достигла финального уровня автономности.")
print("Она может анализировать себя и предлагать улучшения своего кода.")
print("\n⚠️  Для безопасности:")
print("   - Критичные файлы защищены от модификации")
print("   - Автоматические бэкапы перед изменениями")
print("   - Проверка синтаксиса и автоматический откат при ошибках")
print("   - Высокорисковые изменения требуют подтверждения")
