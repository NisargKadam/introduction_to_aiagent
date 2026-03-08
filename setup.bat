@echo off
echo ============================================
echo   AI Agent Demo - Setup
echo   Author: Nisarg Kadam
echo ============================================
echo.

:: Create virtual environment
echo [1/3] Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate

:: Install dependencies
echo [2/3] Installing dependencies...
pip install -r requirements.txt

:: Check for .env
echo.
if not exist .env (
    echo [3/3] Creating .env from template...
    copy .env.example .env
    echo.
    echo ========================================
    echo  IMPORTANT: Edit .env and add your
    echo  OpenAI API key before running!
    echo ========================================
) else (
    echo [3/3] .env already exists - skipping
)

echo.
echo Setup complete! Run the server with:
echo   .venv\Scripts\activate
echo   python app.py
echo.
pause
