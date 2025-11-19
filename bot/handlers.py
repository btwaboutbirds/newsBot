"""
Обработчики команд Telegram бота.
Реализация команд /start, /news, /digest.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from datetime import timedelta

from database.db_manager import DatabaseManager
from parser.rss_parser import RSSParser
from parser.ranking import RankingEngine
from bot.channel_poster import ChannelPoster
from utils.formatter import format_news_message, format_digest_message
from utils.logger import setup_logger
from config.settings import DEFAULT_NEWS_COUNT, TOP_NEWS_COUNT, SCHEDULE_INTERVALS, DEFAULT_INTERVAL


logger = setup_logger(__name__)
router = Router()


# Инициализация компонентов
db_manager = DatabaseManager()
rss_parser = RSSParser()
ranking_engine = RankingEngine()
# channel_poster будет инициализирован в setup_handlers с экземпляром бота


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start.
    
    Args:
        message: Сообщение от пользователя
    """
    logger.info(f"Пользователь {message.from_user.id} запустил бота")
    
    welcome_text = """
🤖 *Добро пожаловать в NewsBot\\!*

Я помогу вам быть в курсе последних новостей о *Vibe Coding*\\.

*Доступные команды:*

📰 /news \\[количество\\] \\- Получить свежие новости
   Пример: `/news` или `/news 10`

📊 /digest \\- Дайджест лучших новостей

📢 /post\\_digest \\- Отправить дайджест в канал \\(admin\\)

Новости автоматически собираются из проверенных источников и ранжируются по релевантности\\.

*Приятного чтения\\!* 📖
"""
    
    await message.answer(welcome_text, parse_mode="MarkdownV2")


@router.message(Command("news"))
async def cmd_news(message: Message):
    """
    Обработчик команды /news.
    Отправляет свежие новости пользователю.
    
    Args:
        message: Сообщение от пользователя
    """
    logger.info(f"Пользователь {message.from_user.id} запросил новости")
    
    try:
        # Парсим количество новостей из команды
        args = message.text.split()
        count = int(args[1]) if len(args) > 1 else DEFAULT_NEWS_COUNT
        count = max(1, min(count, 20))  # Ограничение 1-20
        
        # Отправляем сообщение о загрузке
        loading_msg = await message.answer("🔄 Загружаю свежие новости\\.\\.\\.", parse_mode="MarkdownV2")
        
        # Парсим новости из всех источников
        news_list = await rss_parser.parse_all_sources()
        
        if not news_list:
            await loading_msg.edit_text("📭 К сожалению, не удалось загрузить новости\\. Попробуйте позже\\.", 
                                       parse_mode="MarkdownV2")
            return
        
        # Ранжируем новости
        ranked_news = ranking_engine.rank_news_list(news_list)
        
        # Сохраняем в БД
        saved_count = 0
        for news in ranked_news[:count]:
            if db_manager.add_news(news):
                saved_count += 1
        
        logger.info(f"Сохранено {saved_count} новых новостей из {len(ranked_news)}")
        
        # Берем топ новости
        top_news = ranked_news[:count]
        
        # Форматируем и отправляем
        formatted_message = format_news_message([news.to_dict() for news in top_news])
        
        await loading_msg.edit_text(formatted_message, parse_mode="MarkdownV2")
        
    except ValueError:
        await message.answer("❌ Неверный формат команды\\. Используйте: `/news` или `/news 5`", 
                           parse_mode="MarkdownV2")
    except Exception as e:
        logger.error(f"Ошибка при обработке команды /news: {e}")
        await message.answer("❌ Произошла ошибка при загрузке новостей\\. Попробуйте позже\\.", 
                           parse_mode="MarkdownV2")


@router.message(Command("digest"))
async def cmd_digest(message: Message):
    """
    Обработчик команды /digest.
    Отправляет дайджест лучших новостей за период.
    
    Args:
        message: Сообщение от пользователя
    """
    logger.info(f"Пользователь {message.from_user.id} запросил дайджест")
    
    try:
        # Отправляем сообщение о загрузке
        loading_msg = await message.answer("🔄 Готовлю дайджест\\.\\.\\.", parse_mode="MarkdownV2")
        
        # Определяем период на основе настроек расписания
        interval_seconds = SCHEDULE_INTERVALS.get(DEFAULT_INTERVAL, 3600)
        hours = interval_seconds // 3600
        
        # Получаем новости за период из БД
        news_list = db_manager.get_news_by_period(hours=hours, limit=TOP_NEWS_COUNT)
        
        if not news_list:
            # Если в БД нет новостей, парсим заново
            logger.info("Новостей в БД нет, запускаем парсинг")
            
            all_news = await rss_parser.parse_all_sources()
            
            if not all_news:
                await loading_msg.edit_text("📭 К сожалению, не удалось загрузить новости\\. Попробуйте позже\\.", 
                                           parse_mode="MarkdownV2")
                return
            
            # Ранжируем и сохраняем
            ranked_news = ranking_engine.rank_news_list(all_news)
            
            for news in ranked_news:
                db_manager.add_news(news)
            
            news_list = ranked_news[:TOP_NEWS_COUNT]
        
        # Определяем текст периода
        if hours == 1:
            period = "последний час"
        elif hours < 24:
            period = f"последние {hours} часа"
        else:
            period = "сегодня"
        
        # Форматируем и отправляем дайджест
        formatted_message = format_digest_message([news.to_dict() for news in news_list], period)
        
        await loading_msg.edit_text(formatted_message, parse_mode="MarkdownV2")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке команды /digest: {e}")
        await message.answer("❌ Произошла ошибка при формировании дайджеста\\. Попробуйте позже\\.", 
                           parse_mode="MarkdownV2")


@router.message(Command("post_digest"))
async def cmd_post_digest(message: Message):
    """
    Обработчик команды /post_digest.
    Отправляет дайджест лучших новостей напрямую в канал.
    Команда доступна только администраторам бота.
    
    Args:
        message: Сообщение от пользователя
    """
    logger.info(f"Пользователь {message.from_user.id} запросил постинг дайджеста в канал")
    
    try:
        # Отправляем сообщение о начале процесса
        status_msg = await message.answer("🔄 Готовлю дайджест для канала\\.\\.\\.", parse_mode="MarkdownV2")
        
        # Определяем период на основе настроек расписания
        interval_seconds = SCHEDULE_INTERVALS.get(DEFAULT_INTERVAL, 3600)
        hours = interval_seconds // 3600
        
        # Получаем новости за период из БД
        news_list = db_manager.get_news_by_period(hours=hours, limit=TOP_NEWS_COUNT)
        
        if not news_list:
            # Если в БД нет новостей, парсим заново
            logger.info("Новостей в БД нет, запускаем парсинг")
            await status_msg.edit_text("🔍 Парсинг свежих новостей\\.\\.\\.", parse_mode="MarkdownV2")
            
            all_news = await rss_parser.parse_all_sources()
            
            if not all_news:
                await status_msg.edit_text(
                    "📭 К сожалению, не удалось загрузить новости\\. Попробуйте позже\\.", 
                    parse_mode="MarkdownV2"
                )
                return
            
            # Ранжируем и сохраняем
            ranked_news = ranking_engine.rank_news_list(all_news)
            
            for news in ranked_news:
                db_manager.add_news(news)
            
            news_list = ranked_news[:TOP_NEWS_COUNT]
        
        # Определяем текст периода
        if hours == 1:
            period = "последний час"
        elif hours < 24:
            period = f"последние {hours} часа"
        else:
            period = "сегодня"
        
        # Инициализируем постер и отправляем в канал
        await status_msg.edit_text("📢 Отправка в канал\\.\\.\\.", parse_mode="MarkdownV2")
        
        channel_poster = ChannelPoster(message.bot)
        posted_message = await channel_poster.post_digest(news_list, period)
        
        if posted_message:
            await status_msg.edit_text(
                f"✅ Дайджест успешно отправлен в канал\\!\n"
                f"Отправлено новостей: {len(news_list)}", 
                parse_mode="MarkdownV2"
            )
        else:
            await status_msg.edit_text(
                "❌ Не удалось отправить дайджест в канал\\. Проверьте права бота\\.", 
                parse_mode="MarkdownV2"
            )
        
    except Exception as e:
        logger.error(f"Ошибка при отправке дайджеста в канал: {e}")
        await message.answer(
            "❌ Произошла ошибка при отправке дайджеста в канал\\. Попробуйте позже\\.", 
            parse_mode="MarkdownV2"
        )


def setup_handlers() -> Router:
    """
    Настройка обработчиков команд.
    
    Returns:
        Router с настроенными обработчиками
    """
    logger.info("Обработчики команд настроены")
    return router

