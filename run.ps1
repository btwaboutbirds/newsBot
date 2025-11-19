# Скрипт запуска бота с автоматической активацией окружения
# Использование: .\run.ps1

param(
    [Parameter(Position=0)]
    [ValidateSet('bot', 'parse', 'test')]
    [string]$Command = 'bot'
)

Write-Host '>> Запуск NewsBot...' -ForegroundColor Cyan

# Проверка существования виртуального окружения
if (-Not (Test-Path '.\venv\Scripts\python.exe')) {
    Write-Host 'XX Виртуальное окружение не найдено!' -ForegroundColor Red
    Write-Host 'Создайте его командой: python -m venv venv' -ForegroundColor Yellow
    Write-Host 'Затем установите зависимости: .\venv\Scripts\pip.exe install -r requirements.txt' -ForegroundColor Yellow
    exit 1
}

# Проверка .env файла
if (-Not (Test-Path '.env')) {
    Write-Host '!!  Файл .env не найден!' -ForegroundColor Yellow
    Write-Host 'Создайте .env файл с токеном бота:' -ForegroundColor Yellow
    Write-Host 'TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here=your_token_here' -ForegroundColor White
    Write-Host ''
}

# Запуск соответствующего скрипта
switch ($Command) {
    'bot' {
        Write-Host '>> Запуск Telegram бота...' -ForegroundColor Green
        & '.\venv\Scripts\python.exe' 'main.py'
    }
    'parse' {
        Write-Host '>> Запуск парсинга новостей...' -ForegroundColor Green
        & '.\venv\Scripts\python.exe' 'parse_and_save_news.py'
    }
    'test' {
        Write-Host '>> Запуск тестов парсера...' -ForegroundColor Green
        & '.\venv\Scripts\python.exe' 'test_parser.py'
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host 'XX Ошибка выполнения!' -ForegroundColor Red
    exit $LASTEXITCODE
}
