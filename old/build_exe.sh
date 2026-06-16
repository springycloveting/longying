#!/bin/bash
# 龙胤立志传存档修改器 - 打包脚本
# 使用 PyInstaller 打包为 Windows EXE

echo "======================================"
echo "龙胤立志传存档修改器 - 打包工具"
echo "======================================"

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

# 清理旧文件
echo "[2/4] 清理旧文件..."
rm -rf build dist *.spec 2>/dev/null

# 打包
echo "[3/4] 打包中..."
pyinstaller --noconfirm --onefile --windowed \
    --name "龙胤立志传存档修改器" \
    --add-data "skill_names.json:." \
    --add-data "spe_attr_map.json:." \
    --hidden-import PyQt6.sip \
    save_editor_gui.py

# 检查结果
echo "[4/4] 检查结果..."
if [ -f "dist/龙胤立志传存档修改器" ]; then
    echo ""
    echo "======================================"
    echo "打包成功!"
    echo "======================================"
    echo "输出文件: dist/龙胤立志传存档修改器"
    echo ""
    echo "使用方法:"
    echo "1. 将 'Hero' 存档文件复制到程序同目录"
    echo "2. 运行程序进行修改"
    echo "3. 保存后将 'Hero' 文件复制回游戏存档目录"
    echo ""
else
    echo ""
    echo "======================================"
    echo "打包失败，请检查错误信息"
    echo "======================================"
fi
