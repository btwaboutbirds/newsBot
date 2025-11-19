# Использование HTML парсера

## Обновления

HTML парсер был обновлен для более точного извлечения чистого текста из статей с использованием библиотеки **trafilatura**.

### Что было улучшено:

- ✅ **Точное извлечение** основного контента статьи
- ✅ **Автоматическое удаление** рекламы, навигации, комментариев, боковых панелей
- ✅ **Извлечение метаданных** (заголовок, автор, дата)
- ✅ **Fallback механизм** на BeautifulSoup если trafilatura не справился
- ✅ **Чистый текст** без HTML/CSS кода

## Установка зависимостей

После обновления необходимо установить новую зависимость:

```bash
pip install -r requirements.txt
```

Или отдельно:

```bash
pip install trafilatura==1.12.2
```

## Использование

### 1. Извлечение только текста

```python
from parser.html_parser import HTMLParser
import asyncio

async def main():
    parser = HTMLParser()
    
    # Извлечение текста из статьи
    text = await parser.get_article_text("https://example.com/article")
    
    if text:
        print(f"Текст статьи: {text}")
        print(f"Длина: {parser.calculate_article_length(text)} слов")

asyncio.run(main())
```

### 2. Извлечение текста с метаданными

```python
from parser.html_parser import HTMLParser
import asyncio

async def main():
    parser = HTMLParser()
    
    # Извлечение текста и метаданных
    metadata = await parser.get_article_metadata("https://example.com/article")
    
    if metadata:
        print(f"Заголовок: {metadata['title']}")
        print(f"Автор: {metadata['author']}")
        print(f"Дата: {metadata['date']}")
        print(f"Описание: {metadata['description']}")
        print(f"Текст: {metadata['text']}")

asyncio.run(main())
```

### 3. Прямое извлечение из HTML

```python
from parser.html_parser import HTMLParser

parser = HTMLParser()
html_content = "<html>...</html>"

# Извлечение текста
text = parser.extract_text(html_content, url="https://example.com/article")
print(text)
```

## Тестирование

Запустите тестовый скрипт:

```bash
python test_parser.py
```

Для тестирования на реальных статьях, добавьте URL в файл `test_parser.py`:

```python
test_urls = [
    "https://habr.com/ru/articles/...",
    "https://vc.ru/...",
    # ... другие URL
]
```

## Интеграция с NewsBot

Парсер автоматически используется в основной логике бота. Вы можете использовать метод `get_article_text()` для получения полного текста статьи:

```python
from parser.html_parser import HTMLParser

async def fetch_full_article(news_link: str) -> str:
    """Получить полный текст статьи."""
    parser = HTMLParser()
    text = await parser.get_article_text(news_link)
    return text or "Не удалось извлечь текст"
```

## Преимущества trafilatura

1. **Точность**: Использует ML-подход для определения основного контента
2. **Многоязычность**: Поддержка русского и других языков
3. **Скорость**: Быстрая обработка даже больших статей
4. **Надежность**: Работает с различными структурами сайтов
5. **Метаданные**: Автоматическое извлечение дополнительной информации

## Fallback механизм

Если trafilatura не может извлечь текст, автоматически используется резервный метод на основе BeautifulSoup, который:

1. Удаляет служебные элементы (script, style, nav, footer, header, aside)
2. Ищет основной контент по тегам `<article>`, `<main>` или классам
3. Извлекает текст и очищает от лишних пробелов

## Примечания

- Метод `extract_text()` теперь принимает опциональный параметр `url` для улучшения качества извлечения
- Все методы логируют ошибки через систему логирования проекта
- Рекомендуется использовать `get_article_text()` для простого извлечения текста
- Используйте `get_article_metadata()` когда нужны дополнительные данные о статье

