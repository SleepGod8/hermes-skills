@echo off
chcp 65001 >nul
title SillyTavern (端口 8001)
cd /d E:\SillyTavern
echo ============================================
echo   SillyTavern 启动中...
echo   浏览器访问: http://127.0.0.1:8001
echo   关闭此窗口 = 停止酒馆
echo ============================================
echo.
node server.js
pause
