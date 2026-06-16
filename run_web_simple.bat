@echo off
chcp 65001 >nul
title 龙胤立志传存档修改器 - Web版

echo ========================================
echo   龙胤立志传存档修改器 - Web版
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] 正在安装依赖...
pip install flask -q

echo.
echo ========================================
echo   启动成功！
echo ========================================
echo.
echo   角色编辑器: http://localhost:5000
echo   世界编辑器: http://localhost:5000/world
echo.
echo   按 Ctrl+C 停止服务器
echo ========================================
echo.

start http://localhost:5000

python web_server.py

pause
