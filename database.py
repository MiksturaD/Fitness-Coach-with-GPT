import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class FitnessDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        fitness_level TEXT DEFAULT 'beginner',
                        goals TEXT DEFAULT 'general_fitness',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица чатов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chats (
                        chat_id INTEGER PRIMARY KEY,
                        chat_type TEXT,
                        chat_title TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица истории сообщений
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS message_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER,
                        user_id INTEGER,
                        message_text TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (chat_id) REFERENCES chats (chat_id),
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Таблица тренировок
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS workouts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        workout_type TEXT,
                        workout_data TEXT,
                        completed BOOLEAN DEFAULT FALSE,
                        scheduled_date DATE,
                        completed_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Таблица прогресса
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS progress (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        metric_name TEXT,
                        metric_value REAL,
                        date DATE,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logger.info("База данных инициализирована успешно")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Добавление нового пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
                logger.info(f"Пользователь {user_id} добавлен/обновлен")
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя: {e}")
    
    def add_chat(self, chat_id: int, chat_type: str, chat_title: str = None):
        """Добавление нового чата"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO chats (chat_id, chat_type, chat_title)
                    VALUES (?, ?, ?)
                ''', (chat_id, chat_type, chat_title))
                conn.commit()
                logger.info(f"Чат {chat_id} добавлен/обновлен")
        except Exception as e:
            logger.error(f"Ошибка добавления чата: {e}")
    
    def save_message(self, chat_id: int, user_id: int, message_text: str):
        """Сохранение сообщения в историю"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO message_history (chat_id, user_id, message_text)
                    VALUES (?, ?, ?)
                ''', (chat_id, user_id, message_text))
                conn.commit()
                
                # Обновляем время последней активности пользователя
                cursor.execute('''
                    UPDATE users SET last_activity = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Ошибка сохранения сообщения: {e}")
    
    def get_chat_history(self, chat_id: int, limit: int = 50) -> List[Dict]:
        """Получение истории чата"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT mh.user_id, mh.message_text, mh.timestamp, u.first_name, u.username
                    FROM message_history mh
                    JOIN users u ON mh.user_id = u.user_id
                    WHERE mh.chat_id = ?
                    ORDER BY mh.timestamp DESC
                    LIMIT ?
                ''', (chat_id, limit))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'user_id': row[0],
                        'message': row[1],
                        'timestamp': row[2],
                        'first_name': row[3],
                        'username': row[4]
                    })
                
                return history[::-1]  # Возвращаем в хронологическом порядке
                
        except Exception as e:
            logger.error(f"Ошибка получения истории чата: {e}")
            return []
    
    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Получение информации о пользователе"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, username, first_name, last_name, fitness_level, goals
                    FROM users WHERE user_id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'user_id': row[0],
                        'username': row[1],
                        'first_name': row[2],
                        'last_name': row[3],
                        'fitness_level': row[4],
                        'goals': row[5]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения информации о пользователе: {e}")
            return None
    
    def update_user_fitness_info(self, user_id: int, fitness_level: str = None, goals: str = None):
        """Обновление фитнес-информации пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if fitness_level and goals:
                    cursor.execute('''
                        UPDATE users SET fitness_level = ?, goals = ?
                        WHERE user_id = ?
                    ''', (fitness_level, goals, user_id))
                elif fitness_level:
                    cursor.execute('''
                        UPDATE users SET fitness_level = ?
                        WHERE user_id = ?
                    ''', (fitness_level, user_id))
                elif goals:
                    cursor.execute('''
                        UPDATE users SET goals = ?
                        WHERE user_id = ?
                    ''', (goals, user_id))
                
                conn.commit()
                logger.info(f"Информация пользователя {user_id} обновлена")
                
        except Exception as e:
            logger.error(f"Ошибка обновления информации пользователя: {e}")
    
    def save_workout(self, user_id: int, workout_type: str, workout_data: Dict, scheduled_date: str = None):
        """Сохранение тренировки"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO workouts (user_id, workout_type, workout_data, scheduled_date)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, workout_type, json.dumps(workout_data), scheduled_date))
                conn.commit()
                logger.info(f"Тренировка для пользователя {user_id} сохранена")
                
        except Exception as e:
            logger.error(f"Ошибка сохранения тренировки: {e}")
    
    def save_progress(self, user_id: int, metric_name: str, metric_value: float, date: str, notes: str = None):
        """Сохранение прогресса пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO progress (user_id, metric_name, metric_value, date, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, metric_name, metric_value, date, notes))
                conn.commit()
                logger.info(f"Прогресс пользователя {user_id} сохранен")
                
        except Exception as e:
            logger.error(f"Ошибка сохранения прогресса: {e}")
    
    def get_user_workouts(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Получение тренировок пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT workout_type, workout_data, completed, scheduled_date, completed_date
                    FROM workouts 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (user_id, limit))
                
                workouts = []
                for row in cursor.fetchall():
                    workouts.append({
                        'type': row[0],
                        'data': json.loads(row[1]),
                        'completed': bool(row[2]),
                        'scheduled_date': row[3],
                        'completed_date': row[4]
                    })
                
                return workouts
                
        except Exception as e:
            logger.error(f"Ошибка получения тренировок: {e}")
            return []
    
    def get_chat_users(self, chat_id: int) -> List[Dict]:
        """Получение списка пользователей в чате"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT DISTINCT u.user_id, u.first_name, u.username, u.fitness_level
                    FROM users u
                    JOIN message_history mh ON u.user_id = mh.user_id
                    WHERE mh.chat_id = ?
                ''', (chat_id,))
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'user_id': row[0],
                        'first_name': row[1],
                        'username': row[2],
                        'fitness_level': row[3]
                    })
                
                return users
                
        except Exception as e:
            logger.error(f"Ошибка получения пользователей чата: {e}")
            return []
