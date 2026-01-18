"""
Скрипт для публикации проекта на GitHub

ВАЖНО: GitHub больше не принимает пароли для Git операций!
Вам нужен Personal Access Token:
1. Перейдите: https://github.com/settings/tokens/new
2. Создайте токен с правами 'repo'
3. Используйте токен вместо пароля

Или используйте GitHub CLI: gh auth login
"""
import subprocess
import sys
import os
from getpass import getpass


def run_command(cmd, capture_output=False):
    """Выполнить команду"""
    print(f"🔧 Выполняю: {cmd}")
    try:
        if capture_output:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                check=True
            )
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")
        if capture_output and e.stderr:
            print(f"   {e.stderr}")
        return None


def check_git_status():
    """Проверить статус Git"""
    print("\n📊 Проверка статуса Git...")
    
    # Проверяем есть ли uncommitted changes
    status = run_command("git status --porcelain", capture_output=True)
    if status:
        print("⚠️  Есть незакоммиченные изменения:")
        print(status)
        
        commit = input("\n💾 Закоммитить изменения? (y/n): ")
        if commit.lower() == 'y':
            message = input("📝 Сообщение коммита: ")
            run_command("git add -A")
            run_command(f'git commit -m "{message}"')
    else:
        print("✅ Все изменения закоммичены")


def setup_github_repo():
    """Настроить GitHub репозиторий"""
    print("\n🔧 Настройка GitHub репозитория...")
    
    # Проверяем есть ли уже remote
    remotes = run_command("git remote -v", capture_output=True)
    if remotes and "origin" in remotes:
        print("✅ Remote 'origin' уже настроен:")
        print(remotes)
        
        change = input("\n🔄 Изменить remote? (y/n): ")
        if change.lower() == 'y':
            run_command("git remote remove origin")
        else:
            return True
    
    # Запрашиваем данные
    print("\n📝 Введите данные GitHub:")
    username = input("GitHub username: ")
    repo_name = input("Название репозитория (по умолчанию: kiro-ai-local): ") or "kiro-ai-local"
    
    # Добавляем remote
    remote_url = f"https://github.com/{username}/{repo_name}.git"
    print(f"\n🔗 Добавляю remote: {remote_url}")
    
    result = run_command(f"git remote add origin {remote_url}")
    if result is None:  # Команда выполнилась без ошибок
        print("✅ Remote добавлен успешно")
        return True
    else:
        print("❌ Не удалось добавить remote")
        return False


def push_to_github():
    """Push на GitHub"""
    print("\n🚀 Публикация на GitHub...")
    print("\n⚠️  ВАЖНО: GitHub требует Personal Access Token!")
    print("   Создайте токен: https://github.com/settings/tokens/new")
    print("   Права: ✓ repo (все подпункты)")
    print("\n   При запросе пароля введите ТОКЕН (не пароль аккаунта)!")
    
    input("\n📌 Нажмите Enter когда будете готовы...")
    
    # Пробуем push
    print("\n📤 Отправляю код на GitHub...")
    result = run_command("git push -u origin master")
    
    if result is None:  # Успех
        print("\n✅ Код успешно опубликован на GitHub!")
        return True
    else:
        print("\n❌ Не удалось опубликовать код")
        print("\n💡 Возможные причины:")
        print("   1. Репозиторий не создан на GitHub")
        print("   2. Неверный токен")
        print("   3. Нет прав на запись")
        return False


def create_repo_with_api():
    """Создать репозиторий через GitHub API"""
    print("\n🔧 Создание репозитория через GitHub API...")
    
    try:
        import requests
    except ImportError:
        print("❌ Требуется библиотека 'requests'")
        print("   Установите: pip install requests")
        return False
    
    username = input("GitHub username: ")
    token = getpass("Personal Access Token: ")
    repo_name = input("Название репозитория (по умолчанию: kiro-ai-local): ") or "kiro-ai-local"
    description = input("Описание (по умолчанию: AI Combiner Stack with Tree-of-Thought): ") or "AI Combiner Stack with Tree-of-Thought Engine"
    is_private = input("Приватный репозиторий? (y/n, по умолчанию: n): ").lower() == 'y'
    
    # Создаем репозиторий
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "description": description,
        "private": is_private,
        "auto_init": False
    }
    
    print(f"\n📡 Создаю репозиторий {repo_name}...")
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("✅ Репозиторий создан успешно!")
        repo_url = response.json()["html_url"]
        print(f"   URL: {repo_url}")
        
        # Добавляем remote
        remote_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
        run_command(f"git remote add origin {remote_url}")
        
        return True
    else:
        print(f"❌ Ошибка создания репозитория: {response.status_code}")
        print(f"   {response.json().get('message', 'Unknown error')}")
        return False


def main():
    """Главная функция"""
    print("=" * 60)
    print("🚀 ПУБЛИКАЦИЯ ПРОЕКТА НА GITHUB")
    print("=" * 60)
    
    # Проверяем что мы в Git репозитории
    if not os.path.exists(".git"):
        print("❌ Это не Git репозиторий!")
        print("   Выполните: git init")
        sys.exit(1)
    
    # Проверяем статус
    check_git_status()
    
    # Выбираем метод
    print("\n📋 Выберите метод публикации:")
    print("1. Создать репозиторий вручную на GitHub (рекомендуется)")
    print("2. Создать репозиторий через API (требуется токен)")
    print("3. Использовать существующий репозиторий")
    
    choice = input("\nВыбор (1/2/3): ")
    
    if choice == "1":
        print("\n📝 Инструкция:")
        print("1. Откройте: https://github.com/new")
        print("2. Создайте репозиторий (НЕ добавляйте README, .gitignore)")
        print("3. Скопируйте URL репозитория")
        
        input("\n📌 Нажмите Enter когда создадите репозиторий...")
        
        if setup_github_repo():
            push_to_github()
    
    elif choice == "2":
        if create_repo_with_api():
            push_to_github()
    
    elif choice == "3":
        if setup_github_repo():
            push_to_github()
    
    else:
        print("❌ Неверный выбор")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ ГОТОВО!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
