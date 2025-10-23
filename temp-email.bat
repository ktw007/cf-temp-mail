@echo off
REM Cloudflare Email Routing CLI - Windows Batch Wrapper

setlocal EnableDelayedExpansion

REM Script directory
set "SCRIPT_DIR=%~dp0"

REM Check .env file
if not exist "%SCRIPT_DIR%.env" (
    echo Error: .env file not found
    echo Please copy .env.example to .env and configure it:
    echo   copy .env.example .env
    exit /b 1
)

REM Load environment variables
for /f "usebackq tokens=1,* delims==" %%a in ("%SCRIPT_DIR%.env") do (
    set "line=%%a"
    REM Skip comments and empty lines
    if not "!line:~0,1!"=="#" if not "!line!"=="" (
        set "%%a=%%b"
    )
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python 3.6 or higher
    exit /b 1
)

REM Execute Python script
python "%SCRIPT_DIR%temp_email.py" %*
