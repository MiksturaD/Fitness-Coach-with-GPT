"""
Дополнительные утилиты для спортивного тренера
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def format_workout_schedule(workouts: List[Dict]) -> str:
    """
    Форматирование расписания тренировок
    
    Args:
        workouts: Список тренировок
        
    Returns:
        Отформатированное расписание
    """
    if not workouts:
        return "📅 У вас пока нет запланированных тренировок"
    
    schedule = "📅 <b>Расписание тренировок:</b>\n\n"
    
    for i, workout in enumerate(workouts, 1):
        status = "✅" if workout.get('completed') else "⏳"
        workout_type = workout.get('type', 'Неизвестно')
        date = workout.get('scheduled_date', 'Не указана')
        
        schedule += f"{i}. {status} {workout_type} - {date}\n"
    
    return schedule

def calculate_weekly_stats(workouts: List[Dict]) -> Dict:
    """
    Расчет недельной статистики тренировок
    
    Args:
        workouts: Список тренировок за неделю
        
    Returns:
        Статистика тренировок
    """
    if not workouts:
        return {
            'total_workouts': 0,
            'completed_workouts': 0,
            'completion_rate': 0,
            'workout_types': {}
        }
    
    total = len(workouts)
    completed = sum(1 for w in workouts if w.get('completed', False))
    completion_rate = (completed / total) * 100 if total > 0 else 0
    
    # Подсчет типов тренировок
    workout_types = {}
    for workout in workouts:
        workout_type = workout.get('type', 'Неизвестно')
        workout_types[workout_type] = workout_types.get(workout_type, 0) + 1
    
    return {
        'total_workouts': total,
        'completed_workouts': completed,
        'completion_rate': round(completion_rate, 1),
        'workout_types': workout_types
    }

def format_progress_summary(progress_data: List[Dict]) -> str:
    """
    Форматирование сводки прогресса
    
    Args:
        progress_data: Данные о прогрессе
        
    Returns:
        Отформатированная сводка
    """
    if not progress_data:
        return "📊 У вас пока нет данных о прогрессе"
    
    summary = "📊 <b>Сводка прогресса:</b>\n\n"
    
    # Группируем по метрикам
    metrics = {}
    for item in progress_data:
        metric_name = item.get('metric_name', 'Неизвестно')
        if metric_name not in metrics:
            metrics[metric_name] = []
        metrics[metric_name].append(item)
    
    for metric_name, items in metrics.items():
        summary += f"<b>{metric_name}:</b>\n"
        
        # Показываем последние 3 значения
        recent_items = sorted(items, key=lambda x: x.get('date', ''), reverse=True)[:3]
        
        for item in recent_items:
            value = item.get('metric_value', 'N/A')
            date = item.get('date', 'Не указана')
            notes = item.get('notes', '')
            
            summary += f"  • {value} ({date})"
            if notes:
                summary += f" - {notes}"
            summary += "\n"
        
        summary += "\n"
    
    return summary

def generate_motivational_quote() -> str:
    """
    Генерация случайной мотивационной цитаты
    
    Returns:
        Мотивационная цитата
    """
    quotes = [
        "💪 Каждая тренировка - это шаг к лучшей версии себя",
        "🔥 Сила не в том, чтобы никогда не падать, а в том, чтобы всегда подниматься",
        "🏃‍♂️ Движение - это жизнь, а жизнь - это движение",
        "🌟 Ты сильнее, чем думаешь, и способнее, чем можешь представить",
        "🎯 Цель без плана - это просто желание",
        "💎 Алмаз создается под давлением, а чемпион - в тренировках",
        "🚀 Сегодняшние усилия - это завтрашние результаты",
        "🌈 После каждой бури приходит радуга, после каждой тренировки - сила",
        "⚡ Энергия и настойчивость побеждают все",
        "🎪 Жизнь - это не спринт, а марафон. Тренируйся соответственно"
    ]
    
    import random
    return random.choice(quotes)

def format_user_profile(user_info: Dict) -> str:
    """
    Форматирование профиля пользователя
    
    Args:
        user_info: Информация о пользователе
        
    Returns:
        Отформатированный профиль
    """
    profile = f"👤 <b>Профиль {user_info.get('first_name', 'Пользователь')}</b>\n\n"
    
    # Уровень подготовки
    fitness_level = user_info.get('fitness_level', 'Не указан')
    level_emoji = {
        'beginner': '🟢',
        'intermediate': '🟡', 
        'advanced': '🔴'
    }
    level_name = {
        'beginner': 'Начинающий',
        'intermediate': 'Средний',
        'advanced': 'Продвинутый'
    }
    
    emoji = level_emoji.get(fitness_level, '⚪')
    level = level_name.get(fitness_level, fitness_level)
    
    profile += f"📊 <b>Уровень подготовки:</b> {emoji} {level}\n"
    
    # Цели
    goals = user_info.get('goals', 'Не указаны')
    profile += f"🎯 <b>Цели:</b> {goals}\n"
    
    # Дата регистрации
    created_at = user_info.get('created_at', 'Неизвестно')
    if created_at and created_at != 'Неизвестно':
        try:
            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_ago = (datetime.now() - date_obj).days
            profile += f"📅 <b>В системе:</b> {days_ago} дней\n"
        except:
            profile += f"📅 <b>Дата регистрации:</b> {created_at}\n"
    
    return profile

def suggest_next_workout(user_info: Dict, last_workout: Optional[Dict] = None) -> str:
    """
    Предложение следующей тренировки
    
    Args:
        user_info: Информация о пользователе
        last_workout: Последняя тренировка
        
    Returns:
        Предложение тренировки
    """
    level = user_info.get('fitness_level', 'beginner')
    
    suggestions = {
        'beginner': [
            "🚶‍♂️ Прогулка 30 минут + легкая разминка",
            "🧘‍♀️ Йога для начинающих 20 минут",
            "💪 Базовые отжимания от стены 3x5",
            "🏃‍♂️ Интервальная ходьба 20 минут"
        ],
        'intermediate': [
            "🏋️‍♂️ Круговая тренировка 45 минут",
            "🚴‍♂️ Велотренажер 30 минут + силовые",
            "🏃‍♂️ Бег 5км + растяжка",
            "💪 Комплекс упражнений с гантелями"
        ],
        'advanced': [
            "🔥 HIIT тренировка 40 минут",
            "🏋️‍♂️ Силовая тренировка 60 минут",
            "🏃‍♂️ Бег 10км + скоростные интервалы",
            "💪 Кроссфит комплекс"
        ]
    }
    
    import random
    suggestion = random.choice(suggestions.get(level, suggestions['beginner']))
    
    if last_workout:
        last_type = last_workout.get('type', '')
        if 'cardio' in last_type.lower() or 'бег' in last_type.lower():
            suggestion = "💪 Силовая тренировка (чередуем с кардио)"
        elif 'силовая' in last_type.lower() or 'strength' in last_type.lower():
            suggestion = "🏃‍♂️ Кардио тренировка (чередуем с силовой)"
    
    return f"💡 <b>Предложение на сегодня:</b>\n{suggestion}"

def format_group_workout_summary(users: List[Dict], workout_type: str = "group") -> str:
    """
    Форматирование сводки групповой тренировки
    
    Args:
        users: Список участников
        workout_type: Тип тренировки
        
    Returns:
        Отформатированная сводка
    """
    if not users:
        return "👥 Нет участников для групповой тренировки"
    
    summary = f"👥 <b>Групповая тренировка: {workout_type}</b>\n\n"
    summary += f"📊 <b>Участники ({len(users)}):</b>\n"
    
    # Группируем по уровню подготовки
    levels = {}
    for user in users:
        level = user.get('fitness_level', 'beginner')
        if level not in levels:
            levels[level] = []
        levels[level].append(user.get('first_name', 'Пользователь'))
    
    level_names = {
        'beginner': '🟢 Начинающие',
        'intermediate': '🟡 Средний уровень',
        'advanced': '🔴 Продвинутые'
    }
    
    for level, names in levels.items():
        emoji_name = level_names.get(level, level)
        summary += f"{emoji_name}: {', '.join(names)}\n"
    
    summary += f"\n🎯 <b>Рекомендации:</b>\n"
    
    if len(users) == 2:
        summary += "• Идеально для парных упражнений\n"
        summary += "• Взаимная поддержка и мотивация\n"
        summary += "• Можно соревноваться друг с другом\n"
    elif len(users) <= 4:
        summary += "• Отличный размер для круговых тренировок\n"
        summary += "• Возможность ротации упражнений\n"
        summary += "• Групповая динамика и веселье\n"
    else:
        summary += "• Разделитесь на подгруппы по уровню\n"
        summary += "• Используйте станции для упражнений\n"
        summary += "• Организуйте командные соревнования\n"
    
    return summary
