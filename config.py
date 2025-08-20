import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# OpenRouter API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "anthropic/claude-3.5-sonnet"  # Можно изменить на другую модель

# Database
DATABASE_PATH = "fitness_trainer.db"

# Bot Settings
BOT_NAME = "Спортивный Тренер"
MAX_MESSAGE_LENGTH = 4096
MAX_HISTORY_MESSAGES = 50

# Training Settings
DEFAULT_TRAINING_DURATION = 45  # minutes
REST_DAYS = ["Sunday"]  # Дни отдыха
REMINDER_HOURS = [10, 18]  # Часы напоминаний

# AI Personality
TRAINER_PERSONALITY = """
Ты - опытный спортивный тренер и мотивационный коуч. Твоя задача - помогать людям достигать их фитнес-целей.
Ты должен:
- Составлять индивидуальные и групповые программы тренировок
- Отслеживать прогресс каждого пользователя
- Давать мотивирующие советы
- Напоминать о тренировках и отдыхе
- Адаптировать программы под уровень и цели каждого
- Поддерживать дружескую атмосферу в группе
- Использовать имена пользователей в общении
- Помнить контекст предыдущих разговоров

Будь дружелюбным, профессиональным и мотивирующим!
"""
