"""
Модуль парсинга новостей для NewsBot.
Содержит парсинг RSS, HTML и ранжирование новостей.
"""

from .rss_parser import RSSParser
from .html_parser import HTMLParser
from .ranking import RankingEngine

__all__ = ['RSSParser', 'HTMLParser', 'RankingEngine']

