@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ======================================
echo 龙胤立志传存档修改器 - 打包工具
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

REM 清理旧文件
echo 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec 2>nul

REM 打包
echo 打包中...
pyinstaller --noconfirm --onefile --windowed ^
    --name "SaveEditor" ^
    --add-data "skill_names.json;." ^
    --add-data "spe_attr_map.json;." ^
    --hidden-import PyQt6.sip ^
    save_editor_gui.py

REM 检查结果
if exist "dist\SaveEditor.exe" (
    echo.
    echo ======================================
    echo 打包成功!
    echo ======================================
    echo 输出文件: dist\SaveEditor.exe
    echo.
) else (
    echo.
    echo 打包失败，请检查错误信息
)

pause
