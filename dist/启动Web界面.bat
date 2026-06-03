@echo off
chcp 65001 >nul
echo ========================================================
echo        学霸帝 Text-to-CAD v2.0 Web界面启动器
echo ========================================================
echo.
echo [INFO] 启动Web服务器...
start "" "%~dp0学霸帝TextToCAD_Web.exe"
echo [INFO] 等待服务器启动（约10-20秒）...
timeout /t 5 /nobreak >nul
echo [INFO] 正在打开浏览器...
start http://localhost:8080
echo.
echo [OK] 如果浏览器未自动打开，请手动访问: http://localhost:8080
echo.
pause