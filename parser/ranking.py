"""
Модуль ранжирования новостей для NewsBot.
Расчет рейтинга на основе различных критериев.
"""

from datetime import datetime, timedelta
from typing import List
import re

from database.models import News
from config.settings import (
    RELEVANCE_KEYWORDS,
    WEIGHT_FRESHNESS,
    WEIGHT_SOURCE,
    WEIGHT_KEYWORDS,
    WEIGHT_LENGTH,
    RATING_MIN,
    RATING_MAX
)
from config.sources import RSS_SOURCES
from utils.logger import setup_logger


logger = setup_logger(__name__)


class RankingEngine:
    """Движок для ранжирования новостей."""
    
    def __init__(self):
        """Инициализация движка ранжирования."""
        self.source_weights = {source['name']: source['weight'] for source in RSS_SOURCES}
    
    def calculate_rating(self, news: News, article_length: int = 0) -> float:
        """
        Расчет рейтинга новости.
        
        Args:
            news: Объект новости
            article_length: Длина статьи в словах (опционально)
        
        Returns:
            Рейтинг от 0.0 до 10.0
        """
        # Компоненты рейтинга
        freshness_score = self._calculate_freshness_score(news.published_at)
        source_score = self._calculate_source_score(news.source)
        keyword_score = self._calculate_keyword_score(news.title, news.description)
        length_score = self._calculate_length_score(article_length)
        
        # Взвешенная сумма
        total_score = (
            freshness_score * WEIGHT_FRESHNESS +
            source_score * WEIGHT_SOURCE +
            keyword_score * WEIGHT_KEYWORDS +
            length_score * WEIGHT_LENGTH
        )
        
        # Нормализация к диапазону RATING_MIN - RATING_MAX
        rating = max(RATING_MIN, min(RATING_MAX, total_score * RATING_MAX))
        
        logger.debug(f"Рейтинг для '{news.title[:30]}...': {rating:.2f} "
                    f"(свежесть={freshness_score:.2f}, источник={source_score:.2f}, "
                    f"ключевые слова={keyword_score:.2f}, длина={length_score:.2f})")
        
        return round(rating, 2)
    
    def _calculate_freshness_score(self, published_at: datetime) -> float:
        """
        Расчет оценки свежести новости.
        
        Args:
            published_at: Время публикации
        
        Returns:
            Оценка от 0.0 до 1.0
        """
        # Удаляем timezone info для совместимости
        if published_at.tzinfo is not None:
            published_at = published_at.replace(tzinfo=None)
        
        now = datetime.now()
        age = now - published_at
        
        # Чем свежее, тем выше оценка
        if age < timedelta(hours=1):
            return 1.0
        elif age < timedelta(hours=3):
            return 0.9
        elif age < timedelta(hours=6):
            return 0.7
        elif age < timedelta(hours=12):
            return 0.5
        elif age < timedelta(days=1):
            return 0.3
        else:
            return 0.1
    
    def _calculate_source_score(self, source: str) -> float:
        """
        Расчет оценки источника.
        
        Args:
            source: Название источника
        
        Returns:
            Оценка от 0.0 до 1.0
        """
        weight = self.source_weights.get(source, 5.0)
        # Нормализация веса (0-10) к диапазону 0-1
        return weight / 10.0
    
    def _calculate_keyword_score(self, title: str, description: str) -> float:
        """
        Расчет оценки на основе ключевых слов.
        
        Args:
            title: Заголовок новости
            description: Описание новости
        
        Returns:
            Оценка от 0.0 до 1.0
        """
        text = f"{title} {description}".lower()
        
        keyword_count = 0
        for keyword in RELEVANCE_KEYWORDS:
            # Используем регулярные выражения для поиска целых слов
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            matches = len(re.findall(pattern, text))
            keyword_count += matches
        
        # Нормализация: 5+ ключевых слов = максимальная оценка
        score = min(1.0, keyword_count / 5.0)
        
        return score
    
    def _calculate_length_score(self, article_length: int) -> float:
        """
        Расчет оценки на основе длины статьи.
        
        Args:
            article_length: Длина статьи в словах
        
        Returns:
            Оценка от 0.0 до 1.0
        """
        if article_length == 0:
            # Если длина неизвестна, даем среднюю оценку
            return 0.5
        
        # Оптимальная длина: 500-2000 слов
        if 500 <= article_length <= 2000:
            return 1.0
        elif 300 <= article_length < 500:
            return 0.8
        elif 2000 < article_length <= 3000:
            return 0.8
        elif 100 <= article_length < 300:
            return 0.5
        else:
            return 0.3
    
    def rank_news_list(self, news_list: List[News], article_lengths: dict = None) -> List[News]:
        """
        Ранжирование списка новостей.
        
        Args:
            news_list: Список новостей
            article_lengths: Словарь {link: length} с длинами статей
        
        Returns:
            Отсортированный список новостей с рассчитанными рейтингами
        """
        article_lengths = article_lengths or {}
        
        # Рассчитываем рейтинг для каждой новости
        for news in news_list:
            length = article_lengths.get(news.link, 0)
            news.rating = self.calculate_rating(news, length)
        
        # Сортируем по рейтингу (от большего к меньшему)
        ranked_news = sorted(news_list, key=lambda x: x.rating, reverse=True)
        
        logger.info(f"Ранжировано {len(ranked_news)} новостей")
        
        return ranked_news

