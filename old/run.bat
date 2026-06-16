@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ======================================
echo 龙胤立志传存档修改器
echo ======================================

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo 首次运行，正在设置环境...
    python -m venv venv
    if errorlevel 1 (
        echo 创建虚拟环境失败
        pause
        exit /b 1
    )
    call venv\Scripts\activate
    pip install PyQt6 pyinstaller -q
) else (
    call venv\Scripts\activate
)

REM 运行 GUI
python save_editor_gui.py
