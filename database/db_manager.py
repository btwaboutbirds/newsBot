"""
Управление базой данных SQLite для NewsBot.
Содержит методы для работы с новостями и пользователями.
"""

import sqlite3
from typing import List, Optional
from datetime import datetime, timedelta
from contextlib import contextmanager

from .models import News, User
from config.settings import DATABASE_PATH
from utils.logger import setup_logger


logger = setup_logger(__name__)


class DatabaseManager:
    """Менеджер для работы с SQLite базой данных."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """
        Инициализация менеджера БД.
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """
        Контекстный менеджер для работы с соединением к БД.
        
        Yields:
            Соединение с БД
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Ошибка при работе с БД: {e}")
            raise
        finally:
            conn.close()
    
    def init_database(self) -> None:
        """Создание таблиц в базе данных, если они не существуют."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица новостей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL UNIQUE,
                    link TEXT NOT NULL UNIQUE,
                    description TEXT,
                    source TEXT NOT NULL,
                    published_at DATETIME NOT NULL,
                    parsed_at DATETIME NOT NULL,
                    language TEXT NOT NULL,
                    rating REAL DEFAULT 0.0,
                    content_hash TEXT UNIQUE
                )
            """)
            
            # Таблица пользователей (для будущего расширения)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    created_at DATETIME NOT NULL,
                    settings TEXT
                )
            """)
            
            # Индексы для оптимизации запросов
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_news_published_at 
                ON news(published_at DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_news_rating 
                ON news(rating DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_news_content_hash 
                ON news(content_hash)
            """)
            
            logger.info("База данных инициализирована")
    
    def add_news(self, news: News) -> Optional[int]:
        """
        Добавление новости в БД с проверкой уникальности.
        
        Args:
            news: Объект новости
        
        Returns:
            ID добавленной новости или None, если новость уже существует
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO news 
                    (title, link, description, source, published_at, parsed_at, 
                     language, rating, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    news.title,
                    news.link,
                    news.description,
                    news.source,
                    news.published_at,
                    news.parsed_at,
                    news.language,
                    news.rating,
                    news.content_hash
                ))
                
                news_id = cursor.lastrowid
                logger.info(f"Новость добавлена: {news.title[:50]}... (ID: {news_id})")
                return news_id
                
        except sqlite3.IntegrityError:
            logger.debug(f"Новость уже существует: {news.title[:50]}...")
            return None
    
    def get_news_by_period(self, hours: int = 24, limit: Optional[int] = None) -> List[News]:
        """
        Получение новостей за указанный период.
        
        Args:
            hours: Количество часов для выборки
            limit: Максимальное количество новостей
        
        Returns:
            Список новостей
        """
        time_threshold = datetime.now() - timedelta(hours=hours)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM news 
                WHERE published_at >= ? 
                ORDER BY rating DESC, published_at DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (time_threshold,))
            rows = cursor.fetchall()
            
            return [self._row_to_news(row) for row in rows]
    
    def get_top_news(self, limit: int = 4) -> List[News]:
        """
        Получение топ новостей по рейтингу.
        
        Args:
            limit: Количество новостей
        
        Returns:
            Список топ новостей
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM news 
                ORDER BY rating DESC, published_at DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [self._row_to_news(row) for row in rows]
    
    def check_news_exists(self, content_hash: str) -> bool:
        """
        Проверка существования новости по хешу.
        
        Args:
            content_hash: Хеш контента
        
        Returns:
            True, если новость существует
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT 1 FROM news WHERE content_hash = ? LIMIT 1",
                (content_hash,)
            )
            
            return cursor.fetchone() is not None
    
    def _row_to_news(self, row: sqlite3.Row) -> News:
        """
        Конвертация строки БД в объект News.
        
        Args:
            row: Строка из БД
        
        Returns:
            Объект News
        """
        return News(
            id=row['id'],
            title=row['title'],
            link=row['link'],
            description=row['description'],
            source=row['source'],
            published_at=datetime.fromisoformat(row['published_at']),
            parsed_at=datetime.fromisoformat(row['parsed_at']),
            language=row['language'],
            rating=row['rating'],
            content_hash=row['content_hash']
        )
    
    def add_user(self, user: User) -> Optional[int]:
        """
        Добавление пользователя в БД.
        
        Args:
            user: Объект пользователя
        
        Returns:
            ID добавленного пользователя или None при ошибке
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO users (telegram_id, username, created_at, settings)
                    VALUES (?, ?, ?, ?)
                """, (
                    user.telegram_id,
                    user.username,
                    user.created_at,
                    user.settings
                ))
                
                user_id = cursor.lastrowid
                logger.info(f"Пользователь добавлен: {user.telegram_id}")
                return user_id
                
        except sqlite3.IntegrityError:
            logger.debug(f"Пользователь уже существует: {user.telegram_id}")
            return None
    
    def clear_all_news(self) -> int:
        """
        Удаление всех новостей из базы данных.
        
        Returns:
            Количество удаленных новостей
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Получаем количество записей перед удалением
            cursor.execute("SELECT COUNT(*) FROM news")
            count = cursor.fetchone()[0]
            
            # Удаляем все новости
            cursor.execute("DELETE FROM news")
            
            logger.info(f"Удалено {count} новостей из базы данных")
            return count

