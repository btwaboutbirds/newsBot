# Скрипт первоначальной настройки проекта
# Использование: .\setup.ps1

Write-Host "🔧 Настройка проекта NewsBot..." -ForegroundColor Cyan
Write-Host ""

# 1. Проверка Python
Write-Host "1️⃣  Проверка Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Python найден: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ❌ Python не найден! Установите Python 3.8 или выше." -ForegroundColor Red
    exit 1
}

# 2. Создание виртуального окружения
Write-Host ""
Write-Host "2️⃣  Создание виртуального окружения..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "   ⚠️  Окружение уже существует, пропускаем..." -ForegroundColor Yellow
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Виртуальное окружение создано" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Ошибка создания окружения!" -ForegroundColor Red
        exit 1
    }
}

# 3. Установка зависимостей
Write-Host ""
Write-Host "3️⃣  Установка зависимостей..." -ForegroundColor Yellow
& ".\venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\venv\Scripts\pip.exe" install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Зависимости установлены" -ForegroundColor Green
} else {
    Write-Host "   ❌ Ошибка установки зависимостей!" -ForegroundColor Red
    exit 1
}

# 4. Проверка .env файла
Write-Host ""
Write-Host "4️⃣  Проверка конфигурации..." -ForegroundColor Yellow
if (-Not (Test-Path ".env")) {
    Write-Host "   ⚠️  Файл .env не найден!" -ForegroundColor Yellow
    Write-Host "   Создаю шаблон .env файла..." -ForegroundColor Cyan
    
    $envTemplate = @"
# Telegram Bot Token (обязательно)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Database Configuration
DATABASE_PATH=newsbot.db

# Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Schedule Mode (manual или auto)
SCHEDULE_MODE=manual

# Schedule Interval (hourly, 3hours, 6hours, daily)
DEFAULT_INTERVAL=hourly
"@
    
    $envTemplate | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "   ✅ Создан файл .env" -ForegroundColor Green
    Write-Host "   ⚠️  ВАЖНО: Отредактируйте .env и добавьте токен бота!" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ Файл .env существует" -ForegroundColor Green
}

# 5. Проверка структуры проекта
Write-Host ""
Write-Host "5️⃣  Проверка структуры проекта..." -ForegroundColor Yellow

$requiredDirs = @("bot", "config", "database", "parser", "utils", "logs")
$allDirsExist = $true

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "   ✅ $dir/" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $dir/ отсутствует!" -ForegroundColor Red
        $allDirsExist = $false
    }
}

# Создание директории logs если её нет
if (-Not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "   ✅ Создана директория logs/" -ForegroundColor Green
}

# 6. Итоги
Write-Host ""
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 50) -ForegroundColor Cyan
Write-Host "✅ Настройка завершена!" -ForegroundColor Green
Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 50) -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Следующие шаги:" -ForegroundColor Cyan
Write-Host "1. Отредактируйте .env и добавьте токен бота" -ForegroundColor White
Write-Host "2. Запустите бота: .\run.ps1" -ForegroundColor White
Write-Host "   или: .\run.ps1 bot     - Запуск бота" -ForegroundColor White
Write-Host "        .\run.ps1 parse   - Парсинг новостей" -ForegroundColor White
Write-Host "        .\run.ps1 test    - Тестирование" -ForegroundColor White
Write-Host ""
Write-Host "Или активируйте окружение вручную: .\activate.ps1" -ForegroundColor White
Write-Host ""

