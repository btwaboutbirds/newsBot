"""
Модуль логирования для NewsBot.
Настройка логгера с цветным выводом и правильным форматированием.
"""

import logging
import sys
from typing import Optional
from colorlog import ColoredFormatter
from config.settings import LOG_LEVEL, LOG_FORMAT


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Настройка логгера с цветным выводом.
    
    Args:
        name: Имя логгера (обычно __name__ модуля)
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    
    # Устанавливаем уровень логирования
    log_level = level or LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Проверяем, есть ли уже обработчики (избегаем дублирования)
    if logger.handlers:
        return logger
    
    # Создаем обработчик для консольного вывода
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Цветное форматирование
    color_formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)
    
    # Предотвращаем распространение логов к родительскому логгеру
    logger.propagate = False
    
    return logger

