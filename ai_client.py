import aiohttp
import json
import logging
from typing import Dict, List, Optional
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL, TRAINER_PERSONALITY

logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self, api_key: str, base_url: str = OPENROUTER_BASE_URL, model: str = OPENROUTER_MODEL):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_response(self, messages: List[Dict], chat_context: Dict = None) -> Optional[str]:
        """
        Получение ответа от ИИ через OpenRouter API
        
        Args:
            messages: Список сообщений в формате OpenAI
            chat_context: Контекст чата (пользователи, их уровень подготовки и т.д.)
        
        Returns:
            Ответ от ИИ или None в случае ошибки
        """
        try:
            # Формируем системное сообщение с контекстом
            system_message = TRAINER_PERSONALITY
            
            if chat_context:
                users_info = chat_context.get('users', [])
                if users_info:
                    system_message += "\n\nИнформация о пользователях в чате:\n"
                    for user in users_info:
                        name = user.get('first_name', 'Пользователь')
                        level = user.get('fitness_level', 'неизвестен')
                        system_message += f"- {name}: уровень подготовки - {level}\n"
                
                system_message += "\nПомни контекст разговора и используй имена пользователей!"
            
            # Формируем полный список сообщений
            full_messages = [{"role": "system", "content": system_message}] + messages
            
            payload = {
                "model": self.model,
                "messages": full_messages,
                "max_tokens": 1000,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        logger.info("Ответ от ИИ получен успешно")
                        return content
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка API: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Ошибка получения ответа от ИИ: {e}")
            return None
    
    def format_chat_history(self, history: List[Dict]) -> List[Dict]:
        """
        Форматирование истории чата для отправки в API
        
        Args:
            history: История сообщений из базы данных
        
        Returns:
            Отформатированные сообщения для API
        """
        formatted_messages = []
        
        for msg in history:
            role = "user"  # Все сообщения от пользователей
            content = f"{msg.get('first_name', 'Пользователь')}: {msg['message']}"
            
            formatted_messages.append({
                "role": role,
                "content": content
            })
        
        return formatted_messages
    
    async def generate_workout_plan(self, user_info: Dict, workout_type: str = "individual") -> Optional[str]:
        """
        Генерация плана тренировок для пользователя
        
        Args:
            user_info: Информация о пользователе
            workout_type: Тип тренировки (individual/group)
        
        Returns:
            План тренировки или None в случае ошибки
        """
        try:
            name = user_info.get('first_name', 'Пользователь')
            level = user_info.get('fitness_level', 'beginner')
            goals = user_info.get('goals', 'general_fitness')
            
            prompt = f"""
            Составь детальный план тренировки для {name}.
            
            Уровень подготовки: {level}
            Цели: {goals}
            Тип тренировки: {workout_type}
            
            Включи:
            - Разминку (5-10 минут)
            - Основную часть тренировки
            - Заминку (5-10 минут)
            - Рекомендации по технике
            - Продолжительность каждого упражнения
            - Количество подходов и повторений
            
            Будь мотивирующим и учитывай уровень подготовки!
            """
            
            messages = [{"role": "user", "content": prompt}]
            return await self.get_response(messages)
            
        except Exception as e:
            logger.error(f"Ошибка генерации плана тренировки: {e}")
            return None
    
    async def generate_group_workout(self, users: List[Dict], workout_type: str = "group") -> Optional[str]:
        """
        Генерация групповой тренировки для нескольких пользователей
        
        Args:
            users: Список пользователей
            workout_type: Тип групповой тренировки
        
        Returns:
            План групповой тренировки или None в случае ошибки
        """
        try:
            users_info = "\n".join([
                f"- {user.get('first_name', 'Пользователь')} (уровень: {user.get('fitness_level', 'неизвестен')})"
                for user in users
            ])
            
            prompt = f"""
            Составь план групповой тренировки для следующих пользователей:
            {users_info}
            
            Тип тренировки: {workout_type}
            
            Учти:
            - Разные уровни подготовки участников
            - Возможность адаптации упражнений
            - Взаимную поддержку и мотивацию
            - Веселую и дружескую атмосферу
            
            Включи:
            - Разминку для всех
            - Основные упражнения с вариантами сложности
            - Групповые элементы
            - Заминку
            - Рекомендации по взаимодействию
            
            Сделай тренировку интересной для всех участников!
            """
            
            messages = [{"role": "user", "content": prompt}]
            return await self.get_response(messages)
            
        except Exception as e:
            logger.error(f"Ошибка генерации групповой тренировки: {e}")
            return None
    
    async def generate_motivational_message(self, user_info: Dict, context: str = "general") -> Optional[str]:
        """
        Генерация мотивирующего сообщения
        
        Args:
            user_info: Информация о пользователе
            context: Контекст (после тренировки, утром, вечером и т.д.)
        
        Returns:
            Мотивирующее сообщение или None в случае ошибки
        """
        try:
            name = user_info.get('first_name', 'Пользователь')
            level = user_info.get('fitness_level', 'beginner')
            
            prompt = f"""
            Напиши мотивирующее сообщение для {name}.
            
            Контекст: {context}
            Уровень подготовки: {level}
            
            Сообщение должно быть:
            - Персонализированным для {name}
            - Мотивирующим и вдохновляющим
            - Соответствующим контексту
            - Дружелюбным и поддерживающим
            
            Используй имя пользователя и сделай сообщение личным!
            """
            
            messages = [{"role": "user", "content": prompt}]
            return await self.get_response(messages)
            
        except Exception as e:
            logger.error(f"Ошибка генерации мотивирующего сообщения: {e}")
            return None
    
    async def analyze_progress(self, user_info: Dict, progress_data: List[Dict]) -> Optional[str]:
        """
        Анализ прогресса пользователя
        
        Args:
            user_info: Информация о пользователе
            progress_data: Данные о прогрессе
        
        Returns:
            Анализ прогресса или None в случае ошибки
        """
        try:
            name = user_info.get('first_name', 'Пользователь')
            
            if not progress_data:
                prompt = f"""
                {name} еще не начал отслеживать свой прогресс.
                Напиши мотивирующее сообщение о важности отслеживания прогресса
                и предложи начать с простых метрик.
                """
            else:
                # Формируем краткую сводку прогресса
                progress_summary = "\n".join([
                    f"- {item.get('metric_name', 'Метрика')}: {item.get('metric_value', 'N/A')} ({item.get('date', 'дата')})"
                    for item in progress_data[-5:]  # Последние 5 записей
                ])
                
                prompt = f"""
                Проанализируй прогресс {name}:
                
                {progress_summary}
                
                Дай:
                - Оценку прогресса
                - Рекомендации по улучшению
                - Мотивирующие слова
                - Следующие шаги
                
                Будь поддерживающим и конструктивным!
                """
            
            messages = [{"role": "user", "content": prompt}]
            return await self.get_response(messages)
            
        except Exception as e:
            logger.error(f"Ошибка анализа прогресса: {e}")
            return None
