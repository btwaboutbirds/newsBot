"""
Модели данных для NewsBot.
Определяет структуру данных для новостей и пользователей.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import hashlib


@dataclass
class News:
    """
    Модель новости.
    
    Attributes:
        id: Уникальный идентификатор
        title: Заголовок новости
        link: Ссылка на статью
        description: Описание/анонс
        source: Источник RSS
        published_at: Время публикации
        parsed_at: Время парсинга
        language: Язык (en/ru)
        rating: Рейтинг новости (0.0-10.0)
        content_hash: Хеш для проверки уникальности
    """
    title: str
    link: str
    description: str
    source: str
    published_at: datetime
    language: str
    rating: float = 0.0
    parsed_at: Optional[datetime] = None
    content_hash: Optional[str] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Автоматическое вычисление хеша и времени парсинга."""
        if self.parsed_at is None:
            self.parsed_at = datetime.now()
        
        if self.content_hash is None:
            self.content_hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """
        Вычисление хеша контента для проверки уникальности.
        
        Returns:
            SHA256 хеш контента
        """
        content = f"{self.title}{self.link}{self.description}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def to_dict(self) -> dict:
        """
        Конвертация в словарь.
        
        Returns:
            Словарь с данными новости
        """
        return {
            'id': self.id,
            'title': self.title,
            'link': self.link,
            'description': self.description,
            'source': self.source,
            'published_at': self.published_at.isoformat() if isinstance(self.published_at, datetime) else self.published_at,
            'parsed_at': self.parsed_at.isoformat() if isinstance(self.parsed_at, datetime) else self.parsed_at,
            'language': self.language,
            'rating': self.rating,
            'content_hash': self.content_hash
        }


@dataclass
class User:
    """
    Модель пользователя (для будущего расширения).
    
    Attributes:
        telegram_id: ID пользователя в Telegram
        username: Имя пользователя
        created_at: Дата регистрации
        settings: JSON с настройками пользователя
        id: Уникальный идентификатор в БД
    """
    telegram_id: int
    username: Optional[str] = None
    created_at: Optional[datetime] = None
    settings: Optional[str] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Установка даты создания по умолчанию."""
        if self.created_at is None:
            self.created_at = datetime.now()

