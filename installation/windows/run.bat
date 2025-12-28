@echo off
REM Run script for MOSIP IDA Authentication Testing Tool (Windows)

REM Get the script directory and project root
cd /d "%~dp0"
cd ..\..
set PROJECT_ROOT=%CD%

REM Activate virtual environment
if exist "%PROJECT_ROOT%\venv\Scripts\activate.bat" (
    call "%PROJECT_ROOT%\venv\Scripts\activate.bat"
) else (
    echo [ERROR] Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

REM Change to project root
cd /d "%PROJECT_ROOT%"

REM Run the application
python main.py

pause
