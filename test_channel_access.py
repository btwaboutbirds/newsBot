"""
Скрипт для проверки доступа бота к Telegram каналу.
Использовать перед запуском автопостинга.
"""

import asyncio
import sys
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.settings import BOT_TOKEN, CHANNEL_ID
from bot.channel_poster import ChannelPoster
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


async def test_channel_access():
    """
    Проверяет доступ бота к каналу и отправляет тестовое сообщение.
    """
    logger.info("=" * 60)
    logger.info("🧪 Тестирование доступа к Telegram каналу")
    logger.info("=" * 60)
    
    try:
        # Инициализация бота
        logger.info(f"Инициализация бота...")
        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
        )
        
        # Получение информации о боте
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот: @{bot_info.username} (ID: {bot_info.id})")
        
        # Инициализация постера
        logger.info(f"📢 Проверка доступа к каналу: {CHANNEL_ID}")
        channel_poster = ChannelPoster(bot)
        
        # Проверка доступа
        has_access = await channel_poster.test_channel_access()
        
        if not has_access:
            logger.error("❌ Бот не имеет доступа к каналу!")
            logger.info("\n📝 Инструкции:")
            logger.info("1. Откройте ваш канал в Telegram")
            logger.info("2. Добавьте бота как администратора")
            logger.info("3. Убедитесь, что у бота есть право 'Post Messages'")
            logger.info("4. Запустите этот скрипт снова")
            return False
        
        # Отправка тестового сообщения
        logger.info("📤 Отправка тестового сообщения...")
        
        test_message = """
🧪 *Тестовое сообщение*

Это тестовое сообщение для проверки работы бота\\.

Если вы видите это сообщение, значит бот успешно настроен и может постить дайджесты новостей в канал\\!

✅ Все работает\\!
"""
        
        message = await bot.send_message(
            chat_id=CHANNEL_ID,
            text=test_message,
            parse_mode="MarkdownV2"
        )
        
        logger.info(f"✅ Тестовое сообщение успешно отправлено (ID: {message.message_id})")
        
        logger.info("=" * 60)
        logger.info("🎉 Тест пройден успешно!")
        logger.info("=" * 60)
        logger.info("\n✅ Бот готов к автоматическому постингу дайджестов в канал.")
        logger.info("Запустите скрипт parse_and_save_news.py для отправки дайджеста.")
        
        # Закрытие сессии
        await bot.session.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании: {e}", exc_info=True)
        logger.info("\n📝 Возможные причины:")
        logger.info("1. Бот не добавлен в канал")
        logger.info("2. У бота нет прав администратора")
        logger.info("3. Неверный CHANNEL_ID в .env файле")
        logger.info("4. Неверный BOT_TOKEN в .env файле")
        return False


async def main():
    """Главная функция."""
    success = await test_channel_access()
    
    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())

