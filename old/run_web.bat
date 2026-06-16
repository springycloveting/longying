@echo off
title Dragon Save Editor - Web (venv)

echo ========================================
echo   LongYin Save Editor - Web Version
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

echo [INFO] Checking dependencies...
pip install flask -q 2>nul

if not exist "Hero" (
    echo [WARN] Hero save file not found
    echo.
)

echo [INFO] Starting web server...
echo [INFO] Opening browser: http://localhost:5000
echo.

start http://localhost:5000

python web_server.py

pause
