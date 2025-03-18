@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: 激活虚拟环境
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 激活虚拟环境失败
    pause
    exit /b 1
)

:: 启动程序
echo 正在启动程序...
python main.py

:: 如果程序异常退出
if %errorlevel% neq 0 (
    echo 程序运行出错
    pause
)

deactivate