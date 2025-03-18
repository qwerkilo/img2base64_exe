@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo 正在检查环境...

:: 检查Python是否安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python未安装，请先安装Python（建议Python 3.6或更高版本）
    echo 您可以从 https://www.python.org/downloads/ 下载安装
    pause
    exit /b 1
)

:: 检查虚拟环境是否存在
if not exist venv\ (
    echo 正在创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 创建虚拟环境失败，请检查Python安装是否正确
        pause
        exit /b 1
    )
    
    echo 正在激活虚拟环境...
    call venv\Scripts\activate.bat
    if %errorlevel% neq 0 (
        echo 激活虚拟环境失败
        pause
        exit /b 1
    )
    
    echo 正在安装依赖...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 安装依赖失败，请检查网络连接或手动安装以下包：
        type requirements.txt
        pause
        exit /b 1
    )
) else (
    echo 正在激活虚拟环境...
    call venv\Scripts\activate.bat
    if %errorlevel% neq 0 (
        echo 激活虚拟环境失败，尝试重新创建虚拟环境
        rmdir /s /q venv
        python -m venv venv
        call venv\Scripts\activate.bat
        if %errorlevel% neq 0 (
            echo 重新创建虚拟环境失败
            pause
            exit /b 1
        )
        echo 正在重新安装依赖...
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
    )
)

:: 启动程序
echo 正在启动程序...
python main.py

:: 检查程序退出状态
if %errorlevel% neq 0 (
    echo 程序运行出错，错误代码：%errorlevel%
    echo 请查看上方错误信息
    pause
) else (
    echo 程序正常结束
    pause
)

:: 退出虚拟环境
deactivate