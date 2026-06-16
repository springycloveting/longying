@echo off
title Build Web Editor

echo ========================================
echo   Build Web Save Editor to EXE
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] venv not found, please run run_web.bat first
    pause
    exit /b 1
)

echo [INFO] Installing PyInstaller...
pip install pyinstaller -q

echo [INFO] Building...
echo.

pyinstaller --noconfirm --onefile --windowed ^
    --name "LongYinWebEditor" ^
    --add-data "web;web" ^
    --add-data "skill_names.json;." ^
    --add-data "spe_attr_map.json;." ^
    --add-data "talent_names.json;." ^
    --add-data "tag_names.json;." ^
    web_server.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build Complete!
echo   Output: dist\LongYinWebEditor.exe
echo ========================================
echo.

pause
