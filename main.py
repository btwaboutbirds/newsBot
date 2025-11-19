"""
NewsBot - Telegram бот для дайджестов новостей о "Vibe Coding".
Точка входа в приложение.
"""

import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.settings import BOT_TOKEN
from bot.handlers import setup_handlers
from bot.scheduler import NewsScheduler
from database.db_manager import DatabaseManager
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


# Настройка логирования
logger = setup_logger(__name__)


async def main():
    """
    Главная функция запуска бота.
    """
    logger.info("=" * 50)
    logger.info("🚀 Запуск NewsBot")
    logger.info("=" * 50)
    
    try:
        # Инициализация бота и диспетчера
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
        )
        dp = Dispatcher()
        
        # Инициализация базы данных
        logger.info("📊 Инициализация базы данных...")
        db_manager = DatabaseManager()
        
        # Настройка обработчиков команд
        logger.info("⚙️ Настройка обработчиков команд...")
        router = setup_handlers()
        dp.include_router(router)
        
        # Инициализация планировщика (для будущего расширения)
        logger.info("⏰ Инициализация планировщика...")
        scheduler = NewsScheduler(bot)
        
        # Получение информации о боте
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот запущен: @{bot_info.username}")
        logger.info("Режим работы: ручная рассылка (manual)")
        logger.info("Доступные команды: /start, /news, /digest, /post_digest")
        logger.info("=" * 50)
        
        # Запуск планировщика (если режим auto)
        # В MVP используется только manual режим
        asyncio.create_task(scheduler.start())
        
        # Запуск polling
        logger.info("👂 Ожидание сообщений...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.critical(f"❌ Критическая ошибка при запуске бота: {e}")
        sys.exit(1)
    
    finally:
        logger.info("🛑 Остановка бота...")
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⚠️ Бот остановлен пользователем (Ctrl+C)")
    except Exception as e:
        logger.critical(f"❌ Непредвиденная ошибка: {e}")
        sys.exit(1)

