"""
Константы и настройки для NewsBot.
Все константы в UPPER_CASE согласно PEP 8.
"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here не найден в переменных окружения!")

# Telegram Channel Configuration
CHANNEL_ID = os.getenv("CHANNEL_ID")
if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID не найден в переменных окружения!")

# Database Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "newsbot.db")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Schedule Configuration
SCHEDULE_INTERVALS = {
    'hourly': 3600,      # Каждый час (в секундах)
    '3hours': 10800,     # Каждые 3 часа
    '6hours': 21600,     # Каждые 6 часов
    'daily': 86400       # Раз в день
}

# Время отправки для daily режима (формат HH:MM)
DAILY_SEND_TIME = "09:00"

# Режим работы по умолчанию ('manual' или 'auto')
DEFAULT_SCHEDULE_MODE = os.getenv("SCHEDULE_MODE", "manual")
DEFAULT_INTERVAL = os.getenv("DEFAULT_INTERVAL", "hourly")

# News Configuration
DEFAULT_NEWS_COUNT = 4  # Количество новостей по умолчанию для команды /news
TOP_NEWS_COUNT = 4      # Количество новостей в топ-дайджесте

# Rating Configuration
RATING_MIN = 0.0
RATING_MAX = 10.0

# Ключевые слова для ранжирования (больше релевантности = выше рейтинг)
RELEVANCE_KEYWORDS = [
    # Vibe Coding / Atmosphere
    "vibe coding", "вайб кодинг", "coding vibe", "атмосфера программирования",

    # Programming / Development (EN/RU)
    "programming", "программирование",
    "coding", "кодинг", "кодирование",
    "development", "разработка",
    "software development", "разработка софта",
    "app development", "разработка приложений",
    "web development", "веб-разработка",
    "backend", "бэкенд", "backend development", "разработка бэкенда",
    "frontend", "фронтенд", "frontend development", "разработка фронтенда",
    "fullstack", "фулстек", "fullstack developer", "фулстек разработчик",

    # Code / Source Code (EN/RU)
    "code", "код",
    "source code", "исходный код",
    "clean code", "чистый код",

    # Developer / Programmer (EN/RU)
    "developer", "разработчик",
    "software engineer", "инженер-программист", 
    "programmer", "программист",
    "fullstack developer", "фулстек разработчик",
    "ai developer", "разработчик интеллект",
    "machine learning engineer", "инженер по машинному обучению",

    # AI / ML / Neural Networks (EN/RU)
    "artificial intelligence", "искусственный интеллект", "ai", "ии",
    "machine learning", "машинное обучение",
    "neural networks", "нейронные сети",
    "deep learning", "глубокое обучение",
    "ml engineer", "ml инженер",
    "ai tools", "инструменты ии",

    # Cursor / IDE / Editor (EN/RU)
    "cursor", "курсор",
    "cursor ide", "cursor иде", "cursor editor", "editor cursor", "редактор cursor",
    "integrated development environment", "интегрированная среда разработки", "ide", "среда разработки",
    "text editor", "текстовый редактор",

    # Tools / Technologies (EN/RU)
    "git", "гит",
    "github", "гитхаб",
    "version control", "система контроля версий",
    "repository", "репозиторий",
    "command line", "командная строка",
    "terminal", "терминал",

    # Frameworks / Languages (EN/RU)
    "python", "питон",
    "javascript", "джаваскрипт",
    "typescript", "тайпскрипт",
    "java", "ява",
    "c++", "си плюс плюс",
    "c#", "си шарп",
    "go", "го",
    "rust", "раст",
    "sql", "скьюэль",

    # Classic Key Terms (EN/RU)
    "algorithm", "алгоритм",
    "data structure", "структура данных",
    "function", "функция",
    "variable", "переменная",
    "loop", "цикл",
    "debug", "отладка",
    "refactor", "рефакторинг",
    "pull request", "пулл-реквест",
    "commit", "коммит",
    "deploy", "деплой",
    "cloud", "облако",

    # Community, Trends
    "open source", "опенсорс",
    "stack overflow", "стэк оверфлоу",
    "best practice", "лучшие практики",
]

# Веса для расчета рейтинга
WEIGHT_FRESHNESS = 0.3      # Вес свежести новости
WEIGHT_SOURCE = 0.25        # Вес источника
WEIGHT_KEYWORDS = 0.25      # Вес ключевых слов
WEIGHT_LENGTH = 0.2         # Вес длины статьи

# HTTP Configuration
REQUEST_TIMEOUT = 30        # Таймаут для HTTP запросов (секунды)
MAX_RETRIES = 3            # Максимальное количество повторных попыток
RETRY_DELAY = 2            # Задержка между попытками (секунды)

