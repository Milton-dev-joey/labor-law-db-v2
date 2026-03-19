@echo off
chcp 65001 >nul
echo 劳动法数据库 v2 - Windows启动器
echo ================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 进入项目目录
cd /d "%~dp0"

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [首次启动] 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查依赖
pip list | findstr "PyQt6" >nul
if errorlevel 1 (
    echo [首次启动] 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 安装依赖失败
        pause
        exit /b 1
    )
)

REM 启动应用
echo [启动] 劳动法数据库 v2...
python main.py

REM 如果出错，暂停显示错误
if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出
    pause
)

REM 退出虚拟环境
deactivate
