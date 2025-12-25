@echo off
REM Installation script for MOSIP Auth GUI (Windows)

echo ==========================================
echo MOSIP Authentication GUI - Installer
echo ==========================================
echo.

REM Get the script directory and project root
cd /d "%~dp0"
cd ..\..
set PROJECT_ROOT=%CD%

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed. Please install Python 3.10+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Create virtual environment in project root
echo.
echo Creating virtual environment...
cd /d "%PROJECT_ROOT%"
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo Installing dependencies...
pip install -r "%PROJECT_ROOT%\requirements.txt" --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Check if tkinter is available
echo Checking for tkinter support...
python -c "import tkinter" 2>nul
if errorlevel 1 (
    echo [WARNING] tkinter is not available. It should be included with Python.
    echo If you see errors, try reinstalling Python with "tcl/tk" option.
) else (
    echo [OK] tkinter is available
)

echo.
echo ==========================================
echo Installation complete!
echo ==========================================
echo.
echo To run the application:
echo   run.bat
echo.
echo Or manually:
echo   cd %PROJECT_ROOT%
echo   venv\Scripts\activate
echo   python main.py
echo.
pause
