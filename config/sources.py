"""
Список RSS источников для парсинга новостей о "Vibe Coding".
Каждый источник содержит: название, URL, язык и вес для ранжирования.
"""

RSS_SOURCES = [
    # Английские источники
    {
        "name": "Dev.to",
        "url": "https://dev.to/feed",
        "language": "en",
        "weight": 8.5,
        "category": "vibe-coding"
    },
    {
        "name": "Hacker News",
        "url": "https://hnrss.org/newest",
        "language": "en",
        "weight": 9.0,
        "category": "vibe-coding"
    },
    {
        "name": "Reddit Programming",
        "url": "https://www.reddit.com/r/programming/.rss",
        "language": "en",
        "weight": 7.5,
        "category": "vibe-coding"
    },
    {
        "name": "GitHub Blog",
        "url": "https://github.blog/feed/",
        "language": "en",
        "weight": 8.0,
        "category": "vibe-coding"
    },
    
    # Русские источники
    {
        "name": "Habr",
        "url": "https://habr.com/ru/rss/all/all/",
        "language": "ru",
        "weight": 9.0,
        "category": "vibe-coding"
    },
    {
        "name": "Tproger",
        "url": "https://tproger.ru/feed/",
        "language": "ru",
        "weight": 8.0,
        "category": "vibe-coding"
    },
]

