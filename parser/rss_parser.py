"""
Парсер RSS-лент для NewsBot.
Асинхронный парсинг новостей из RSS источников.
"""

import feedparser
import aiohttp
from typing import List, Dict, Any
from datetime import datetime
from dateutil import parser as date_parser
import asyncio

from config.settings import REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY
from config.sources import RSS_SOURCES
from database.models import News
from utils.logger import setup_logger
from utils.formatter import strip_html_tags


logger = setup_logger(__name__)


class RSSParser:
    """Парсер для RSS-лент."""
    
    def __init__(self):
        """Инициализация парсера."""
        self.sources = RSS_SOURCES
        self.timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    
    async def fetch_feed(self, url: str, session: aiohttp.ClientSession) -> str:
        """
        Асинхронное получение RSS-ленты.
        
        Args:
            url: URL RSS-ленты
            session: Сессия aiohttp
        
        Returns:
            Содержимое ленты в виде строки
        """
        for attempt in range(MAX_RETRIES):
            try:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"Статус {response.status} для {url}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Таймаут при запросе {url}, попытка {attempt + 1}/{MAX_RETRIES}")
                
            except Exception as e:
                logger.error(f"Ошибка при запросе {url}: {e}, попытка {attempt + 1}/{MAX_RETRIES}")
            
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
        
        return ""
    
    def parse_feed_content(self, content: str, source: Dict[str, Any]) -> List[News]:
        """
        Парсинг содержимого RSS-ленты.
        
        Args:
            content: Содержимое ленты
            source: Информация об источнике
        
        Returns:
            Список объектов News
        """
        feed = feedparser.parse(content)
        news_list = []
        
        for entry in feed.entries:
            try:
                # Извлечение данных
                title = entry.get('title', 'Без заголовка')
                link = entry.get('link', '')
                description = entry.get('summary', entry.get('description', ''))
                
                # Очистка от HTML-тегов
                title = strip_html_tags(title)
                description = strip_html_tags(description)
                
                # Парсинг даты публикации
                published_at = self._parse_date(entry)
                
                # Создание объекта новости
                news = News(
                    title=title,
                    link=link,
                    description=description,
                    source=source['name'],
                    published_at=published_at,
                    language=source['language'],
                    rating=0.0  # Рейтинг будет рассчитан позже
                )
                
                news_list.append(news)
                
            except Exception as e:
                logger.error(f"Ошибка при парсинге записи из {source['name']}: {e}")
                continue
        
        logger.info(f"Спарсено {len(news_list)} новостей из {source['name']}")
        return news_list
    
    def _parse_date(self, entry: Dict[str, Any]) -> datetime:
        """
        Парсинг даты публикации из RSS записи.
        
        Args:
            entry: Запись из RSS
        
        Returns:
            Объект datetime
        """
        # Пробуем различные поля с датой
        date_fields = ['published', 'updated', 'created']
        
        for field in date_fields:
            date_str = entry.get(field)
            if date_str:
                try:
                    return date_parser.parse(date_str)
                except Exception:
                    continue
        
        # Если дата не найдена, используем текущее время
        logger.warning(f"Не удалось распарсить дату для: {entry.get('title', 'unknown')}")
        return datetime.now()
    
    async def parse_all_sources(self) -> List[News]:
        """
        Асинхронный парсинг всех RSS источников.
        
        Returns:
            Список всех спарсенных новостей
        """
        all_news = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for source in self.sources:
                task = self._parse_source(source, session)
                tasks.append(task)
            
            # Параллельный парсинг всех источников
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_news.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Ошибка при парсинге источника: {result}")
        
        logger.info(f"Всего спарсено {len(all_news)} новостей из {len(self.sources)} источников")
        return all_news
    
    async def _parse_source(self, source: Dict[str, Any], session: aiohttp.ClientSession) -> List[News]:
        """
        Парсинг одного источника.
        
        Args:
            source: Информация об источнике
            session: Сессия aiohttp
        
        Returns:
            Список новостей из источника
        """
        logger.info(f"Парсинг источника: {source['name']}")
        
        content = await self.fetch_feed(source['url'], session)
        
        if not content:
            logger.warning(f"Не удалось получить контент из {source['name']}")
            return []
        
        return self.parse_feed_content(content, source)

