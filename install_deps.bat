@echo off
echo ========================================
echo   安装所有依赖
echo ========================================
echo.

echo [1/2] 安装Python依赖...
pip install requests beautifulsoup4 pycryptodome flask flask-cors
echo.

echo [2/2] 安装前端依赖...
cd frontend
npm install
cd ..
echo.

echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 现在可以运行 start.bat 启动系统
echo.
pause
