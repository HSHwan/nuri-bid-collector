@echo off
setlocal

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.9+ first.
    pause
    exit /b 1
)

if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

if exist "requirements.txt" (
    echo [INFO] Installing requirements...
    pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt not found. Skipping dependency installation.
)

echo [INFO] Installing Playwright browsers...
playwright install chromium

echo [INFO] Starting Nuri Bid Collector...
set PYTHONPATH=%cd%
python src/main.py

pause