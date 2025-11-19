# Скрипт активации виртуального окружения для PowerShell
# Использование: .\activate.ps1
# 
# Этот скрипт автоматически обходит проблему с Execution Policy

Write-Host "🔧 Активация виртуального окружения NewsBot..." -ForegroundColor Cyan

# Проверка существования виртуального окружения
if (-Not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Виртуальное окружение не найдено!" -ForegroundColor Red
    Write-Host "Создайте его командой: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Попытка активации с обходом Execution Policy
try {
    # Сначала пробуем стандартную активацию
    & ".\venv\Scripts\Activate.ps1" -ErrorAction Stop
} catch {
    # Если не получилось из-за Execution Policy, используем обходной путь
    Write-Host "⚠️  Обнаружена проблема с Execution Policy, используем обходной путь..." -ForegroundColor Yellow
    $env:VIRTUAL_ENV = (Resolve-Path ".\venv").Path
    $env:PATH = "$env:VIRTUAL_ENV\Scripts;$env:PATH"
    
    # Удаляем PYTHONHOME, если он установлен
    if ($env:PYTHONHOME) {
        Remove-Item Env:PYTHONHOME
    }
    
    Write-Host "✅ Виртуальное окружение активировано (обходной путь)!" -ForegroundColor Green
    $LASTEXITCODE = 0
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Виртуальное окружение активировано!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Доступные команды:" -ForegroundColor Cyan
    Write-Host "  python main.py                    - Запуск бота" -ForegroundColor White
    Write-Host "  python parse_and_save_news.py     - Парсинг и сохранение новостей" -ForegroundColor White
    Write-Host "  python test_parser.py             - Тест HTML парсера" -ForegroundColor White
    Write-Host "  deactivate                        - Деактивировать окружение" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Ошибка активации окружения!" -ForegroundColor Red
    exit 1
}

