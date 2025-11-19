"""
Скрипт для парсинга и сохранения топ-4 новостей в базу данных.
После сохранения автоматически отправляет дайджест в Telegram канал.
"""

import asyncio
import sys
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from parser.rss_parser import RSSParser
from parser.ranking import RankingEngine
from database.db_manager import DatabaseManager
from bot.channel_poster import ChannelPoster
from config.settings import BOT_TOKEN, DEFAULT_INTERVAL, SCHEDULE_INTERVALS
from utils.logger import setup_logger

# Настройка вывода в UTF-8 для Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


logger = setup_logger(__name__)


async def parse_and_save_top_news(top_count: int = 4, post_to_channel: bool = True):
    """
    Парсит новости из RSS источников, ранжирует их и сохраняет топ-N в БД.
    После сохранения автоматически отправляет дайджест в Telegram канал.
    
    Args:
        top_count: Количество топ новостей для сохранения
        post_to_channel: Отправлять ли дайджест в канал после парсинга
    """
    logger.info("=" * 60)
    logger.info(f"🚀 Запуск парсинга новостей (топ-{top_count})")
    logger.info("=" * 60)
    
    try:
        # 1. Инициализация компонентов
        logger.info("📋 Инициализация компонентов...")
        rss_parser = RSSParser()
        ranking_engine = RankingEngine()
        db_manager = DatabaseManager()
        
        # 2. Парсинг всех источников
        logger.info("🔍 Парсинг RSS источников...")
        all_news = await rss_parser.parse_all_sources()
        
        if not all_news:
            logger.warning("⚠️ Не найдено ни одной новости")
            return
        
        logger.info(f"✅ Спарсено {len(all_news)} новостей")
        
        # 3. Ранжирование новостей
        logger.info("📊 Ранжирование новостей...")
        ranked_news = ranking_engine.rank_news_list(all_news)
        
        # 4. Выбор топ-N новостей
        top_news = ranked_news[:top_count]
        logger.info(f"🏆 Выбрано топ-{len(top_news)} новостей")
        
        # 5. Сохранение в базу данных
        logger.info("💾 Сохранение в базу данных...")
        saved_count = 0
        duplicate_count = 0
        
        for i, news in enumerate(top_news, 1):
            news_id = db_manager.add_news(news)
            
            if news_id:
                saved_count += 1
                logger.info(
                    f"  {i}. ✅ Сохранено (ID: {news_id}, рейтинг: {news.rating:.2f}): "
                    f"{news.title[:60]}..."
                )
            else:
                duplicate_count += 1
                logger.info(
                    f"  {i}. ⏭️  Дубликат (рейтинг: {news.rating:.2f}): "
                    f"{news.title[:60]}..."
                )
        
        # 6. Итоговая статистика
        logger.info("=" * 60)
        logger.info("📈 Итоговая статистика:")
        logger.info(f"  • Всего спарсено: {len(all_news)}")
        logger.info(f"  • Топ новостей: {len(top_news)}")
        logger.info(f"  • Сохранено новых: {saved_count}")
        logger.info(f"  • Дубликатов: {duplicate_count}")
        logger.info("=" * 60)
        
        # 7. Вывод сохраненных новостей
        if saved_count > 0:
            logger.info("🎉 Успешно сохраненные новости:")
            for i, news in enumerate(top_news, 1):
                logger.info(f"\n  {i}. {news.title}")
                logger.info(f"     📰 Источник: {news.source}")
                logger.info(f"     ⭐ Рейтинг: {news.rating:.2f}")
                logger.info(f"     🔗 {news.link}")
        
        logger.info("\n✅ Парсинг завершен успешно!")
        
        # 8. Отправка дайджеста в канал
        if post_to_channel and len(top_news) > 0:
            logger.info("=" * 60)
            logger.info("📢 Отправка дайджеста в Telegram канал...")
            logger.info("=" * 60)
            
            try:
                # Инициализируем бота и постер
                bot = Bot(
                    token=BOT_TOKEN,
                    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
                )
                channel_poster = ChannelPoster(bot)
                
                # Определяем период для дайджеста
                interval_seconds = SCHEDULE_INTERVALS.get(DEFAULT_INTERVAL, 3600)
                hours = interval_seconds // 3600
                
                if hours == 1:
                    period = "последний час"
                elif hours < 24:
                    period = f"последние {hours} часа"
                else:
                    period = "сегодня"
                
                # Отправляем дайджест
                message = await channel_poster.post_digest(top_news, period)
                
                if message:
                    logger.info(f"✅ Дайджест успешно отправлен в канал!")
                else:
                    logger.warning("⚠️ Не удалось отправить дайджест в канал")
                
                # Закрываем сессию бота
                await bot.session.close()
                
            except Exception as e:
                logger.error(f"❌ Ошибка при отправке в канал: {e}", exc_info=True)
        
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге: {e}", exc_info=True)
        raise


async def main():
    """
    Главная функция.
    
    Парсит новости и автоматически отправляет дайджест в канал.
    """
    await parse_and_save_top_news(top_count=4, post_to_channel=True)


if __name__ == "__main__":
    asyncio.run(main())

