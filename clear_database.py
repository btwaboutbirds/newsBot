"""
Скрипт для очистки базы данных от всех новостей.
"""

import sys
import argparse
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


logger = setup_logger(__name__)


def clear_database(confirm: bool = True):
    """
    Очищает базу данных от всех новостей.
    
    Args:
        confirm: Требовать ли подтверждение от пользователя
    """
    logger.info("=" * 60)
    logger.info("🗑️  Очистка базы данных от новостей")
    logger.info("=" * 60)
    
    try:
        db_manager = DatabaseManager()
        
        # Получаем количество новостей перед удалением
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM news")
            count_before = cursor.fetchone()[0]
        
        if count_before == 0:
            logger.info("✅ База данных уже пуста. Новостей для удаления нет.")
            return
        
        logger.info(f"📊 Найдено новостей в базе: {count_before}")
        
        # Подтверждение удаления
        if confirm:
            logger.warning("⚠️  ВНИМАНИЕ: Все новости будут удалены!")
            try:
                response = input("Продолжить? (yes/no): ").strip().lower()
                if response not in ['yes', 'y', 'да', 'д']:
                    logger.info("❌ Операция отменена пользователем")
                    return
            except (EOFError, KeyboardInterrupt):
                logger.info("❌ Операция отменена")
                return
        
        # Удаляем все новости
        deleted_count = db_manager.clear_all_news()
        
        logger.info("=" * 60)
        logger.info(f"✅ Успешно удалено {deleted_count} новостей из базы данных")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Ошибка при очистке базы данных: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Очистка базы данных от новостей")
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Автоматически подтвердить удаление без запроса"
    )
    
    args = parser.parse_args()
    clear_database(confirm=not args.yes)

