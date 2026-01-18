"""
Скрипт для публикации на GitHub через GitHub CLI

САМЫЙ ПРОСТОЙ СПОСОБ!
1. Установите GitHub CLI: winget install GitHub.cli
2. Запустите этот скрипт
3. Авторизуйтесь через браузер (безопасно!)
"""
import subprocess
import sys
import os


def run_command(cmd, capture_output=False):
    """Выполнить команду"""
    print(f"🔧 {cmd}")
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
            result = subprocess.run(cmd, shell=True, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")
        if capture_output and e.stderr:
            print(f"   {e.stderr}")
        return False


def check_gh_cli():
    """Проверить установлен ли GitHub CLI"""
    print("\n🔍 Проверка GitHub CLI...")
    result = run_command("gh --version", capture_output=True)
    
    if result:
        print(f"✅ GitHub CLI установлен: {result.split()[2]}")
        return True
    else:
        print("❌ GitHub CLI не установлен")
        print("\n📥 Установите GitHub CLI:")
        print("   winget install GitHub.cli")
        print("   или скачайте: https://cli.github.com/")
        return False


def check_gh_auth():
    """Проверить авторизацию в GitHub"""
    print("\n🔐 Проверка авторизации...")
    result = run_command("gh auth status", capture_output=True)
    
    if result and "Logged in" in result:
        print("✅ Вы авторизованы в GitHub")
        return True
    else:
        print("⚠️  Вы не авторизованы")
        
        auth = input("\n🔑 Авторизоваться сейчас? (y/n): ")
        if auth.lower() == 'y':
            print("\n📱 Откроется браузер для авторизации...")
            result = run_command("gh auth login")
            if result is None:  # Успех
                print("✅ Авторизация успешна!")
                return True
        
        return False


def commit_changes():
    """Закоммитить изменения"""
    print("\n📊 Проверка изменений...")
    status = run_command("git status --porcelain", capture_output=True)
    
    if status:
        print("⚠️  Есть незакоммиченные изменения")
        
        commit = input("\n💾 Закоммитить? (y/n): ")
        if commit.lower() == 'y':
            message = input("📝 Сообщение коммита: ") or "Update project"
            run_command("git add -A")
            run_command(f'git commit -m "{message}"')
            print("✅ Изменения закоммичены")
    else:
        print("✅ Нет незакоммиченных изменений")


def create_and_push():
    """Создать репозиторий и push"""
    print("\n🚀 Создание репозитория на GitHub...")
    
    # Параметры
    print("\n📝 Настройки репозитория:")
    repo_name = input("Название (по умолчанию: kiro-ai-local): ") or "kiro-ai-local"
    description = input("Описание (Enter для пропуска): ") or "AI Combiner Stack with Tree-of-Thought Engine"
    
    visibility = input("Видимость (public/private, по умолчанию: public): ") or "public"
    
    # Создаем и push одной командой
    cmd = f'gh repo create {repo_name} --{visibility} --source=. --remote=origin --push'
    if description:
        cmd += f' --description "{description}"'
    
    print(f"\n📤 Создаю репозиторий и публикую код...")
    result = run_command(cmd)
    
    if result is None:  # Успех
        print("\n✅ Репозиторий создан и код опубликован!")
        
        # Получаем URL
        url = run_command("gh repo view --web --json url -q .url", capture_output=True)
        if url:
            print(f"\n🔗 URL репозитория: {url}")
            
            open_browser = input("\n🌐 Открыть в браузере? (y/n): ")
            if open_browser.lower() == 'y':
                run_command("gh repo view --web")
        
        return True
    else:
        print("\n❌ Не удалось создать репозиторий")
        return False


def main():
    """Главная функция"""
    print("=" * 60)
    print("🚀 ПУБЛИКАЦИЯ НА GITHUB (через GitHub CLI)")
    print("=" * 60)
    
    # Проверяем Git
    if not os.path.exists(".git"):
        print("❌ Это не Git репозиторий!")
        sys.exit(1)
    
    # Проверяем GitHub CLI
    if not check_gh_cli():
        sys.exit(1)
    
    # Проверяем авторизацию
    if not check_gh_auth():
        print("\n❌ Требуется авторизация в GitHub")
        sys.exit(1)
    
    # Коммитим изменения
    commit_changes()
    
    # Создаем и публикуем
    if create_and_push():
        print("\n" + "=" * 60)
        print("✅ УСПЕХ! Код опубликован на GitHub!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Не удалось опубликовать код")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
