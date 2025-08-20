import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode

from config import TELEGRAM_TOKEN, BOT_NAME, MAX_MESSAGE_LENGTH
from database import FitnessDatabase
from ai_client import OpenRouterClient

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class FitnessTrainerBot:
    def __init__(self):
        self.db = FitnessDatabase("fitness_trainer.db")
        from config import OPENROUTER_API_KEY
        self.ai_client = OpenRouterClient(api_key=OPENROUTER_API_KEY)
        
        # Команды бота
        self.commands = {
            'start': 'Начать работу с ботом',
            'help': 'Показать справку по командам',
            'profile': 'Настроить профиль фитнеса',
            'workout': 'Получить план тренировки',
            'group_workout': 'Групповая тренировка',
            'progress': 'Отследить прогресс',
            'motivation': 'Получить мотивацию',
            'stats': 'Статистика тренировок'
        }
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        chat = update.effective_chat
        
        # Сохраняем пользователя и чат в базе
        self.db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        self.db.add_chat(
            chat_id=chat.id,
            chat_type=chat.type,
            chat_title=chat.title
        )
        
        welcome_message = f"""
🏋️‍♂️ Привет, {user.first_name}! Я {BOT_NAME}!

Я помогу тебе и твоей семье достичь фитнес-целей! 

Что я умею:
✅ Составлять индивидуальные и групповые программы тренировок
✅ Отслеживать прогресс каждого участника
✅ Давать мотивирующие советы
✅ Напоминать о тренировках и отдыхе
✅ Адаптировать программы под твой уровень

Используй команду /help для просмотра всех возможностей!

Начни с настройки профиля командой /profile 🎯
        """
        
        # Создаем клавиатуру с основными командами
        keyboard = [
            [InlineKeyboardButton("📋 Профиль", callback_data="profile")],
            [InlineKeyboardButton("💪 Тренировка", callback_data="workout")],
            [InlineKeyboardButton("👥 Групповая тренировка", callback_data="group_workout")],
            [InlineKeyboardButton("📊 Прогресс", callback_data="progress")],
            [InlineKeyboardButton("🔥 Мотивация", callback_data="motivation")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = f"🤖 <b>{BOT_NAME} - Справка по командам</b>\n\n"
        
        for command, description in self.commands.items():
            help_text += f"/{command} - {description}\n"
        
        help_text += "\n💡 <b>Дополнительно:</b>\n"
        help_text += "• Просто напиши мне сообщение, и я отвечу как тренер\n"
        help_text += "• Используй кнопки под сообщениями для быстрого доступа\n"
        help_text += "• В групповых чатах я помню каждого участника\n"
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /profile"""
        user = update.effective_user
        user_info = self.db.get_user_info(user.id)
        
        if user_info:
            profile_text = f"""
👤 <b>Профиль {user.first_name}</b>

📊 <b>Текущие настройки:</b>
• Уровень подготовки: {user_info.get('fitness_level', 'Не указан')}
• Цели: {user_info.get('goals', 'Не указаны')}

🔄 <b>Обновить профиль:</b>
Выбери свой уровень подготовки:
            """
            
            keyboard = [
                [InlineKeyboardButton("🟢 Начинающий", callback_data="level_beginner")],
                [InlineKeyboardButton("🟡 Средний", callback_data="level_intermediate")],
                [InlineKeyboardButton("🔴 Продвинутый", callback_data="level_advanced")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                profile_text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text("❌ Ошибка получения профиля. Попробуй /start")
    
    async def workout_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /workout"""
        user = update.effective_user
        user_info = self.db.get_user_info(user.id)
        
        if not user_info:
            await update.message.reply_text("❌ Сначала настрой профиль командой /profile")
            return
        
        # Генерируем план тренировки через ИИ
        workout_plan = await self.ai_client.generate_workout_plan(user_info)
        
        if workout_plan:
            # Разбиваем длинное сообщение на части
            if len(workout_plan) > MAX_MESSAGE_LENGTH:
                parts = [workout_plan[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(workout_plan), MAX_MESSAGE_LENGTH)]
                for i, part in enumerate(parts):
                    await update.message.reply_text(f"📋 <b>План тренировки (часть {i+1}/{len(parts)})</b>\n\n{part}", parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text(f"📋 <b>Твой план тренировки:</b>\n\n{workout_plan}", parse_mode=ParseMode.HTML)
            
            # Сохраняем тренировку в базе
            workout_data = {
                "type": "individual",
                "generated_at": datetime.now().isoformat(),
                "user_level": user_info.get('fitness_level'),
                "goals": user_info.get('goals')
            }
            self.db.save_workout(user.id, "individual", workout_data)
            
        else:
            await update.message.reply_text("❌ Не удалось сгенерировать план тренировки. Попробуй позже.")
    
    async def group_workout_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /group_workout"""
        chat = update.effective_chat
        
        if chat.type == "private":
            await update.message.reply_text("👥 Эта команда работает только в групповых чатах!")
            return
        
        # Получаем список пользователей в чате
        chat_users = self.db.get_chat_users(chat.id)
        
        if len(chat_users) < 2:
            await update.message.reply_text("👥 Нужно минимум 2 участника для групповой тренировки!")
            return
        
        # Генерируем групповую тренировку
        group_workout = await self.ai_client.generate_group_workout(chat_users)
        
        if group_workout:
            if len(group_workout) > MAX_MESSAGE_LENGTH:
                parts = [group_workout[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(group_workout), MAX_MESSAGE_LENGTH)]
                for i, part in enumerate(parts):
                    await update.message.reply_text(f"👥 <b>Групповая тренировка (часть {i+1}/{len(parts)})</b>\n\n{part}", parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text(f"👥 <b>Групповая тренировка для всех:</b>\n\n{group_workout}", parse_mode=ParseMode.HTML)
            
            # Сохраняем групповую тренировку для каждого участника
            workout_data = {
                "type": "group",
                "participants": len(chat_users),
                "generated_at": datetime.now().isoformat(),
                "chat_id": chat.id
            }
            
            for user in chat_users:
                self.db.save_workout(user['user_id'], "group", workout_data)
                
        else:
            await update.message.reply_text("❌ Не удалось сгенерировать групповую тренировку. Попробуй позже.")
    
    async def progress_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /progress"""
        user = update.effective_user
        user_info = self.db.get_user_info(user.id)
        
        if not user_info:
            await update.message.reply_text("❌ Сначала настрой профиль командой /profile")
            return
        
        # Получаем тренировки пользователя
        workouts = self.db.get_user_workouts(user.id, limit=5)
        
        if workouts:
            progress_text = f"📊 <b>Прогресс {user.first_name}</b>\n\n"
            progress_text += "Последние тренировки:\n"
            
            for workout in workouts:
                status = "✅" if workout['completed'] else "⏳"
                date = workout.get('scheduled_date', 'Не указана')
                progress_text += f"{status} {workout['type']} - {date}\n"
            
            # Анализируем прогресс через ИИ
            progress_analysis = await self.ai_client.analyze_progress(user_info, workouts)
            if progress_analysis:
                progress_text += f"\n<b>Анализ тренера:</b>\n{progress_analysis}"
            
        else:
            progress_text = f"📊 <b>Прогресс {user.first_name}</b>\n\n"
            progress_text += "У тебя пока нет тренировок. Начни с команды /workout!"
        
        await update.message.reply_text(progress_text, parse_mode=ParseMode.HTML)
    
    async def motivation_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /motivation"""
        user = update.effective_user
        user_info = self.db.get_user_info(user.id)
        
        if not user_info:
            await update.message.reply_text("❌ Сначала настрой профиль командой /profile")
            return
        
        # Генерируем мотивирующее сообщение
        motivational_message = await self.ai_client.generate_motivational_message(
            user_info, 
            context="morning_motivation"
        )
        
        if motivational_message:
            await update.message.reply_text(f"🔥 <b>Мотивация для {user.first_name}:</b>\n\n{motivational_message}", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("❌ Не удалось сгенерировать мотивацию. Попробуй позже.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик обычных сообщений"""
        user = update.effective_user
        chat = update.effective_chat
        message_text = update.message.text
        
        # Сохраняем сообщение в базе
        self.db.save_message(chat.id, user.id, message_text)
        
        # Получаем историю чата для контекста
        chat_history = self.db.get_chat_history(chat.id, limit=20)
        chat_users = self.db.get_chat_users(chat.id)
        
        # Формируем контекст для ИИ
        chat_context = {
            'users': chat_users,
            'chat_type': chat.type,
            'chat_title': chat.title
        }
        
        # Форматируем историю для API
        formatted_messages = self.ai_client.format_chat_history(chat_history)
        
        # Добавляем текущее сообщение
        formatted_messages.append({
            "role": "user",
            "content": f"{user.first_name}: {message_text}"
        })
        
        # Получаем ответ от ИИ
        ai_response = await self.ai_client.get_response(formatted_messages, chat_context)
        
        if ai_response:
            # Сохраняем ответ бота в историю
            self.db.save_message(chat.id, 0, ai_response)  # user_id = 0 для бота
            
            # Отправляем ответ
            if len(ai_response) > MAX_MESSAGE_LENGTH:
                parts = [ai_response[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(ai_response), MAX_MESSAGE_LENGTH)]
                for i, part in enumerate(parts):
                    await update.message.reply_text(f"💬 <b>Ответ тренера (часть {i+1}/{len(parts)})</b>\n\n{part}", parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text(f"💬 <b>Ответ тренера:</b>\n\n{ai_response}", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("❌ Извини, не могу сейчас ответить. Попробуй позже.")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback кнопок"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("level_"):
            level = data.replace("level_", "")
            user = update.effective_user
            
            # Обновляем уровень пользователя
            self.db.update_user_fitness_info(user.id, fitness_level=level)
            
            level_names = {
                "beginner": "начинающий",
                "intermediate": "средний", 
                "advanced": "продвинутый"
            }
            
            await query.edit_message_text(
                f"✅ Уровень {user.first_name} обновлен на: <b>{level_names.get(level, level)}</b>\n\n"
                f"Теперь можешь получить план тренировки командой /workout!",
                parse_mode=ParseMode.HTML
            )
            
        elif data == "profile":
            await self.profile_command(update, context)
            
        elif data == "workout":
            await self.workout_command(update, context)
            
        elif data == "group_workout":
            await self.group_workout_command(update, context)
            
        elif data == "progress":
            await self.progress_command(update, context)
            
        elif data == "motivation":
            await self.motivation_command(update, context)
    
    def run(self):
        """Запуск бота"""
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("profile", self.profile_command))
        application.add_handler(CommandHandler("workout", self.workout_command))
        application.add_handler(CommandHandler("group_workout", self.group_workout_command))
        application.add_handler(CommandHandler("progress", self.progress_command))
        application.add_handler(CommandHandler("motivation", self.motivation_command))
        
        # Добавляем обработчики сообщений и callback
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Запускаем бота
        logger.info("Бот запущен!")
        application.run_polling()

if __name__ == "__main__":
    bot = FitnessTrainerBot()
    bot.run()
