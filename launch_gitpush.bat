@echo off
setlocal enabledelayedexpansion
REM 甘城猫猫的 Git Push 小工具 - 启动脚本
REM 优先用 Python Launcher(py)，其次 python，再次 pythonw；用控制台窗口运行以便看到报错
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY ( where python >nul 2>nul && set "PY=python" )
if not defined PY ( where pythonw >nul 2>nul && set "PY=pythonw" )
if not defined PY (
    echo 主机的 Python 没找到喵~ 请先安装 https://python.org 并勾选 "Add python.exe to PATH"
    pause
    exit /b 1
)
echo 正在启动甘城猫猫的 Git Push 工具...
%PY% "%~dp0git_push_tool.py"
echo.
echo （如果上面出现红色报错文字，请把这些文字发给猫猫喵~）
pause
