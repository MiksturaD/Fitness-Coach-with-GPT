#!/usr/bin/env python3
"""
Скрипт для запуска спортивного тренера
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Проверка переменных окружения"""
    print("🔍 Проверка настроек...")
    
    # Загружаем .env файл
    load_dotenv()
    
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    
    errors = []
    
    if not telegram_token or telegram_token == "your_telegram_bot_token_here":
        errors.append("❌ TELEGRAM_TOKEN не настроен")
    else:
        print("✅ TELEGRAM_TOKEN настроен")
    
    if not openrouter_key or openrouter_key == "your_openrouter_api_key_here":
        errors.append("❌ OPENROUTER_API_KEY не настроен")
    else:
        print("✅ OPENROUTER_API_KEY настроен")
    
    if errors:
        print("\n🚨 Ошибки конфигурации:")
        for error in errors:
            print(error)
        
        print("\n📝 Для настройки:")
        print("1. Скопируйте env_example.txt в .env")
        print("2. Заполните токены в .env файле")
        print("3. Перезапустите скрипт")
        
        return False
    
    return True

def check_dependencies():
    """Проверка зависимостей"""
    print("\n📦 Проверка зависимостей...")
    
    try:
        import telegram
        print("✅ python-telegram-bot установлен")
    except ImportError:
        print("❌ python-telegram-bot не установлен")
        print("Установите: pip install -r requirements.txt")
        return False
    
    try:
        import openai
        print("✅ openai установлен")
    except ImportError:
        print("❌ openai не установлен")
        print("Установите: pip install -r requirements.txt")
        return False
    
    try:
        import aiohttp
        print("✅ aiohttp установлен")
    except ImportError:
        print("❌ aiohttp не установлен")
        print("Установите: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Основная функция"""
    print("🏋️‍♂️ Спортивный Тренер - Запуск")
    print("=" * 40)
    
    # Проверяем настройки
    if not check_environment():
        sys.exit(1)
    
    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)
    
    print("\n🚀 Все проверки пройдены! Запускаем бота...")
    print("Для остановки нажмите Ctrl+C")
    print("-" * 40)
    
    try:
        # Импортируем и запускаем бота
        from bot import FitnessTrainerBot
        
        bot = FitnessTrainerBot()
        bot.run()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска бота: {e}")
        print("Проверьте логи и настройки")

if __name__ == "__main__":
    main()
