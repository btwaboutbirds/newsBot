"""
Тестовый скрипт для проверки извлечения текста из статей.
"""

import asyncio
from parser.html_parser import HTMLParser


async def test_article_extraction():
    """Тест извлечения текста из статьи."""
    parser = HTMLParser()
    
    # Примеры URL для тестирования (замените на реальные URL новостей)
    test_urls = [
        # Добавьте здесь URL статей, которые хотите протестировать
        # Например:
        # "https://example.com/article",
    ]
    
    if not test_urls:
        print("!!  Добавьте URL статей в список test_urls для тестирования")
        print("\nПример использования:")
        print("-" * 60)
        
        # Демонстрация с фейковым HTML
        sample_html = """
        <html>
            <head><title>Тестовая статья</title></head>
            <body>
                <nav>Навигация (будет удалена)</nav>
                <header>Шапка сайта (будет удалена)</header>
                <aside>Реклама (будет удалена)</aside>
                
                <article>
                    <h1>Заголовок статьи</h1>
                    <p>Это основной текст статьи. Он должен быть извлечен.</p>
                    <p>Еще один параграф с полезной информацией.</p>
                </article>
                
                <footer>Футер (будет удален)</footer>
            </body>
        </html>
        """
        
        text = parser.extract_text(sample_html)
        print("Извлеченный текст:")
        print(text)
        print("-" * 60)
        return
    
    for url in test_urls:
        print(f"\n{'='*80}")
        print(f"Обработка: {url}")
        print(f"{'='*80}\n")
        
        # Тест 1: Извлечение только текста
        print(">> Извлечение текста:")
        text = await parser.get_article_text(url)
        if text:
            # Показываем первые 500 символов
            preview = text[:500] + "..." if len(text) > 500 else text
            print(preview)
            print(f"\n>> Статистика:")
            print(f"  - Длина текста: {len(text)} символов")
            print(f"  - Количество слов: {parser.calculate_article_length(text)}")
        else:
            print("XX Не удалось извлечь текст")
        
        # Тест 2: Извлечение метаданных
        print(f"\n>> Метаданные статьи:")
        metadata = await parser.get_article_metadata(url)
        if metadata:
            print(f"  - Заголовок: {metadata.get('title', 'N/A')}")
            print(f"  - Автор: {metadata.get('author', 'N/A')}")
            print(f"  - Дата: {metadata.get('date', 'N/A')}")
            print(f"  - Описание: {metadata.get('description', 'N/A')[:100]}...")
        else:
            print("XX Не удалось извлечь метаданные")


if __name__ == "__main__":
    print(">> Тестирование HTML парсера с trafilatura\n")
    asyncio.run(test_article_extraction())

