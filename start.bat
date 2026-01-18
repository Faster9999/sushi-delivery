@echo off
chcp 65001 >nul
color 0A

echo.
echo 🍣 TokyoGo - Quick Start
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установи Python 3.10+ с python.org
    pause
    exit /b 1
)

echo ✅ Python найден

REM Check venv
if not exist venv (
    echo 📦 Создаю виртуальное окружение...
    python -m venv venv
)

echo 🔧 Активирую виртуальное окружение...
call venv\Scripts\activate.bat

echo 📥 Устанавливаю зависимости...
pip install -q -r requirements.txt

echo 🗄️  Инициализирую БД...
python database.py

echo.
echo ✅ Подготовка завершена!
echo.
echo 🚀 Запускаю FastAPI сервер (https://localhost:8443)...
echo.

start cmd /k "venv\Scripts\activate.bat && python main.py"

timeout /t 3 /nobreak

echo 🤖 Запускаю Telegram бот...
echo.

start cmd /k "venv\Scripts\activate.bat && python bot.py"

echo.
echo ✅ Оба процесса запущены!
echo.
echo 📱 Открой Telegram, напиши своему боту /start
echo 🌐 Админ-панель: https://localhost:8443/admin
echo 📚 API документация: https://localhost:8443/docs
echo.
echo Закрой это окно, чтобы остановить запуск
pause