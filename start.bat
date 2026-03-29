@echo off
:: Set code page to UTF-8
chcp 65001 > nul

title Video Delivery Agent - Startup

echo =======================================================
echo          Video Delivery Agent Launcher
echo =======================================================
echo.
echo [1/1] Starting Flask backend...
echo The browser will open automatically in a few seconds.
echo.
echo NOTE: DO NOT close this window while using the platform.
echo =======================================================
echo.

:: Check if python is available
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found in your PATH. Please install Python.
    pause
    exit /b
)

:: Run the app
python app.py

pause
