@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ======================================
echo 龙胤立志传存档修改器
echo ======================================
echo.

REM 直接运行，使用系统 Python
python save_editor_v2.py

if errorlevel 1 (
    echo.
    echo 如果提示缺少 PyQt6，请运行以下命令安装:
    echo     pip install PyQt6
    echo.
    pause
)
