@echo off
chcp 65001 >nul
echo ========================================
echo 智能安检系统 - 快速启动
echo ========================================
echo.

echo [1/3] 检查后端服务...
netstat -ano | findstr :8888 >nul
if %errorlevel% equ 0 (
    echo ✅ 后端服务已运行
) else (
    echo ⚠️ 后端服务未运行，正在启动...
    start "智能安检系统-后端" cmd /k "cd backend && python main.py"
    timeout /t 3 >nul
)

echo.
echo [2/3] 检查前端服务...
netstat -ano | findstr :5173 >nul
if %errorlevel% equ 0 (
    echo ✅ 前端服务已运行
) else (
    echo ⚠️ 前端服务未运行，正在启动...
    start "智能安检系统-前端" cmd /k "npm run dev"
    timeout /t 5 >nul
)

echo.
echo [3/3] 打开浏览器...
timeout /t 2 >nul
start http://localhost:5173

echo.
echo ========================================
echo ✅ 系统启动完成！
echo ========================================
echo.
echo 📌 访问地址: http://localhost:5173
echo 📌 API 文档: http://localhost:8888/docs
echo.
echo 💡 提示:
echo    - 当前使用模拟数据模式
echo    - 要使用真实AI识别，请更新API Key
echo    - 详见: API_KEY问题解决方案.md
echo.
echo 按任意键关闭此窗口...
pause >nul
