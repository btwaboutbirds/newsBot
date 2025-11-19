"""
Модуль для автоматической отправки дайджеста новостей в Telegram канал.
"""

from typing import List, Optional
from aiogram import Bot
from aiogram.types import Message

from config.settings import CHANNEL_ID, TOP_NEWS_COUNT
from database.models import News
from utils.formatter import format_digest_message
from utils.logger import setup_logger


logger = setup_logger(__name__)


class ChannelPoster:
    """
    Класс для отправки дайджестов новостей в Telegram канал.
    """
    
    def __init__(self, bot: Bot):
        """
        Инициализация постера.
        
        Args:
            bot: Экземпляр бота aiogram
        """
        self.bot = bot
        self.channel_id = CHANNEL_ID
        
        logger.info(f"ChannelPoster инициализирован для канала: {self.channel_id}")
    
    async def post_digest(
        self, 
        news_list: List[News], 
        period: str = "последний час"
    ) -> Optional[Message]:
        """
        Отправляет дайджест топ-4 новостей в канал.
        
        Args:
            news_list: Список новостей для отправки
            period: Период дайджеста (например, "последний час", "последние 3 часа")
        
        Returns:
            Отправленное сообщение или None в случае ошибки
        """
        try:
            if not news_list:
                logger.warning("Попытка отправить пустой дайджест в канал")
                return None
            
            # Ограничиваем до TOP_NEWS_COUNT новостей
            top_news = news_list[:TOP_NEWS_COUNT]
            
            # Форматируем дайджест
            formatted_message = format_digest_message(
                [news.to_dict() for news in top_news], 
                period
            )
            
            # Отправляем в канал
            logger.info(f"📢 Отправка дайджеста в канал {self.channel_id} ({len(top_news)} новостей)")
            
            message = await self.bot.send_message(
                chat_id=self.channel_id,
                text=formatted_message,
                parse_mode="MarkdownV2",
                disable_web_page_preview=False
            )
            
            logger.info(f"✅ Дайджест успешно отправлен в канал (message_id: {message.message_id})")
            
            return message
            
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке дайджеста в канал: {e}", exc_info=True)
            return None
    
    async def test_channel_access(self) -> bool:
        """
        Проверяет доступ бота к каналу.
        
        Returns:
            True если бот имеет доступ, False иначе
        """
        try:
            # Пытаемся получить информацию о чате
            chat = await self.bot.get_chat(self.channel_id)
            logger.info(f"✅ Доступ к каналу подтвержден: {chat.title}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Нет доступа к каналу {self.channel_id}: {e}")
            return False

