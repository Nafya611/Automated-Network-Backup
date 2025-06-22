@echo off
REM Network Device Backup Tool - Windows Startup Script
REM
REM This script provides easy access to the backup tool functions

setlocal enabledelayedexpansion

echo ==========================================
echo Network Device Backup Tool
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import netmiko, yaml, schedule" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

:menu
echo.
echo Choose an option:
echo [1] Run backup now
echo [2] Test device connections
echo [3] Start backup scheduler
echo [4] Show current configuration
echo [5] Run test suite
echo [6] Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Running backup...
    python main.py --backup
    echo.
    pause
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo Testing device connections...
    python main.py --test
    echo.
    pause
    goto menu
)

if "%choice%"=="3" (
    echo.
    echo Starting backup scheduler...
    echo Press Ctrl+C to stop the scheduler
    python main.py --schedule
    echo.
    pause
    goto menu
)

if "%choice%"=="4" (
    echo.
    echo Current configuration:
    python main.py --config
    echo.
    pause
    goto menu
)

if "%choice%"=="5" (
    echo.
    echo Running test suite...
    python test_tool.py
    echo.
    pause
    goto menu
)

if "%choice%"=="6" (
    echo Goodbye!
    exit /b 0
)

echo Invalid choice. Please try again.
goto menu
