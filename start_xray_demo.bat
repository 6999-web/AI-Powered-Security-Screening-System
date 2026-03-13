@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo X 光安检机模拟 Demo - 启动脚本
echo ============================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未检测到 Python
    echo 请从 https://www.python.org/downloads/ 下载并安装 Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python 已安装

REM 进入后端目录
cd backend

REM 检查虚拟环境
if not exist venv (
    echo.
    echo 📦 创建虚拟环境...
    python -m venv venv
    echo ✅ 虚拟环境已创建
)

REM 激活虚拟环境
echo.
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo.
echo 📥 安装依赖...
pip install -r requirements_xray_demo.txt >nul 2>&1
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖已安装

REM 启动后端服务
echo.
echo 🚀 启动后端服务...
echo.
python main_xray_demo.py

pause
