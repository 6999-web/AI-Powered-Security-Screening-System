#!/bin/bash

echo ""
echo "============================================================"
echo "X 光安检机模拟 Demo - 启动脚本"
echo "============================================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未检测到 Python"
    echo "请使用以下命令安装 Python："
    echo "  macOS: brew install python3"
    echo "  Ubuntu: sudo apt-get install python3 python3-pip"
    exit 1
fi

echo "✅ Python 已安装"

# 进入后端目录
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境已创建"
fi

# 激活虚拟环境
echo ""
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "📥 安装依赖..."
pip install -r requirements_xray_demo.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi
echo "✅ 依赖已安装"

# 启动后端服务
echo ""
echo "🚀 启动后端服务..."
echo ""
python main_xray_demo.py
