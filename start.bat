@echo off
echo Setting up Sadqa Tracker Backend for Windows...
echo ===============================================

REM Check if .env file exists
if not exist .env (
    echo.
    echo Warning: .env file not found!
    echo Please copy .env.example to .env and configure your settings:
    echo   copy .env.example .env
    echo Then edit .env with your database URL and Google OAuth credentials.
    pause
    exit /b 1
)

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo.
    echo Warning: Virtual environment not detected!
    echo Please activate your virtual environment first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements-dev.txt

echo.
echo Setting up database...
python -c "
import asyncio
from app.db.init_db import init_db

async def setup():
    await init_db()
    print('Database setup complete!')

asyncio.run(setup())
"

echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo Documentation will be available at: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.

python main.py
