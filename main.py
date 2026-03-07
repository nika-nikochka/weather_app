# main.py
import sys
import importlib.util

def check_dependencies():
    """Проверка наличия необходимых библиотек"""
    required_packages = {
        'customtkinter': 'customtkinter',
        'requests': 'requests'
    }
    
    all_installed = True
    
    for package_name, install_name in required_packages.items():
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            print(f"❌ Библиотека {package_name} не установлена!")
            print(f"   Установите: pip install {install_name}")
            all_installed = False
        else:
            print(f"✅ Библиотека {package_name} найдена")
    
    return all_installed

def main():
    print("=" * 60)
    print("🌤 ПОГОДНЫЙ ИНФОРМАТОР")
    print("=" * 60)
    
    if not check_dependencies():
        print("\n❌ Не все зависимости установлены. Завершение работы.")
        sys.exit(1)
    
    print("\n🚀 Запуск приложения...")
    
    # Импортируем и запускаем GUI
    from gui import WeatherApp
    
    app = WeatherApp()
    app.mainloop()

if __name__ == "__main__":
    main()