@echo off
echo ========================================
echo   成绩监控系统 v2.0 - 启动脚本
echo ========================================
echo.

echo [1/3] 检查Python依赖...
python -c "import requests, bs4, flask, flask_cors" 2>nul
if errorlevel 1 (
    echo 缺少Python依赖，正在安装...
    pip install requests beautifulsoup4 pycryptodome flask flask-cors
) else (
    echo ✓ Python依赖已就绪
)
echo.

echo [2/3] 检查前端依赖...
cd frontend
if not exist "node_modules" (
    echo 前端依赖未安装，正在安装...
    npm install
) else (
    echo ✓ 前端依赖已就绪
)
cd ..
echo.

echo [3/3] 启动服务...
echo ✓ 正在启动后端监控服务...
start "成绩监控后端" python monitor.py

timeout /t 3 >nul

echo ✓ 正在启动前端界面...
cd frontend
start "成绩监控前端" npm start

echo.
echo ========================================
echo   启动完成
echo ========================================
echo.
echo 后端API: http://localhost:5000
echo 前端界面: http://localhost:3000
echo.
echo 按任意键退出此窗口（不影响服务运行）...
pause >nul
