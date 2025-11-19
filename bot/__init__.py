"""
Модуль Telegram бота для NewsBot.
Содержит обработчики команд и логику расписания.
"""

from .handlers import setup_handlers
from .scheduler import NewsScheduler

__all__ = ['setup_handlers', 'NewsScheduler']

