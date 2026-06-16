#!/bin/bash
# 龙胤立志传存档修改器 - 启动脚本

cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "首次运行，正在设置环境..."
    python3 -m venv venv
    source venv/bin/activate
    pip install PyQt6 pyinstaller -q
else
    source venv/bin/activate
fi

# 运行 GUI
python save_editor_gui.py
