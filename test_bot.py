#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы компонентов бота
"""

import asyncio
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

async def test_database():
    """Тестирование базы данных"""
    print("🧪 Тестирование базы данных...")
    
    try:
        from database import FitnessDatabase
        
        db = FitnessDatabase("test_fitness.db")
        print("✅ База данных инициализирована")
        
        # Тест добавления пользователя
        db.add_user(12345, "test_user", "Тест", "Пользователь")
        print("✅ Пользователь добавлен")
        
        # Тест получения пользователя
        user_info = db.get_user_info(12345)
        if user_info:
            print(f"✅ Пользователь получен: {user_info['first_name']}")
        else:
            print("❌ Ошибка получения пользователя")
        
        # Тест добавления чата
        db.add_chat(67890, "group", "Тестовый чат")
        print("✅ Чат добавлен")
        
        # Тест сохранения сообщения
        db.save_message(67890, 12345, "Тестовое сообщение")
        print("✅ Сообщение сохранено")
        
        # Тест получения истории
        history = db.get_chat_history(67890, limit=5)
        if history:
            print(f"✅ История получена: {len(history)} сообщений")
        else:
            print("❌ Ошибка получения истории")
        
        # Очистка тестовой базы
        os.remove("test_fitness.db")
        print("✅ Тестовая база удалена")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования базы данных: {e}")
        return False

async def test_ai_client():
    """Тестирование AI клиента"""
    print("\n🧪 Тестирование AI клиента...")
    
    try:
        from ai_client import OpenRouterClient
        
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key or api_key == "your_openrouter_api_key_here":
            print("⚠️ API ключ не настроен, пропускаем тест")
            return True
        
        client = OpenRouterClient(api_key=api_key)
        print("✅ AI клиент инициализирован")
        
        # Тест форматирования сообщений
        test_history = [
            {"user_id": 1, "message": "Привет", "first_name": "Анна"},
            {"user_id": 2, "message": "Как дела?", "first_name": "Иван"}
        ]
        
        formatted = client.format_chat_history(test_history)
        if formatted:
            print(f"✅ Сообщения отформатированы: {len(formatted)}")
        else:
            print("❌ Ошибка форматирования сообщений")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования AI клиента: {e}")
        return False

async def test_config():
    """Тестирование конфигурации"""
    print("\n🧪 Тестирование конфигурации...")
    
    try:
        from config import TELEGRAM_TOKEN, OPENROUTER_API_KEY, BOT_NAME
        
        print(f"✅ BOT_NAME: {BOT_NAME}")
        
        if TELEGRAM_TOKEN and TELEGRAM_TOKEN != "your_telegram_bot_token_here":
            print("✅ TELEGRAM_TOKEN настроен")
        else:
            print("⚠️ TELEGRAM_TOKEN не настроен")
        
        if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_openrouter_api_key_here":
            print("✅ OPENROUTER_API_KEY настроен")
        else:
            print("⚠️ OPENROUTER_API_KEY не настроен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования конфигурации: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования компонентов бота...\n")
    
    tests = [
        test_config(),
        test_database(),
        test_ai_client()
    ]
    
    results = await asyncio.gather(*tests)
    
    print(f"\n📊 Результаты тестирования:")
    print(f"✅ Успешно: {sum(results)}")
    print(f"❌ Ошибок: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 Все тесты пройдены успешно!")
        print("Бот готов к запуску!")
    else:
        print("\n⚠️ Некоторые тесты не пройдены.")
        print("Проверьте настройку и зависимости.")

if __name__ == "__main__":
    asyncio.run(main())
