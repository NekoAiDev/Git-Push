@echo off
chcp 65001 >nul
echo 正在刷新 Windows 图标缓存，请稍候...
echo.
taskkill /f /im explorer.exe >nul 2>&1
cd /d %localappdata%
del /f /s /q IconCache.db >nul 2>&1
timeout /t 1 /nobreak >nul
start explorer.exe
echo 图标缓存已刷新，请重新打开 dist 文件夹查看 GitPush.exe 的新图标喵~
pause
