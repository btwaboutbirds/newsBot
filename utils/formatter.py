"""
Модуль форматирования сообщений для Telegram.
Создает красивые и читаемые сообщения в формате Markdown.
"""

from typing import List, Dict, Any
import re
from bs4 import BeautifulSoup


def strip_html_tags(text: str) -> str:
    """
    Удаление всех HTML/CSS тегов и разметки из текста.
    
    Args:
        text: Текст с возможными HTML-тегами
    
    Returns:
        Чистый текст без HTML-разметки
    """
    if not text:
        return text
    
    try:
        # Используем BeautifulSoup для парсинга и извлечения текста
        soup = BeautifulSoup(text, 'html.parser')
        # Извлекаем только текст, без тегов
        clean_text = soup.get_text(separator=' ', strip=True)
        # Удаляем множественные пробелы
        clean_text = ' '.join(clean_text.split())
        return clean_text
    except Exception:
        # Если BeautifulSoup не справился, используем регулярные выражения как fallback
        # Удаляем HTML-теги
        clean_text = re.sub(r'<[^>]+>', '', text)
        # Удаляем HTML-сущности
        clean_text = re.sub(r'&[a-zA-Z0-9#]+;', '', clean_text)
        # Удаляем множественные пробелы
        clean_text = ' '.join(clean_text.split())
        return clean_text


def escape_markdown(text: str) -> str:
    """
    Экранирование специальных символов Markdown для Telegram.
    
    Args:
        text: Исходный текст
    
    Returns:
        Текст с экранированными специальными символами
    """
    # Символы, которые нужно экранировать в Markdown
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text


def truncate_by_sentences(text: str, max_chars: int = 500) -> str:
    """
    Обрезает текст по целым предложениям до указанного лимита символов.
    
    Args:
        text: Исходный текст
        max_chars: Максимальное количество символов
    
    Returns:
        Обрезанный текст по предложениям
    """
    if not text or len(text) <= max_chars:
        return text
    
    # Обрезаем до лимита
    truncated = text[:max_chars]
    
    # Ищем последнее завершенное предложение (точка, восклицательный или вопросительный знак)
    # с пробелом после него или в конце строки
    sentence_endings = re.finditer(r'[.!?]\s+', truncated)
    matches = list(sentence_endings)
    
    if matches:
        # Берем позицию после последнего предложения
        last_match = matches[-1]
        return truncated[:last_match.end()].strip()
    
    # Если не нашли предложения, обрезаем по последнему пробелу
    last_space = truncated.rfind(' ')
    if last_space > max_chars * 0.7:  # Если пробел не слишком близко к началу
        return truncated[:last_space].strip() + '...'
    
    return truncated.strip() + '...'


def format_news_message(news_list: List[Dict[str, Any]]) -> str:
    """
    Форматирование списка новостей для отправки в Telegram.
    
    Args:
        news_list: Список новостей (словари с полями title, link, description)
    
    Returns:
        Отформатированное сообщение в Markdown
    """
    if not news_list:
        return "📭 Новостей не найдено\\."
    
    message_parts = ["📰 *Свежие новости:*\n"]
    
    for idx, news in enumerate(news_list, 1):
        title = escape_markdown(news.get('title', 'Без заголовка'))
        link = news.get('link', '')
        description = news.get('description', '')
        
        # Обрезаем описание по предложениям до 300 символов
        if description:
            description = truncate_by_sentences(description, max_chars=300)
        
        # Экранируем описание
        description = escape_markdown(description) if description else ''
        
        # Формируем сообщение для одной новости
        news_message = f"\n{idx}\\. *{title}*\n"
        news_message += f"[Читать далее]({link})\n"
        
        if description:
            news_message += f"\n_{description}_\n"
        
        message_parts.append(news_message)
    
    return "\n".join(message_parts)


def format_digest_message(news_list: List[Dict[str, Any]], period: str = "период") -> str:
    """
    Форматирование дайджеста новостей (топ-4 или громкая новость).
    
    Args:
        news_list: Список новостей
        period: Период дайджеста (например, "последний час", "сегодня")
    
    Returns:
        Отформатированное сообщение дайджеста
    """
    if not news_list:
        return f"📭 Новостей за {escape_markdown(period)} не найдено\\."
    
    period_escaped = escape_markdown(period)
    
    if len(news_list) == 1:
        # Формат "громкой новости" - больше места для описания
        news = news_list[0]
        title = escape_markdown(news.get('title', 'Без заголовка'))
        link = news.get('link', '')
        description = news.get('description', '')
        rating = news.get('rating', 0.0)
        
        # Для громкой новости используем больше символов (600) и обрезаем по предложениям
        if description:
            description = truncate_by_sentences(description, max_chars=600)
        description = escape_markdown(description) if description else ''
        
        message = f"🔥 *Громкая новость за {period_escaped}\\!*\n\n"
        message += f"*{title}*\n"
        message += f"[Читать далее]({link})\n\n"
        
        if description:
            message += f"_{description}_\n\n"
        
        rating_str = escape_markdown(f"{rating:.1f}")
        message += f"⭐ Рейтинг: {rating_str}/10"
        
        return message
    
    else:
        # Формат "топ-4 новости"
        message_parts = [f"⭐ *Топ\\-{len(news_list)} новостей за {period_escaped}:*\n"]
        
        for idx, news in enumerate(news_list, 1):
            title = escape_markdown(news.get('title', 'Без заголовка'))
            link = news.get('link', '')
            description = news.get('description', '')
            rating = news.get('rating', 0.0)
            
            # Обрезаем описание по предложениям до 400 символов
            if description:
                description = truncate_by_sentences(description, max_chars=400)
            
            description = escape_markdown(description) if description else ''
            
            news_message = f"\n{idx}\\. *{title}*\n"
            news_message += f"[Читать далее]({link})\n"
            
            if description:
                news_message += f"_{description}_\n"
            
            rating_str = escape_markdown(f"{rating:.1f}")
            news_message += f"⭐ {rating_str}/10\n"
            
            message_parts.append(news_message)
        
        return "\n".join(message_parts)

