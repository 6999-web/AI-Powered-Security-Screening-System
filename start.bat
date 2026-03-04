@echo off
chcp 65001 >nul
title 智能安检系统启动器

echo ========================================
echo    智能安检系统 - 一键启动
echo ========================================
echo.

echo [1/2] 正在启动后端服务...
echo 端口: 8888
echo.
start "后端服务" cmd /k "cd backend && python main.py"

timeout /t 3 /nobreak >nul

echo [2/2] 正在启动前端服务...
echo 端口: 5173
echo.
start "前端服务" cmd /k "npm run dev"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo    ✅ 系统启动完成！
echo ========================================
echo.
echo 📱 前端界面: http://localhost:5173
echo 🔧 后端 API: http://localhost:8888
echo 📖 API 文档: http://localhost:8888/docs
echo.
echo 提示：
echo - 两个命令行窗口会自动打开
echo - 关闭窗口即可停止服务
echo - 按任意键退出此窗口
echo.
pause
