@echo off
REM Installation script for MOSIP Auth GUI (Windows)

echo ==========================================
echo MOSIP IDA Authentication Testing Tool - Installer
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
echo Creating desktop shortcut...
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
set "APP_NAME=MOSIP IDA Authentication Testing Tool"
set "SHORTCUT_PATH=%DESKTOP_DIR%\%APP_NAME%.lnk"
set "TARGET_PATH=%PROJECT_ROOT%\installation\windows\run.bat"
set "ICON_PATH=%PROJECT_ROOT%\logo.png"
set "VBS_FILE=%TEMP%\create_shortcut.vbs"

(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%SHORTCUT_PATH%"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%TARGET_PATH%"
echo oLink.WorkingDirectory = "%PROJECT_ROOT%"
echo oLink.IconLocation = "%ICON_PATH%"
echo oLink.Description = "MOSIP IDA Authentication Testing Tool"
echo oLink.Save
) > "%VBS_FILE%"

cscript //nologo "%VBS_FILE%" >nul 2>&1
del "%VBS_FILE%"

if exist "%SHORTCUT_PATH%" (
    echo Desktop shortcut created at: %SHORTCUT_PATH%
    echo You can now launch the application from your Desktop.
) else (
    echo Warning: Could not create desktop shortcut
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
echo Or double-click the desktop shortcut: %SHORTCUT_PATH%
echo.
pause
