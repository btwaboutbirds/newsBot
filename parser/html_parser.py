"""
Парсер HTML для извлечения полного текста статей.
Используется для расширенного анализа контента новостей.
"""

import aiohttp
from bs4 import BeautifulSoup
from typing import Optional, Dict
import asyncio
import trafilatura

from config.settings import REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY
from utils.logger import setup_logger


logger = setup_logger(__name__)


class HTMLParser:
    """Парсер для извлечения текста из HTML статей."""
    
    def __init__(self):
        """Инициализация парсера."""
        self.timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
    
    async def fetch_article(self, url: str) -> Optional[str]:
        """
        Асинхронное получение HTML статьи.
        
        Args:
            url: URL статьи
        
        Returns:
            HTML контент или None при ошибке
        """
        for attempt in range(MAX_RETRIES):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.text()
                        else:
                            logger.warning(f"Статус {response.status} для {url}")
                            
            except asyncio.TimeoutError:
                logger.warning(f"Таймаут при запросе {url}, попытка {attempt + 1}/{MAX_RETRIES}")
                
            except Exception as e:
                logger.error(f"Ошибка при запросе {url}: {e}")
            
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
        
        return None
    
    def extract_text(self, html: str, url: str = "") -> str:
        """
        Извлечение чистого текста статьи из HTML с использованием trafilatura.
        
        Args:
            html: HTML контент
            url: URL статьи (опционально, для улучшения качества извлечения)
        
        Returns:
            Извлеченный чистый текст статьи
        """
        try:
            # Используем trafilatura для извлечения основного контента
            # include_comments=False - не включать комментарии
            # include_tables=False - не включать таблицы
            # no_fallback=False - использовать fallback если основной метод не сработал
            text = trafilatura.extract(
                html,
                url=url,
                include_comments=False,
                include_tables=False,
                no_fallback=False,
                favor_precision=True  # Приоритет точности над полнотой
            )
            
            if text:
                # Очистка от лишних пробелов и переносов строк
                text = ' '.join(text.split())
                return text
            
            # Fallback на BeautifulSoup если trafilatura не смог извлечь текст
            logger.warning(f"Trafilatura не смог извлечь текст, используем BeautifulSoup fallback")
            return self._extract_text_fallback(html)
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста через trafilatura: {e}")
            return self._extract_text_fallback(html)
    
    def _extract_text_fallback(self, html: str) -> str:
        """
        Запасной метод извлечения текста через BeautifulSoup.
        
        Args:
            html: HTML контент
        
        Returns:
            Извлеченный текст
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Удаляем ненужные элементы
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 
                                'aside', 'iframe', 'noscript', 'form']):
                element.decompose()
            
            # Пытаемся найти основной контент по распространенным классам/тегам
            main_content = (
                soup.find('article') or 
                soup.find('main') or 
                soup.find('div', class_=['content', 'article', 'post', 'entry-content']) or
                soup.find('div', id=['content', 'article', 'post'])
            )
            
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                # Если не нашли основной контент, берем весь body
                text = soup.get_text(separator=' ', strip=True)
            
            # Очистка от лишних пробелов
            text = ' '.join(text.split())
            
            return text
            
        except Exception as e:
            logger.error(f"Ошибка при fallback извлечении текста: {e}")
            return ""
    
    async def get_article_text(self, url: str) -> Optional[str]:
        """
        Получение и извлечение текста статьи.
        
        Args:
            url: URL статьи
        
        Returns:
            Текст статьи или None при ошибке
        """
        html = await self.fetch_article(url)
        
        if html:
            return self.extract_text(html, url)
        
        return None
    
    async def get_article_metadata(self, url: str) -> Optional[Dict[str, str]]:
        """
        Получение метаданных и текста статьи.
        
        Args:
            url: URL статьи
        
        Returns:
            Словарь с метаданными (title, author, date, text) или None при ошибке
        """
        html = await self.fetch_article(url)
        
        if not html:
            return None
        
        try:
            # Извлекаем метаданные через trafilatura
            metadata = trafilatura.extract_metadata(html, url=url)
            text = self.extract_text(html, url)
            
            result = {
                'text': text or '',
                'title': metadata.title if metadata else '',
                'author': metadata.author if metadata else '',
                'date': metadata.date if metadata else '',
                'description': metadata.description if metadata else ''
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении метаданных для {url}: {e}")
            return None
    
    def calculate_article_length(self, text: str) -> int:
        """
        Подсчет длины статьи в словах.
        
        Args:
            text: Текст статьи
        
        Returns:
            Количество слов
        """
        return len(text.split())

