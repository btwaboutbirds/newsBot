"""
Модуль работы с базой данных NewsBot.
Содержит модели данных и управление SQLite БД.
"""

from .db_manager import DatabaseManager
from .models import News, User

__all__ = ['DatabaseManager', 'News', 'User']

