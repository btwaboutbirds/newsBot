"""
Модуль расписания рассылки для NewsBot.
Содержит логику автоматической рассылки новостей (для будущего расширения).
"""

import asyncio
from datetime import datetime, time, timedelta
from typing import Optional

from aiogram import Bot
from aiogram.types import Message

from config.settings import (
    SCHEDULE_INTERVALS,
    DEFAULT_SCHEDULE_MODE,
    DEFAULT_INTERVAL,
    DAILY_SEND_TIME,
    TOP_NEWS_COUNT
)
from database.db_manager import DatabaseManager
from parser.rss_parser import RSSParser
from parser.ranking import RankingEngine
from bot.channel_poster import ChannelPoster
from utils.formatter import format_digest_message
from utils.logger import setup_logger


logger = setup_logger(__name__)


class NewsScheduler:
    """
    Планировщик автоматической рассылки новостей.
    
    Примечание: В MVP используется только ручная рассылка.
    Этот класс подготовлен для будущего расширения.
    """
    
    def __init__(self, bot: Bot):
        """
        Инициализация планировщика.
        
        Args:
            bot: Экземпляр бота aiogram
        """
        self.bot = bot
        self.db_manager = DatabaseManager()
        self.rss_parser = RSSParser()
        self.ranking_engine = RankingEngine()
        self.channel_poster = ChannelPoster(bot)
        self.is_running = False
        self.mode = DEFAULT_SCHEDULE_MODE
        self.interval = DEFAULT_INTERVAL
        
        logger.info(f"Планировщик инициализирован (режим: {self.mode})")
    
    async def start(self):
        """Запуск планировщика (если режим 'auto')."""
        if self.mode == 'manual':
            logger.info("Планировщик в режиме 'manual', автоматическая рассылка отключена")
            return
        
        self.is_running = True
        logger.info("Планировщик запущен")
        
        if self.interval == 'daily':
            await self._run_daily_schedule()
        else:
            await self._run_interval_schedule()
    
    async def stop(self):
        """Остановка планировщика."""
        self.is_running = False
        logger.info("Планировщик остановлен")
    
    async def _run_interval_schedule(self):
        """Запуск рассылки с интервалами (hourly, 3hours, 6hours)."""
        interval_seconds = SCHEDULE_INTERVALS.get(self.interval, 3600)
        
        logger.info(f"Запущен интервальный режим: каждые {interval_seconds} секунд")
        
        while self.is_running:
            try:
                await self._send_scheduled_digest()
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Ошибка в интервальном планировщике: {e}")
                await asyncio.sleep(60)  # Подождать минуту при ошибке
    
    async def _run_daily_schedule(self):
        """Запуск ежедневной рассылки в определенное время."""
        logger.info(f"Запущен ежедневный режим: отправка в {DAILY_SEND_TIME}")
        
        while self.is_running:
            try:
                now = datetime.now()
                send_time = datetime.strptime(DAILY_SEND_TIME, "%H:%M").time()
                
                # Вычисляем время до следующей отправки
                next_send = datetime.combine(now.date(), send_time)
                if now.time() > send_time:
                    # Если время уже прошло, планируем на завтра
                    next_send = datetime.combine(now.date(), send_time) + timedelta(days=1)
                
                wait_seconds = (next_send - now).total_seconds()
                
                logger.info(f"Ожидание до следующей рассылки: {wait_seconds:.0f} секунд")
                await asyncio.sleep(wait_seconds)
                
                await self._send_scheduled_digest()
                
            except Exception as e:
                logger.error(f"Ошибка в ежедневном планировщике: {e}")
                await asyncio.sleep(3600)  # Подождать час при ошибке
    
    async def _send_scheduled_digest(self):
        """
        Отправка запланированного дайджеста в Telegram канал.
        
        Парсит новости, ранжирует их, сохраняет в БД и автоматически
        отправляет топ-4 новостей в настроенный канал.
        """
        logger.info("Начало отправки запланированного дайджеста")
        
        try:
            # Парсинг новостей
            news_list = await self.rss_parser.parse_all_sources()
            
            if not news_list:
                logger.warning("Нет новостей для рассылки")
                return
            
            # Ранжирование
            ranked_news = self.ranking_engine.rank_news_list(news_list)
            
            # Сохранение в БД
            saved_count = 0
            for news in ranked_news:
                if self.db_manager.add_news(news):
                    saved_count += 1
            
            logger.info(f"Сохранено {saved_count} новых новостей из {len(ranked_news)}")
            
            # Получение топ новостей
            top_news = ranked_news[:TOP_NEWS_COUNT]
            
            # Определение периода
            interval_seconds = SCHEDULE_INTERVALS.get(self.interval, 3600)
            hours = interval_seconds // 3600
            
            if hours == 1:
                period = "последний час"
            elif hours < 24:
                period = f"последние {hours} часа"
            else:
                period = "сегодня"
            
            # Отправка дайджеста в канал
            message = await self.channel_poster.post_digest(top_news, period)
            
            if message:
                logger.info(f"✅ Автоматический дайджест успешно отправлен в канал")
            else:
                logger.warning("⚠️ Не удалось отправить автоматический дайджест в канал")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке запланированного дайджеста: {e}", exc_info=True)

